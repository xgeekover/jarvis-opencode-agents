# Jarvis OpenCode Agents

[![validate](https://github.com/xgeekover/jarvis-opencode-agents/actions/workflows/validate.yml/badge.svg)](https://github.com/xgeekover/jarvis-opencode-agents/actions/workflows/validate.yml)

**Jarvis Dev Factory for [OpenCode](https://opencode.ai)**: a Queen orchestrator, five role subagents (planner · developer · tester · reviewer · integrator), workflow skills and commands, plus 13 general development skills. Made for Windows PCs; it works the same way on macOS, Linux and WSL.

[한국어](#한국어) · [English](#english)

---

## 한국어

### 무엇인가요?

개발 요청 하나를 **검증 가능한 단계**로 진행하는 멀티 에이전트 구성입니다. 단계는 요구사항 → 계획 → 격리 워크트리 → 개발 → 테스트 → 독립 리뷰 → 통합 → 품질 게이트입니다.

- **Queen (`jarvis-queen`, primary)** 은 일을 쪼개 서브에이전트에게 맡기고, 결과를 diff와 실제 명령 결과로 검증합니다.
  - 품질 게이트(build/test/lint, 리뷰, diff 검사)는 Queen이 직접 실행합니다.
  - 커밋·push·병합·삭제는 하지 않습니다. 절차를 준비하고, 실행은 사람이 합니다.
- **역할 서브에이전트 5개**는 각자 권한이 다릅니다. 예를 들어 reviewer는 파일을 고칠 수 없고, developer는 태스크 워크트리 안에서만 편집합니다.
- 진행 상태는 프로젝트의 **`.jarvis/`** 폴더에 파일로 남습니다. 대화가 끊겨도 `/jarvis-status`로 이어서 할 수 있습니다.
- 그 밖에 **범용 개발 스킬 13종**이 들어 있습니다. 코드 리뷰, TDD, 디버깅, 보안 리뷰 등입니다.

### 구성

| 경로 | 내용 |
|---|---|
| `.opencode/agents/jarvis-queen.md` | 오케스트레이터 (primary, Tab으로 선택) |
| `.opencode/agents/jarvis-{planner,developer,tester,reviewer,integrator}.md` | 역할 서브에이전트 |
| `.opencode/commands/jarvis-*.md` | `/jarvis-analyze`, `/jarvis-feature`, `/jarvis-review`, `/jarvis-gate`, `/jarvis-status` |
| `.opencode/skills/jarvis-*/` | 워크플로 스킬 5종 (상태 파일 형식·JSON 스키마·위임 템플릿 포함) |
| `.opencode/skills/<범용 13종>/` | code-reviewer, codex-grade-coding, design-pattern-advisor, env-doctor, prompt-engineer, react-typescript-reviewer, security-reviewer, skill-creator, spring-boot-reviewer, systematic-debugging, tdd, queen-orchestration, pdf-table-clip-check |
| `templates/opencode.json` | 권한 규칙 템플릿 (위험 명령 승인, `.env` 읽기 금지) |
| `templates/AGENTS.md` | 프로젝트 규칙 템플릿 |
| `install/install.ps1`, `install/install.sh` | 설치·제거 스크립트 (Windows / macOS·Linux·WSL) |
| `tools/validate.py` | 패키지 검증 (CI에서도 사용) |

### 요구 사항

- **OpenCode 1.18 이상.** CI가 Windows와 Linux에서 OpenCode 1.18.34와 1.19.5로 설치·로딩을 검사합니다(결과는 맨 위 배지). V2 호환은 [아래 설명](#opencode-v1--v2-호환)을 보세요.
- **Git for Windows.** 워크트리와 diff에 필요합니다. 병합 검사(`git merge-tree --write-tree`)는 git 2.38 이상이 필요합니다.
- **Windows PowerShell 5.1 또는 PowerShell 7.** 설치 스크립트용입니다.
- (선택) **Python 3.** `pdf-table-clip-check` 스킬과 `tools/validate.py`에 필요합니다.
- 사용할 **모델이 OpenCode에 설정**돼 있어야 합니다. 사내 LLM도 됩니다(`opencode providers`).

> OpenCode 공식 문서는 Windows에서 **WSL 사용을 권장**합니다. 네이티브 Windows에서도 동작하며, 이 패키지의 명령은 Git Bash와 PowerShell 양쪽에서 돌도록 작성했습니다.

### 설치

#### 1) 내려받기

- **Release에서 zip을 받는 방법:** [Releases](https://github.com/xgeekover/jarvis-opencode-agents/releases)에서 `jarvis-opencode-agents-v1.0.0.zip`을 받아 원하는 폴더에 압축을 풉니다.
- **git으로 받는 방법:**
  ```powershell
  git clone https://github.com/xgeekover/jarvis-opencode-agents.git
  cd jarvis-opencode-agents
  ```

인터넷에서 받은 zip은 PowerShell이 스크립트 실행을 막을 수 있습니다. 그럴 때는 압축 푼 폴더에서 아래 명령을 한 번 실행하세요.

```powershell
Get-ChildItem -Recurse | Unblock-File
```

#### 2) 프로젝트에 설치 (권장)

대상 프로젝트의 `.opencode\` 아래에 에이전트·명령·스킬을 복사합니다. 템플릿까지 함께 넣으려면 `-WithTemplates`를 붙입니다.

```powershell
powershell -ExecutionPolicy Bypass -File .\install\install.ps1 -Target C:\work\my-app -WithTemplates
```

- 이미 있는 파일은 **덮어쓰지 않고 건너뜁니다.** 건너뛴 목록이 출력됩니다. 덮어쓰려면 `-Force`를 붙입니다.
- `-WithTemplates`를 붙이면 `opencode.json`과 `AGENTS.md`를 프로젝트 루트에 만듭니다. 이미 있으면 건드리지 않고, 직접 합칠 수 있게 안내만 출력합니다.
- 설치가 끝나면 프로젝트의 `.gitignore`에 `.jarvis/`를 추가하세요. 태스크 상태와 워크트리는 로컬 전용입니다.

#### 3) 전역 설치 (모든 프로젝트에서 사용)

```powershell
powershell -ExecutionPolicy Bypass -File .\install\install.ps1 -Global
```

- 기본 위치는 `%USERPROFILE%\.config\opencode\`입니다.
- 실제 위치는 `opencode debug paths`를 실행해 `config` 줄에서 확인하세요. 다르면 `-ConfigDir <그 경로>`를 붙입니다.
- 전역 설치에는 `opencode.json` 템플릿이 들어가지 않습니다. 권한 규칙은 각 에이전트 파일 안에도 들어 있습니다.

#### 4) 설치 확인

```powershell
cd C:\work\my-app
opencode agent list      # jarvis-queen (primary) 와 jarvis-* (subagent) 5개가 보여야 함
opencode debug skill     # jarvis-factory, tdd 등 스킬이 보여야 함
```

#### 설치 스크립트 옵션

| PowerShell | bash | 설명 |
|---|---|---|
| `-Target <폴더>` | `--target <폴더>` | 프로젝트에 설치 (`<폴더>\.opencode\`) |
| `-Global` | `--global` | 전역 설치 |
| `-ConfigDir <폴더>` | `--config-dir <폴더>` | 전역 설치 위치 지정 |
| `-Only all\|factory\|skills` | `--only …` | 전부 / Jarvis 팩토리만 / 범용 스킬만 |
| `-WithTemplates` | `--with-templates` | `opencode.json`, `AGENTS.md` 템플릿 생성 (프로젝트 설치만) |
| `-Force` | `--force` | 기존 파일 덮어쓰기 |
| `-DryRun` | `--dry-run` | 바꾸지 않고 무엇을 할지만 출력 |
| `-Uninstall` | `--uninstall` | 제거 (직접 고친 파일은 남김, `-Force`면 함께 제거) |

macOS·Linux·WSL에서는 `bash install/install.sh --target ~/work/my-app --with-templates`처럼 씁니다.

#### 수동 설치

스크립트를 실행할 수 없는 환경이면 폴더를 그대로 복사하세요.

- **프로젝트 설치:** 이 패키지의 `.opencode\agents`, `.opencode\commands`, `.opencode\skills`를 대상 프로젝트의 `.opencode\` 아래로 복사합니다.
- **전역 설치:** 같은 폴더들을 `%USERPROFILE%\.config\opencode\` 아래로 복사합니다.

### 모델 지정 (사내 LLM 등)

에이전트 파일에는 모델이 지정돼 있지 않아서, OpenCode의 기본 모델을 씁니다. 역할별로 바꾸려면 다음 둘 중 하나를 쓰세요.

- 각 에이전트 파일 frontmatter에 `model: <provider>/<model>`을 추가합니다.
- 프로젝트 `opencode.json`에서 지정합니다.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "jarvis-queen":    { "model": "company-llm/large-model" },
    "jarvis-reviewer": { "model": "company-llm/large-model" },
    "jarvis-tester":   { "model": "company-llm/fast-model" }
  }
}
```

`company-llm/...`은 예시입니다. 실제 이름은 `opencode models`로 확인하세요.

### 사용법

#### 처음 한 번: 프로젝트 분석

1. 프로젝트 폴더에서 `opencode`를 실행합니다.
2. **Tab** 키로 `jarvis-queen`을 고릅니다.
3. 다음을 실행합니다.

```
/jarvis-analyze
```

- Queen이 스택과 CI 설정을 읽고 build·test·lint 명령을 찾습니다. 찾은 명령은 **한 번씩 실제로 실행해** 결과를 확인합니다.
- 확인이 끝나면 `.jarvis/analysis.md`를 쓰고, `.jarvis/project.json`(게이트가 쓸 명령)을 제안합니다.
- **사람이 확인한 뒤에만** 저장합니다. 이 명령들이 게이트의 근거가 되기 때문입니다.

#### 기능 개발 / 버그 수정

```
/jarvis-feature 회원 이름이 비어 있으면 생성 API가 400을 돌려주게 해줘. 테스트 포함.
```

트랙을 직접 정하려면 끝에 `--track simple|standard|parallel`을 붙입니다.

| 트랙 | 언제 | 흐름 |
|---|---|---|
| `simple` | 파일 3개 안팎, 낮은 위험 | developer → reviewer (계획·테스트·통합 확인은 Queen) |
| `standard` | 여러 모듈, 설계 판단, 중간 위험 | planner → developer → tester → reviewer → integrator |
| `parallel` | 파일이 겹치지 않는 독립 하위 작업이 2개 이상 | 하위 작업마다 별도 워크트리, developer 최대 2명 동시 |

진행 흐름은 다음과 같습니다.

```
REQUEST → REQUIREMENTS_ANALYSIS → PLANNING → TASK_ASSIGNMENT → DEVELOPMENT → TESTING
        → CODE_REVIEW → INTEGRATION → QUALITY_GATE → COMPLETED
실패 → DEVELOPMENT로 되돌림 (자동 재시도 최대 2회) → 그다음은 ESCALATED (사람이 결정)
```

- **워크트리:** 작업은 `.jarvis\worktrees\<TASK-ID>\`(브랜치 `jarvis/<TASK-ID>`)에서 진행합니다. 메인 작업 트리는 건드리지 않습니다. 워크트리를 만들 때 승인 창이 뜹니다.
- **기록:** 각 단계의 결과 JSON, 실패 사유, 게이트 결과가 `.jarvis\tasks\<TASK-ID>\`에 쌓입니다.
- **완료 조건:** 품질 게이트의 필수 항목이 모두 PASSED일 때만 COMPLETED가 됩니다. 명령이 설정되지 않은 필수 게이트는 BLOCKED입니다.

#### 그 밖의 명령

| 명령 | 하는 일 |
|---|---|
| `/jarvis-status` | 열린 태스크 목록, 상태, 다음 할 일 |
| `/jarvis-review <TASK-ID>` | 새 리뷰어로 코드·보안·아키텍처 리뷰 (경로나 브랜치를 주면 기록 없는 즉석 리뷰) |
| `/jarvis-gate <TASK-ID>` | 품질 게이트 실행 → 완료 또는 되돌림 |

#### 서브에이전트를 직접 부르기

OpenCode 버전에 따라 Queen이 커스텀 서브에이전트를 자동으로 호출하지 못할 수 있습니다. 그러면 Queen이 위임 내용을 `.jarvis\tasks\<ID>\envelope-<역할>-c<N>.md`에 저장하고, 실행할 문장을 알려 줍니다. 그대로 붙여 넣으면 됩니다.

```
@jarvis-developer Read .jarvis/tasks/T-20261110-093000/envelope-developer-c1.md and follow it.
```

#### 작업이 끝난 뒤 (사람이 할 일)

Queen은 커밋하지 않습니다. 보고서(`.jarvis\tasks\<ID>\REPORT.md`)를 보고 다음을 직접 실행합니다.

```powershell
git -C .jarvis\worktrees\T-20261110-093000 diff                       # 변경 검토
git -C .jarvis\worktrees\T-20261110-093000 add -A
git -C .jarvis\worktrees\T-20261110-093000 commit -m "<제안된 메시지>"
git merge jarvis/T-20261110-093000                                    # 메인 브랜치에서
git worktree remove .jarvis\worktrees\T-20261110-093000
```

#### 범용 스킬 13종

OpenCode가 작업 내용과 스킬 설명이 맞을 때 알아서 불러옵니다. 직접 쓰게 하려면 프롬프트에 "use the tdd skill"처럼 적으세요. (OpenCode V2 문서에는 `@<스킬이름>`으로 불러오는 방법도 있지만, 1.x에서는 확인하지 않았습니다.)

| 스킬 | 언제 |
|---|---|
| `code-reviewer` | 커밋 전 변경분 전반 점검 |
| `security-reviewer` | 인증·입력·시크릿을 다룬 코드의 취약점 감사 |
| `spring-boot-reviewer` | Spring 컨트롤러·서비스·레포지토리 변경 |
| `react-typescript-reviewer` | React 컴포넌트 변경 (i18n·다크 테마 포함) |
| `design-pattern-advisor` | 패턴 추천, 과설계 점검 |
| `codex-grade-coding` | 새 기능을 처음부터 프로덕션 수준으로 |
| `tdd` | 테스트 먼저 (red-green-refactor) |
| `systematic-debugging` | 근본 원인을 가설·검증으로 찾기 |
| `env-doctor` | 빌드·설치·버전 충돌 진단 |
| `prompt-engineer` | LLM 프롬프트 다듬기 |
| `skill-creator` | 새 SKILL.md 만들기 |
| `queen-orchestration` | Jarvis 워크플로 없이 가벼운 퀸-워커 오케스트레이션 (프리셋: 설계문서·코드리뷰·코드개발) |
| `pdf-table-clip-check` | DRM PDF를 페이지 이미지로 렌더해 표 잘림 검사 (Python + pillow·numpy) |

`jarvis-queen`과 `queen-orchestration`은 쓰임새가 다릅니다.
- **`jarvis-queen`:** 상태 파일과 게이트가 있는 엄격한 개발 워크플로입니다.
- **`queen-orchestration`:** 문서 작성이나 조사처럼 가벼운 병렬 작업용 패턴입니다.

### 권한과 안전장치

- **에이전트별 권한:** 각 에이전트 파일의 `permission:`에 들어 있습니다.
  - planner·tester·reviewer·integrator는 **편집 도구 사용이 금지**됩니다.
  - planner·reviewer·integrator는 읽기 전용 git 명령만 허용하고, 나머지 명령은 승인을 받습니다.
  - tester는 테스트를 돌려야 하므로 셸 명령을 승인 없이 실행합니다(커밋·브랜치 조작·배포·`.env` 읽기는 거부, 삭제는 승인). 셸은 샌드박스가 아니어서 이론상 셸로 파일을 바꿀 수 있습니다.
- **승인이 필요한 명령:** 커밋·push·병합·rebase·reset·clean·checkout·switch·stash, 브랜치·워크트리 생성과 삭제, 파일 삭제(`rm`, `del`, `erase`, `ri`, `Remove-Item`), 배포성 명령(`kubectl`, `terraform`, `helm`, `docker push`, `npm publish`, `gh`). `.env*` 읽기는 막혀 있습니다. 같은 목록이 에이전트 파일과 `templates/opencode.json`에 똑같이 들어 있고, `tools/validate.py`가 둘이 어긋나지 않는지 검사합니다.
- **프로젝트 공통 규칙:** `templates/opencode.json`은 같은 규칙을 프로젝트 전체에 적용합니다. OpenCode는 프로젝트 규칙 뒤에 에이전트 규칙을 적용하고, 나중에 맞는 규칙이 이깁니다.
- **한계:** OpenCode의 권한 패턴은 명령 문자열을 패턴으로 비교하는 장치이고, 샌드박스가 아닙니다. 예를 들어 `git diff … ; rm …`처럼 이어 붙인 명령까지 완전히 막지는 못합니다. 중요한 저장소는 커밋해 두고 작업하세요.

### Windows 참고

- **셸:** OpenCode가 Windows에서 어떤 셸로 명령을 실행하는지는 공식 문서에 명시돼 있지 않고, 설치 환경에 따라 다를 수 있습니다. 그래서 이 패키지의 명령은 `git -C <경로>`처럼 Git Bash와 PowerShell 양쪽에서 도는 형태로 썼습니다.
- **프로젝트 명령:** `.jarvis/project.json`의 build/test 명령도 두 셸에서 모두 도는 형태를 권합니다. 예: `mvn -f backend/pom.xml test`, `npm --prefix web test`.
- **PowerShell 5.1:** `&&`를 지원하지 않습니다. `cd a && b` 같은 명령은 Git Bash나 PowerShell 7에서만 됩니다.
- **실행 정책:** 회사 정책 때문에 스크립트를 못 돌리면 [수동 설치](#수동-설치)를 쓰세요.
- **경로:** 긴 경로 문제가 있으면 짧은 폴더(예: `C:\work\`)에 프로젝트를 두세요. `git config --global core.longpaths true`도 도움이 됩니다.

### OpenCode V1 / V2 호환

모든 파일은 **V1 frontmatter**(`permission`, `tools`, `temperature`)로, V2 기본 위치(`.opencode/agents|commands|skills/`)에 있습니다.

- **V1 (1.18.x, 1.19.x):** 그대로 읽힙니다. macOS에서 1.18.34로 직접 확인했고, CI가 Windows·Linux에서 1.18.34·1.19.5로 검사합니다.
- **V2:** 공식 이전 문서에 따르면 V1 frontmatter를 메모리에서 자동 변환합니다. 이 패키지는 아직 V2에서 CI로 검증하지 않았습니다.
- **주의:** OpenCode 1.x는 V2 전용 키(`permissions`, `system`, `disabled`, `request`)를 무시합니다. 그래서 규칙을 그 키로 옮기면 1.x에서는 **조용히 사라집니다**(1.18.34에서 확인). 반대로 V2는 V2 전용 키가 하나라도 있는 파일에서 V1 키를 무시합니다. 회사 PC가 1.x라면 V1 형식을 유지하세요. `tools/validate.py`가 이 점을 검사합니다.

### Claude Code 판과의 차이

원래 Jarvis Dev Factory는 Claude Code에서 쓰던 것이고, 그쪽에는 워크플로 CLI와 훅(hook) 기반 가드가 있었습니다. 이 OpenCode 판은 **프롬프트와 권한 설정**만으로 만들었습니다.

- 상태 전이, 동시 실행 제한(서브에이전트 2개, 테스트 스위트 1개), 게이트 판정은 **Queen의 절차**로 지킵니다. 코드로 강제하지는 않습니다.
- 그래서 진행 중에 `.jarvis/tasks/<ID>/task.md`의 기록을 가끔 확인하세요.

### 문제 해결

| 증상 | 확인 |
|---|---|
| `jarvis-queen`이 Tab 목록에 없음 | `opencode agent list`. 프로젝트 루트에서 실행했는지, `.opencode\agents\`에 파일이 있는지 확인 |
| 스킬이 안 보임 | `opencode debug skill`. 같은 이름의 스킬이 전역에도 있으면 프로젝트 쪽이 우선 |
| 서브에이전트가 자동으로 안 불림 | 위의 `@jarvis-…` 멘션 방식 사용 |
| 설치가 "skipped"만 출력 | 이미 같은 파일이 있음. 덮어쓰려면 `-Force` |
| 스크립트 실행 차단 | `Unblock-File` 또는 `-ExecutionPolicy Bypass`, 안 되면 수동 설치 |
| 게이트가 BLOCKED | `.jarvis/project.json`에 build/test/lint 명령이 비어 있음. `/jarvis-analyze`로 다시 설정 |

### 제거

```powershell
powershell -ExecutionPolicy Bypass -File .\install\install.ps1 -Target C:\work\my-app -Uninstall
powershell -ExecutionPolicy Bypass -File .\install\install.ps1 -Global -Uninstall
```

설치 뒤 직접 고친 파일은 남겨 두고 목록만 출력합니다. 함께 지우려면 `-Force`를 붙입니다. `-WithTemplates`로 만든 `opencode.json`·`AGENTS.md`와 `.jarvis/` 폴더는 지우지 않습니다(직접 정리).

### 라이선스

[MIT](LICENSE)

---

## English

### What is it?

A multi-agent setup for [OpenCode](https://opencode.ai) that takes one development request through **verifiable stages**: requirements → plan → isolated worktree → develop → test → independent review → integrate → quality gate.

- **The Queen (`jarvis-queen`, primary)** splits the work, delegates it to subagents, and verifies their results against the diff and real command output.
  - The Queen runs the quality gate itself: build/test/lint, reviews and diff inspection.
  - It never commits, pushes, merges or deletes. It prepares those steps and a human runs them.
- **Five role subagents** have their own permissions. For example, the reviewer cannot edit files, and the developer edits only inside the task worktree.
- Progress is stored as files in the project's **`.jarvis/`** folder, so an interrupted session can continue with `/jarvis-status`.
- **13 general development skills** are included as well: code review, TDD, debugging, security review and more.

### Contents

| Path | What |
|---|---|
| `.opencode/agents/jarvis-queen.md` | The orchestrator (primary; select it with Tab) |
| `.opencode/agents/jarvis-{planner,developer,tester,reviewer,integrator}.md` | Role subagents |
| `.opencode/commands/jarvis-*.md` | `/jarvis-analyze`, `/jarvis-feature`, `/jarvis-review`, `/jarvis-gate`, `/jarvis-status` |
| `.opencode/skills/jarvis-*/` | 5 workflow skills (state-file formats, JSON schemas, delegation template) |
| `.opencode/skills/<13 general>/` | code-reviewer, codex-grade-coding, design-pattern-advisor, env-doctor, prompt-engineer, react-typescript-reviewer, security-reviewer, skill-creator, spring-boot-reviewer, systematic-debugging, tdd, queen-orchestration, pdf-table-clip-check |
| `templates/opencode.json` | Permission template (dangerous commands need approval; `.env` reads denied) |
| `templates/AGENTS.md` | Project rules template |
| `install/install.ps1`, `install/install.sh` | Install / uninstall (Windows / macOS · Linux · WSL) |
| `tools/validate.py` | Package validator (also used by CI) |

### Requirements

- **OpenCode 1.18 or later.** CI installs and loads the package with OpenCode 1.18.34 and 1.19.5 on Windows and Linux (see the badge at the top). For V2, see [V1 / V2 compatibility](#opencode-v1--v2-compatibility).
- **Git for Windows**, for worktrees and diffs. The merge check (`git merge-tree --write-tree`) needs git 2.38 or later.
- **Windows PowerShell 5.1 or PowerShell 7**, for the installer.
- Optional: **Python 3**, for the `pdf-table-clip-check` skill and `tools/validate.py`.
- A **model configured in OpenCode** (`opencode providers`). A company LLM gateway works too.

> The OpenCode documentation **recommends WSL on Windows**. Native Windows works as well, and the commands in this package are written to run in both Git Bash and PowerShell.

### Install

#### 1) Download

- **From a release:** get `jarvis-opencode-agents-v1.0.0.zip` from [Releases](https://github.com/xgeekover/jarvis-opencode-agents/releases) and extract it.
- **With git:**
  ```powershell
  git clone https://github.com/xgeekover/jarvis-opencode-agents.git
  cd jarvis-opencode-agents
  ```

PowerShell may block scripts that came from the internet. If it does, run this once in the extracted folder:

```powershell
Get-ChildItem -Recurse | Unblock-File
```

#### 2) Install into a project (recommended)

This copies the agents, commands and skills into the project's `.opencode\`. Add `-WithTemplates` to install the templates too.

```powershell
powershell -ExecutionPolicy Bypass -File .\install\install.ps1 -Target C:\work\my-app -WithTemplates
```

- Existing files are **skipped, never overwritten**, and the skipped files are listed. Use `-Force` to overwrite.
- `-WithTemplates` creates `opencode.json` and `AGENTS.md` in the project root. If either already exists, it is left alone and you are told to merge it by hand.
- Afterwards, add `.jarvis/` to the project's `.gitignore`. Task state and worktrees are local.

#### 3) Global install (for all projects)

```powershell
powershell -ExecutionPolicy Bypass -File .\install\install.ps1 -Global
```

- The default location is `%USERPROFILE%\.config\opencode\`.
- Check the real location with `opencode debug paths` (the `config` line). If it differs, pass `-ConfigDir <that path>`.
- A global install does not include the `opencode.json` template. Each agent file also carries its own permission rules.

#### 4) Check the install

```powershell
cd C:\work\my-app
opencode agent list      # expect jarvis-queen (primary) and five jarvis-* subagents
opencode debug skill     # expect jarvis-factory, tdd and the other skills
```

#### Installer options

| PowerShell | bash | Meaning |
|---|---|---|
| `-Target <dir>` | `--target <dir>` | Install into a project (`<dir>\.opencode\`) |
| `-Global` | `--global` | Install globally |
| `-ConfigDir <dir>` | `--config-dir <dir>` | Global location to use |
| `-Only all\|factory\|skills` | `--only …` | Everything / Jarvis factory only / general skills only |
| `-WithTemplates` | `--with-templates` | Create the `opencode.json` and `AGENTS.md` templates (project install only) |
| `-Force` | `--force` | Overwrite existing files |
| `-DryRun` | `--dry-run` | Show what would happen without changing anything |
| `-Uninstall` | `--uninstall` | Remove (files you changed are kept unless `-Force`) |

On macOS, Linux or WSL: `bash install/install.sh --target ~/work/my-app --with-templates`.

#### Manual install

If you cannot run scripts, copy the folders directly.

- **Project install:** copy `.opencode\agents`, `.opencode\commands` and `.opencode\skills` from this package into the target project's `.opencode\`.
- **Global install:** copy the same folders into `%USERPROFILE%\.config\opencode\`.

### Choosing models (e.g. a company LLM)

The agent files set no model, so they use OpenCode's default model. To pick a model per role, either:

- add `model: <provider>/<model>` to an agent's frontmatter, or
- set it in the project's `opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "jarvis-queen":    { "model": "company-llm/large-model" },
    "jarvis-reviewer": { "model": "company-llm/large-model" },
    "jarvis-tester":   { "model": "company-llm/fast-model" }
  }
}
```

`company-llm/...` is a placeholder. Find the real names with `opencode models`.

### Usage

#### Once per project: analyse it

1. Run `opencode` in the project folder.
2. Press **Tab** to select `jarvis-queen`.
3. Run:

```
/jarvis-analyze
```

- The Queen reads the stack and the CI configuration to find the build/test/lint commands, and **runs each one once** to check it.
- It then writes `.jarvis/analysis.md` and proposes `.jarvis/project.json`, the commands the gate will use.
- It saves that file **only after a human confirms it**, because those commands become gate evidence.

#### Features and fixes

```
/jarvis-feature Make the create-member API return 400 when the name is empty, with tests.
```

To choose the track yourself, append `--track simple|standard|parallel`.

| Track | When | Flow |
|---|---|---|
| `simple` | about 3 files or fewer, low risk | developer → reviewer (the Queen does planning, testing and integration checks) |
| `standard` | several modules, a design choice, moderate risk | planner → developer → tester → reviewer → integrator |
| `parallel` | two or more independent subtasks with disjoint files | one worktree per subtask, at most 2 developers at once |

The workflow:

```
REQUEST → REQUIREMENTS_ANALYSIS → PLANNING → TASK_ASSIGNMENT → DEVELOPMENT → TESTING
        → CODE_REVIEW → INTEGRATION → QUALITY_GATE → COMPLETED
failure → back to DEVELOPMENT (up to 2 automatic retries) → then ESCALATED (a human decides)
```

- **Worktree:** the work happens in `.jarvis\worktrees\<TASK-ID>\` on branch `jarvis/<TASK-ID>`. Your main working tree is not touched. An approval prompt appears when the worktree is created.
- **Records:** each stage's JSON, every failure reason and the gate results are kept in `.jarvis\tasks\<TASK-ID>\`.
- **Done means done:** a task is COMPLETED only when every mandatory gate PASSED. A mandatory gate without a configured command is BLOCKED.

#### Other commands

| Command | What it does |
|---|---|
| `/jarvis-status` | Open tasks, their status and the next step |
| `/jarvis-review <TASK-ID>` | Code, security and architecture review by a fresh reviewer. Given a path or branch, it does an ad-hoc review and records nothing. |
| `/jarvis-gate <TASK-ID>` | Run the quality gate, then complete the task or send it back |

#### Calling a subagent by hand

Some OpenCode versions do not let the Queen call custom subagents automatically. In that case the Queen saves the delegation to `.jarvis\tasks\<ID>\envelope-<role>-c<N>.md` and tells you what to paste:

```
@jarvis-developer Read .jarvis/tasks/T-20261110-093000/envelope-developer-c1.md and follow it.
```

#### After a task (your part)

The Queen never commits. Read the report (`.jarvis\tasks\<ID>\REPORT.md`), then run:

```powershell
git -C .jarvis\worktrees\T-20261110-093000 diff                       # review the change
git -C .jarvis\worktrees\T-20261110-093000 add -A
git -C .jarvis\worktrees\T-20261110-093000 commit -m "<proposed message>"
git merge jarvis/T-20261110-093000                                    # on your main branch
git worktree remove .jarvis\worktrees\T-20261110-093000
```

#### The 13 general skills

OpenCode loads a skill on its own when your task matches the skill's description. To ask for one explicitly, write "use the tdd skill" in your prompt. (The OpenCode V2 docs also describe loading a skill with `@<skill-name>`; this was not checked on 1.x.)

| Skill | Use it for |
|---|---|
| `code-reviewer` | A pre-commit review of the whole change |
| `security-reviewer` | A vulnerability audit of code that handles auth, input or secrets |
| `spring-boot-reviewer` | Spring controller, service or repository changes |
| `react-typescript-reviewer` | React component changes (i18n and dark theme included) |
| `design-pattern-advisor` | Pattern suggestions and over-engineering checks |
| `codex-grade-coding` | Writing a new feature at production quality from the start |
| `tdd` | Test first (red-green-refactor) |
| `systematic-debugging` | Finding a root cause by hypothesis and verification |
| `env-doctor` | Diagnosing build, install and version conflicts |
| `prompt-engineer` | Hardening LLM prompts |
| `skill-creator` | Scaffolding a new SKILL.md |
| `queen-orchestration` | Lightweight queen-worker orchestration without the Jarvis workflow (presets: design doc, code review, code development) |
| `pdf-table-clip-check` | Checking DRM PDFs for clipped tables from rendered page images (Python + pillow, numpy) |

`jarvis-queen` and `queen-orchestration` serve different purposes:
- **`jarvis-queen`** is the strict development workflow, with state files and gates.
- **`queen-orchestration`** is a lightweight pattern for parallel work such as documents or research.

### Permissions and safety

- **Per-agent rules** live in each agent file's `permission:` block.
  - The planner, tester, reviewer and integrator **cannot use the edit tools**.
  - The planner, reviewer and integrator may run read-only git commands; every other command asks.
  - The tester has to run tests, so it runs shell commands without approval (commits, branch operations, deployments and `.env` reads are denied; deletions ask). The shell is not a sandbox, so in theory the tester could still change files through it.
- **Commands that need approval:** commit, push, merge, rebase, reset, clean, checkout, switch, stash, creating or deleting branches and worktrees, deleting files (`rm`, `del`, `erase`, `ri`, `Remove-Item`) and deployment-like commands (`kubectl`, `terraform`, `helm`, `docker push`, `npm publish`, `gh`). Reading `.env*` is denied. The same list is in the agent files and in `templates/opencode.json`, and `tools/validate.py` checks that they stay in sync.
- **Project-wide rules:** `templates/opencode.json` applies the same rules to the whole project. OpenCode applies agent rules after project rules, and the last matching rule wins.
- **Limit:** OpenCode permissions match command strings against patterns; they are not a sandbox. A chained command such as `git diff … ; rm …` is not fully contained. Commit important work before you start.

### Notes for Windows

- **Shell:** the OpenCode documentation does not say which shell runs commands on Windows, and it may depend on your setup. The commands in this package therefore use forms that work in both Git Bash and PowerShell, such as `git -C <path>`.
- **Project commands:** write the build/test commands in `.jarvis/project.json` so they work in both shells too, for example `mvn -f backend/pom.xml test` or `npm --prefix web test`.
- **PowerShell 5.1:** it has no `&&`, so commands like `cd a && b` work only in Git Bash or PowerShell 7.
- **Execution policy:** if company policy blocks scripts, use the [manual install](#manual-install).
- **Long paths:** keep projects in short folders (for example `C:\work\`). `git config --global core.longpaths true` also helps.

### OpenCode V1 / V2 compatibility

Every file uses **V1 frontmatter** (`permission`, `tools`, `temperature`) and sits in the V2 default locations (`.opencode/agents|commands|skills/`).

- **V1 (1.18.x, 1.19.x):** loaded as is. Checked by hand on macOS with 1.18.34; CI checks Windows and Linux with 1.18.34 and 1.19.5.
- **V2:** according to the official migration guide, V2 translates V1 frontmatter in memory. This package is not yet CI-tested on V2.
- **Caution:** OpenCode 1.x ignores the V2-only keys (`permissions`, `system`, `disabled`, `request`), so rules moved there are **silently lost** on 1.x (seen on 1.18.34). Conversely, V2 ignores a file's V1 keys once the file contains any V2-only key. Keep the V1 format while your PCs run 1.x. `tools/validate.py` checks for this.

### Differences from the Claude Code edition

The original Jarvis Dev Factory runs in Claude Code, where it has a workflow CLI and hook-based guards. This OpenCode edition is built from **prompts and permission rules only**.

- State transitions, the concurrency limits (2 subagents, 1 test suite) and the gate verdicts are kept by the **Queen's procedure**. No code enforces them.
- So check the record in `.jarvis/tasks/<ID>/task.md` now and then.

### Troubleshooting

| Symptom | Check |
|---|---|
| `jarvis-queen` is missing from the Tab list | `opencode agent list`. Did you start in the project root, and are the files in `.opencode\agents\`? |
| Skills don't show up | `opencode debug skill`. If a global skill has the same name, the project one wins. |
| The Queen doesn't call subagents itself | Use the `@jarvis-…` mention described above |
| The installer only prints "skipped" | The files already exist. Use `-Force` to overwrite. |
| The script is blocked | `Unblock-File` or `-ExecutionPolicy Bypass`; otherwise use the manual install |
| A gate is BLOCKED | A build/test/lint command in `.jarvis/project.json` is empty. Re-run `/jarvis-analyze`. |

### Uninstall

```powershell
powershell -ExecutionPolicy Bypass -File .\install\install.ps1 -Target C:\work\my-app -Uninstall
powershell -ExecutionPolicy Bypass -File .\install\install.ps1 -Global -Uninstall
```

Files you changed after installing are kept and listed. Add `-Force` to remove them too. The `opencode.json` and `AGENTS.md` created by `-WithTemplates`, and the `.jarvis/` folder, are never removed; delete them yourself if you want.

### License

[MIT](LICENSE)
