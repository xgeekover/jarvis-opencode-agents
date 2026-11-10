#!/usr/bin/env python3
"""Validate the Jarvis OpenCode package (stdlib only; Windows, macOS, Linux).

    python tools/validate.py              # static checks
    python tools/validate.py --opencode   # + install into a temp project and let OpenCode load it

Exit code 0 = all checks passed, 1 = at least one problem (each is printed).
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OC = ROOT / ".opencode"
FACTORY_AGENTS = {"jarvis-queen": "primary", "jarvis-planner": "subagent", "jarvis-developer": "subagent",
                  "jarvis-tester": "subagent", "jarvis-reviewer": "subagent", "jarvis-integrator": "subagent"}
COMMANDS = {"jarvis-analyze", "jarvis-feature", "jarvis-review", "jarvis-gate", "jarvis-status"}
SKILLS = {"jarvis-factory", "jarvis-project-analysis", "jarvis-feature-development", "jarvis-code-review", "jarvis-quality-gate",
          "code-reviewer", "codex-grade-coding", "design-pattern-advisor", "env-doctor", "prompt-engineer",
          "react-typescript-reviewer", "security-reviewer", "skill-creator", "spring-boot-reviewer",
          "systematic-debugging", "tdd", "queen-orchestration", "pdf-table-clip-check"}
V2_ONLY_KEYS = {"permissions", "system", "disabled", "request"}  # V1 (1.x) silently ignores these
SKILL_ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
PRIVATE = [  # personal or secret material that must never ship
    (re.compile(r"/Users/[A-Za-z0-9._-]+|/Volumes/[A-Za-z0-9._-]+|[A-Za-z]:\\Users\\[A-Za-z0-9._-]+"), "absolute home/volume path"),
    (re.compile(r"[A-Za-z0-9._%+-]+@(gmail|naver|daum|hanmail|outlook|hotmail)\.[a-z]+", re.I), "personal e-mail address"),
    (re.compile(r"claude\.ai/code/session_|session_01[A-Za-z0-9]{10,}"), "Claude session link"),
    (re.compile(r"\b(sk-[A-Za-z0-9_-]{20,}|sk-ant-[A-Za-z0-9_-]{10,}|ghp_[A-Za-z0-9]{30,}|gho_[A-Za-z0-9]{30,}|nvapi-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{30,}|AKIA[0-9A-Z]{16})\b"), "credential-like token"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
]
problems: list[str] = []
TEMPLATE_GUARDS: list[str] = []


def bad(msg: str) -> None:
    problems.append(msg)
    print(f"  FAIL {msg}")


def frontmatter(path: Path) -> tuple[dict, list[str], str]:
    """Top-level keys -> raw value (str) or nested lines; minimal YAML reader for the shapes used here."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, [], text
    end = text.find("\n---", 4)
    if end < 0:
        return {}, [], text
    lines = text[4:end].splitlines()
    keys: dict = {}
    current = None
    for ln in lines:
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        if not ln.startswith((" ", "\t")):
            m = re.match(r"^([A-Za-z0-9_-]+):(?:\s+(.*))?$", ln)
            if not m:
                bad(f"{rel(path)}: unparsable frontmatter line {ln!r}")
                continue
            current = m.group(1)
            keys[current] = (m.group(2) or "").strip()
            if keys[current]:
                v = keys[current]
                if not (v.startswith(('"', "'")) or v in ("true", "false") or re.fullmatch(r"-?[0-9.]+", v)) and re.search(r":\s", v):
                    bad(f"{rel(path)}: value of '{current}' contains ': ' and must be quoted")
        elif current is not None:
            keys.setdefault(f"{current}.__children", []).append(ln)
    return keys, lines, text[end + 4:]


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def check_static() -> None:
    print("static checks")
    global TEMPLATE_GUARDS
    tb = json.loads((ROOT / "templates" / "opencode.json").read_text(encoding="utf-8"))["permission"]["bash"]
    TEMPLATE_GUARDS = [k for k, v in tb.items() if v in ("ask", "deny") and k != "*.env*"]
    # agents
    agents = {p.stem: p for p in (OC / "agents").glob("*.md")}
    if set(agents) != set(FACTORY_AGENTS):
        bad(f"agents: expected {sorted(FACTORY_AGENTS)}, found {sorted(agents)}")
    for name, p in agents.items():
        fm, _, body = frontmatter(p)
        for k in V2_ONLY_KEYS & set(fm):
            bad(f"{rel(p)}: V2-only key '{k}' (OpenCode 1.x ignores it, so rules written there are silently lost; OpenCode 2 then ignores the file's V1 fields)")
        if not fm.get("description"):
            bad(f"{rel(p)}: missing description")
        if fm.get("mode") != FACTORY_AGENTS.get(name):
            bad(f"{rel(p)}: mode is {fm.get('mode')!r}, expected {FACTORY_AGENTS.get(name)!r}")
        if len(body.strip()) < 200:
            bad(f"{rel(p)}: prompt body is suspiciously short")
        perm = "\n".join(fm.get("permission.__children", []))
        if not perm:
            bad(f"{rel(p)}: no permission block")
        bash = dict(re.findall(r'^\s+"([^"]+)": (allow|ask|deny)$', perm.split("bash:", 1)[1].split("webfetch:")[0], re.M)) if "bash:" in perm else {}
        if bash.get("*") == "allow":
            guarded = [q for q, a in bash.items() if a in ("ask", "deny")]
            missing = [t for t in TEMPLATE_GUARDS if not any(fnmatch.fnmatchcase(t, q) for q in guarded)]
            if missing:
                bad(f"{rel(p)}: bash allows '*' but does not ask/deny what templates/opencode.json guards: {missing}")
        if name in ("jarvis-planner", "jarvis-tester", "jarvis-reviewer", "jarvis-integrator") and "edit: deny" not in perm:
            bad(f"{rel(p)}: read-only role without 'edit: deny'")
        if '"*.env": deny' not in perm:
            bad(f"{rel(p)}: read permission does not deny *.env")
    # commands
    cmds = {p.stem: p for p in (OC / "commands").glob("*.md")}
    if set(cmds) != COMMANDS:
        bad(f"commands: expected {sorted(COMMANDS)}, found {sorted(cmds)}")
    for name, p in cmds.items():
        fm, _, body = frontmatter(p)
        if not fm.get("description"):
            bad(f"{rel(p)}: missing description")
        if fm.get("agent") != "jarvis-queen":
            bad(f"{rel(p)}: agent should be jarvis-queen")
        if "$ARGUMENTS" not in body:
            bad(f"{rel(p)}: body does not use $ARGUMENTS")
    # skills
    skills = {p.parent.name: p for p in (OC / "skills").glob("*/SKILL.md")}
    if set(skills) != SKILLS:
        bad(f"skills: missing {sorted(SKILLS - set(skills))}, unexpected {sorted(set(skills) - SKILLS)}")
    for name, p in skills.items():
        fm, _, body = frontmatter(p)
        if not SKILL_ID.match(name):
            bad(f"{rel(p)}: skill id '{name}' is not lowercase kebab-case")
        if fm.get("name") != name:
            bad(f"{rel(p)}: name {fm.get('name')!r} does not match its folder")
        d = fm.get("description", "")
        if not d or len(d) > 1024:
            bad(f"{rel(p)}: description missing or longer than 1024 characters ({len(d)})")
        if len(body.strip()) < 100:
            bad(f"{rel(p)}: body is suspiciously short")
    # JSON
    for p in list(ROOT.rglob("*.json")):
        if ".git" in p.parts:
            continue
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except ValueError as e:
            bad(f"{rel(p)}: invalid JSON ({e})")
    # installers
    ps1 = ROOT / "install" / "install.ps1"
    try:
        ps1.read_bytes().decode("ascii")
    except UnicodeDecodeError:
        bad("install/install.ps1 must be ASCII only (Windows PowerShell 5.1 reads BOM-less scripts in the ANSI code page)")
    # README
    readme = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").exists() else ""
    if not re.search(r"[가-힣]{20,}", readme.replace(" ", "")) or "## English" not in readme or "## 한국어" not in readme:
        bad("README.md must contain both a '## 한국어' and a '## English' section")
    # private material
    for p in ROOT.rglob("*"):
        if not p.is_file() or ".git" in p.parts or p.suffix in (".png", ".zip") or p.resolve() == Path(__file__).resolve():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for rx, what in PRIVATE:
            m = rx.search(text)
            if m:
                bad(f"{rel(p)}: {what}: {m.group(0)[:40]!r}")


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """Capture stdout through a file, not a pipe: OpenCode 1.18 truncates large output written to a pipe at 64 KiB."""
    with tempfile.TemporaryFile(mode="w+b") as out, tempfile.TemporaryFile(mode="w+b") as err:
        r = subprocess.run(cmd, cwd=cwd, stdout=out, stderr=err, timeout=300)
        out.seek(0)
        err.seek(0)
        return subprocess.CompletedProcess(cmd, r.returncode, out.read().decode("utf-8", "replace"), err.read().decode("utf-8", "replace"))


def check_opencode() -> None:
    print("opencode load check")
    exe = shutil.which("opencode")
    if not exe:
        bad("opencode is not on PATH (install it, or run without --opencode)")
        return
    ver = run([exe, "--version"], ROOT).stdout.strip()
    print(f"  opencode {ver}")
    with tempfile.TemporaryDirectory(prefix="jarvis-oc-", ignore_cleanup_errors=True) as tmp:
        proj = Path(tmp) / "demo"
        proj.mkdir()
        run(["git", "init", "-q"], proj)
        if os.name == "nt":
            shell = shutil.which("pwsh") or shutil.which("powershell")
            r = run([shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ROOT / "install" / "install.ps1"),
                     "-Target", str(proj), "-WithTemplates"], ROOT)
        else:
            r = run(["bash", str(ROOT / "install" / "install.sh"), "--target", str(proj), "--with-templates"], ROOT)
        if r.returncode != 0:
            bad(f"installer exited {r.returncode}: {r.stdout[-400:]} {r.stderr[-400:]}")
            return
        r = run([exe, "agent", "list"], proj)
        listed = dict(re.findall(r"^([a-z][a-z0-9/_-]*) \((primary|subagent|all)\)", r.stdout, re.M))
        for name, mode in FACTORY_AGENTS.items():
            if listed.get(name) != mode:
                bad(f"opencode agent list: {name} expected ({mode}), got {listed.get(name)!r}")
        for name in ("jarvis-reviewer", "jarvis-queen"):
            r = run([exe, "debug", "agent", name], proj)
            try:
                d = json.loads(r.stdout[r.stdout.find("{"):])
            except ValueError:
                bad(f"opencode debug agent {name}: unreadable output: {r.stdout[:200]!r} {r.stderr[:200]!r}")
                continue
            rules = d.get("permission") or d.get("permissions") or []
            text = json.dumps(rules)
            if name == "jarvis-reviewer" and not re.search(r'"edit".{0,40}"deny"|"deny".{0,40}"edit"', text):
                bad("jarvis-reviewer: OpenCode did not load the 'edit: deny' rule")
            if name == "jarvis-queen" and "jarvis-*" not in text:
                bad("jarvis-queen: OpenCode did not load the task (subagent) allow-list")
        r = run([exe, "debug", "skill"], proj)
        try:
            found = {s.get("name") for s in json.loads(r.stdout[r.stdout.find("["):])}
        except ValueError:
            found = set(re.findall(r'"name":\s*"([^"]+)"', r.stdout))
        missing = sorted(SKILLS - found)
        if missing:
            bad(f"opencode debug skill: not discovered: {missing}")
        r = run([exe, "debug", "config"], proj)
        for c in COMMANDS:
            if f'"{c}"' not in r.stdout:
                bad(f"opencode debug config: command {c} not loaded")
        print(f"  agents ok: {sorted(k for k in listed if k.startswith('jarvis-'))}")
        print(f"  skills discovered: {len(SKILLS & found)}/{len(SKILLS)}")


def main() -> int:
    check_static()
    if "--opencode" in sys.argv[1:]:
        check_opencode()
    print("RESULT:", "OK" if not problems else f"{len(problems)} problem(s)")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
