#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pdf_image_qa.py — (DRM PDF용) 페이지 '이미지' 폴더를 받아 표 가로 짤림 / 세로 짤림 / 렌더 이상 검사 → CSV.

권장 파일명:  <문서명>_p<페이지>.png  (예: 보고서A_p003.png)  또는  <문서명>/003.png
필요:  pip install pillow numpy
사용:  python pdf_image_qa.py "<페이지 이미지 폴더>"
출력:  pdf_qa_detail.csv / pdf_qa_summary.csv
"""
import sys, os, glob, csv, re

try:
    import numpy as np
    from PIL import Image
except ImportError as e:
    sys.exit(f"의존성 필요:  pip install pillow numpy   ({e})")

INK         = 200      # 이보다 어두우면 '잉크'로 간주 (0=검정, 255=흰색)
BAND_FRAC   = 0.006    # 페이지 가장자리 밴드 두께 비율(작은 변 기준)
CLIP_RUN    = 0.08     # 가장자리에 내용이 변 길이의 8% 이상 '연속'으로 닿으면 짤림 의심
FRAME_RUN   = 0.85     # 마주보는 두 변 모두 이만큼 길면 테두리로 보고 제외
BLACK_RATIO = 0.70     # 이 이상이 잉크면 '새까만' 렌더 이상
BLANK_RATIO = 0.001    # 이 이하면 사실상 빈 페이지
EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff")


def longest_true_run(mask):
    """1D bool 배열에서 True가 연속으로 가장 길게 이어진 길이."""
    if not mask.any():
        return 0
    padded = np.concatenate(([False], mask, [False]))
    diff = np.diff(padded.astype(np.int8))
    return int((np.flatnonzero(diff == -1) - np.flatnonzero(diff == 1)).max())


def analyze(arr):
    """한 페이지 이미지(2D 흑백)를 분석해 (문제유형, 상세) 리스트 반환. 정상이면 []."""
    out = []
    ink = arr < INK
    H, W = ink.shape
    ratio = ink.mean()

    if ratio > BLACK_RATIO:
        return [("렌더이상", f"페이지의 {ratio*100:.0f}%가 검게 나옴(렌더 이상)")]
    if ratio < BLANK_RATIO:
        return [("렌더이상", "잉크가 거의 없음(빈 페이지/렌더 실패 의심)")]

    band = max(4, round(min(H, W) * BAND_FRAC))
    r = longest_true_run(ink[:, W - band:].any(axis=1)) / H   # 우측 밴드
    l = longest_true_run(ink[:, :band].any(axis=1)) / H       # 좌측 밴드
    b = longest_true_run(ink[H - band:, :].any(axis=0)) / W   # 하단 밴드
    t = longest_true_run(ink[:band, :].any(axis=0)) / W       # 상단 밴드
    frame_lr = l > FRAME_RUN and r > FRAME_RUN                # 좌·우 모두 김 → 세로 테두리
    frame_tb = t > FRAME_RUN and b > FRAME_RUN                # 상·하 모두 김 → 가로 테두리

    if r > CLIP_RUN and not frame_lr:
        out.append(("표짤림(가로)", f"오른쪽 끝에 내용이 세로 {r*100:.0f}% 닿음 — 우측 열 잘림 의심"))
    if b > CLIP_RUN and not frame_tb:
        out.append(("표짤림(세로)", f"아래 끝에 내용이 가로 {b*100:.0f}% 닿음 — 하단 행 잘림 의심"))
    return out


def parse_doc_page(path, root):
    """이미지 경로에서 (문서명, 페이지번호)를 추출."""
    rel = os.path.relpath(path, root)
    parts = rel.split(os.sep)
    stem = os.path.splitext(parts[-1])[0]

    m = re.search(r'(?:^|[ _\-])p?(\d+)$', stem)       # 끝의 _p003 / -3 / _012
    if not m:
        m = re.search(r'(\d+)(?!.*\d)', stem)          # 없으면 마지막 숫자 덩어리
    page = int(m.group(1)) if m else 0

    if len(parts) > 1:
        doc = parts[0]                                  # 하위폴더명 = 문서명
    else:
        doc = re.sub(r'[ _\-]p?\d+$', '', stem) or stem # 파일명에서 끝 페이지 토큰 제거
    return doc, page


def main():
    if len(sys.argv) < 2:
        sys.exit('사용법: python pdf_image_qa.py "<페이지 이미지 폴더>"')
    root = sys.argv[1]
    if not os.path.isdir(root):
        sys.exit(f"폴더가 아닙니다: {root}")

    imgs = [p for p in glob.glob(os.path.join(root, "**", "*"), recursive=True)
            if p.lower().endswith(EXTS)]
    if not imgs:
        sys.exit("이미지를 찾지 못했습니다.")

    docs = {}
    for p in imgs:
        doc, page = parse_doc_page(p, root)
        docs.setdefault(doc, []).append((page, p))

    detail, summary = [], []
    for doc in sorted(docs):
        pages = sorted(docs[doc])
        fails = []
        for (pno, path) in pages:
            try:
                arr = np.asarray(Image.open(path).convert("L"))
            except Exception as e:
                fails.append((pno, "렌더이상", f"이미지 열기 실패: {e}", path))
                continue
            for (itype, det) in analyze(arr):
                fails.append((pno, itype, det, path))

        if not fails:
            detail.append((doc, "-", "-", "이상 없음", "PASS"))
            summary.append((doc, len(pages), "PASS", "", ""))
        else:
            for (pno, itype, det, path) in fails:
                detail.append((doc, pno, itype, f"{det}  [{os.path.basename(path)}]", "FAIL"))
            pnos = sorted({f[0] for f in fails})
            types = sorted({f[1] for f in fails})
            summary.append((doc, len(pages), "FAIL",
                            ", ".join(str(p) for p in pnos), ", ".join(types)))
        s = summary[-1]
        print(f"  {doc}: {s[2]}" + (f"  (페이지 {s[3]})" if s[2] == 'FAIL' else ""), flush=True)

    with open("pdf_qa_detail.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["문서명", "페이지", "문제유형", "상세", "판정"])
        w.writerows(detail)
    with open("pdf_qa_summary.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["문서명", "총페이지수", "판정", "문제페이지", "문제유형"])
        w.writerows(summary)

    total = len(docs); failed = sum(1 for s in summary if s[2] == "FAIL")
    print(f"\n검사 완료: 문서 {total}개 · PASS {total - failed} · FAIL {failed}")
    print("→ pdf_qa_detail.csv / pdf_qa_summary.csv")


if __name__ == "__main__":
    main()
