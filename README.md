# awwsome/skills

에이전트용 개인 스킬 두 개를 모은 저장소입니다. 한국어 존댓말로 대화하는 사용자를 기준으로 쓴 스킬이라, 에이전트가 사용자에게 쓰는 글도 한국어 존댓말이 됩니다.

| 스킬 | 하는 일 | 켜는 말 |
|---|---|---|
| `adhd-mode` | 사용자가 앞선 대화를 거의 기억하지 못한다고 보고, 의견이나 결정을 묻는 질문을 맥락 없이 읽어도 고를 수 있는 "결정 카드"(추천 선택지 포함)로 씁니다. 진행 보고는 짧게 씁니다. | "adhd 모드", `/adhd` |
| `oc` | 세션을 오케스트레이터로 돌립니다. 모든 작업을 자식 에이전트에 맡기고 본인은 사용자 응대를 위해 비워 둡니다. 자식은 필요하면 손자 에이전트를 만듭니다. | "오케스트레이터 모드", `/oc` |

두 모드는 같이 켜도 됩니다. `oc`가 자식의 질문을 모아 물을 때 `adhd-mode`의 결정 카드 형식을 씁니다.

## 설치

### 1. Claude Code 플러그인 (스킬 + `/adhd` 명령 + 상기 훅)

```bash
claude plugin install awwsome-skills --marketplace awwsome/skills
```

`--marketplace` 옵션이 없는 예전 Claude Code에서는 두 단계로 나눕니다.

```bash
claude plugin marketplace add awwsome/skills
claude plugin install awwsome-skills@awwsome
```

한 프로젝트에만 넣으려면 그 프로젝트 폴더에서 `--scope local`을 붙입니다. 설치한 뒤 새 세션을 열거나, 열려 있는 세션에서 `/reload-plugins`를 실행합니다.

플러그인으로 설치하면 이름 앞에 플러그인 이름이 붙습니다. 스킬은 `awwsome-skills:adhd-mode`, `awwsome-skills:oc`, 명령은 `/awwsome-skills:adhd`입니다. 평소처럼 "adhd 모드 켜"라고 말해도 됩니다.

### 2. 여러 에이전트에 스킬 파일만 (`npx skills`)

[skills CLI](https://github.com/vercel-labs/skills)로 Claude Code, Codex, Cursor 등 설치된 에이전트의 스킬 폴더에 넣습니다.

```bash
npx skills add awwsome/skills -g
```

질문 없이 두 스킬을 모든 에이전트에 넣으려면 `npx skills add awwsome/skills -g --all`, 하나만 넣으려면 `--skill adhd-mode`처럼 이름을 줍니다. `-g`를 빼면 지금 폴더(프로젝트)에만 들어갑니다.

이 방법은 **스킬 파일(`SKILL.md`)만** 설치합니다. `/adhd` 명령과 adhd 상기 훅은 들어가지 않습니다. 훅이 없으면 긴 대화나 대화 요약(compact) 뒤에 에이전트가 모드를 잊을 수 있습니다. 필요하면 아래 "훅 직접 등록"을 따릅니다.

## 전제 조건

- `oc` 스킬은 T3 Code의 `delegate_task`, `orchestrator_capabilities` 같은 오케스트레이션 도구가 있다고 전제합니다. 이 도구가 없는 환경에서는 위임 규칙을 그대로 따를 수 없습니다.
- adhd 상기 훅은 `python3`(표준 라이브러리만 사용)가 필요합니다.
- `adhd-mode`의 그림 규칙은 T3 Code의 `html_preview`·`html_render` 도구가 있으면 쓰고, 없으면 코드 블록 그림으로 대신합니다.

## adhd 상기 훅

`hooks/adhd-mode-reminder.py`는 매 턴(`UserPromptSubmit`)과 대화 요약 직후(`SessionStart`의 `compact`)에 돕니다. 대화 기록(transcript)에서 adhd 모드를 켠 기록과 끈 기록 중 마지막 것을 보고, 켜져 있을 때만 짧은 상기 문구를 넣습니다. 꺼져 있으면 아무것도 출력하지 않고, 어떤 오류가 나도 조용히 끝납니다.

### 훅 직접 등록 (`npx skills`로 설치한 경우)

이 저장소의 `hooks/adhd-mode-reminder.py`를 원하는 곳(예: `~/.claude/hooks/`)에 복사하고, `~/.claude/settings.json`의 `hooks`에 아래를 넣습니다. 이미 다른 훅이 있으면 배열에 덧붙입니다.

```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "hooks": [{ "type": "command", "command": "python3 -I \"$HOME/.claude/hooks/adhd-mode-reminder.py\"", "timeout": 5 }] }
    ],
    "SessionStart": [
      { "matcher": "compact", "hooks": [{ "type": "command", "command": "python3 -I \"$HOME/.claude/hooks/adhd-mode-reminder.py\"", "timeout": 5 }] }
    ]
  }
}
```

플러그인으로 설치했다면 이 단계는 필요 없습니다. 두 방법을 함께 쓰면 상기 문구가 두 번 들어갑니다.

## 끄기

- adhd 모드: "adhd off", "adhd 꺼", `/adhd off`(플러그인은 `/awwsome-skills:adhd off`). 에이전트가 "adhd 모드를 껐어요."로 답하면 훅도 상기를 멈춥니다.
- oc 모드: "오케스트레이터 모드 끝". 돌고 있는 위임이 있으면 계속 둘지 멈출지 묻습니다.
- 플러그인 자체를 끄거나 지우기:

  ```bash
  claude plugin disable awwsome-skills@awwsome
  claude plugin uninstall awwsome-skills@awwsome
  ```

- `npx skills`로 넣은 스킬 지우기: `npx skills remove adhd-mode oc -g`

## 라이선스

MIT
