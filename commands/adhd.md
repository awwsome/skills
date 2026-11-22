---
description: adhd 모드를 켠다(결정 질문을 아주 쉽게, 추천안과 함께 묻는 모드). 끌 때는 /adhd off
argument-hint: "[off]"
---

<!-- /adhd 단축 입력. 본체는 이 저장소의 skills/adhd-mode/SKILL.md(adhd-mode 스킬)다. -->

인자: $ARGUMENTS

- 인자가 `off`, `꺼`, `끄기` 중 하나면 Skill 도구를 부르지 않는다. 첫 줄을 정확히 "adhd 모드를 껐어요."로 시작하는 한 줄로 답하고 평소 문체로 돌아간다.
- 그 밖에는 Skill 도구로 `adhd-mode` 스킬을 불러 따른다. 플러그인으로 설치했으면 스킬 이름이 `awwsome-skills:adhd-mode`처럼 플러그인 이름을 앞에 단다. 인자에 다른 요청이 있으면 모드를 켠 뒤 그 요청을 이 모드로 처리한다.
