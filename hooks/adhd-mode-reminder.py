#!/usr/bin/env python3
# UserPromptSubmit, SessionStart(compact) 훅: adhd-mode 스킬이 켜진 세션에서만 매 턴과 대화 요약 직후에 짧은 상기 문구를 넣는다.
# 플러그인으로 설치하면 hooks/hooks.json이 등록한다. 직접 설치할 때는 README의 "훅 직접 등록"을 따른다.
# 외부 패키지 없이 파이썬 표준 라이브러리만 쓰고, 경로는 stdin으로 받은 transcript_path만 읽는다.
# 켜지지 않았거나 꺼진 세션에서는 아무것도 출력하지 않는다. 어떤 실패든 조용히 끝낸다(exit 0, 출력 없음).
#
# 판정: stdin JSON의 transcript_path(JSONL)에서 켜짐·꺼짐 신호 중 "마지막" 것만 본다.
# 신호는 JSON 문자열 값의 맨 앞에 올 때만 센다. 스킬 본문을 읽거나 고친 도구 기록, 설명 글에 섞인 같은 글자를
# 신호로 오인하지 않기 위해서다.
#   켜짐: /adhd·/adhd-mode 명령 기록(플러그인 이름이 붙은 /<플러그인>:adhd 포함), adhd-mode 스킬 본문이 로드된 기록("Base directory for this skill: .../adhd-mode")
#   꺼짐: /adhd off 명령 기록, 사용자가 보낸 "adhd off"·"adhd 꺼" 같은 짧은 메시지, 응답 첫머리의 "adhd 모드를 껐어요"
#
# 속도: 파일 전체에 정규식을 돌리지 않는다. 파일 끝에서부터 b"adhd" 위치만 거꾸로 찾고(mmap.rfind) 그 주변 몇백 바이트만
# 정규식으로 확인한다. 처음 찾은 신호가 마지막 신호다. 시스템 grep은 50MB에 0.4초 걸려서 쓰지 않는다.
import json
import mmap
import re
import sys

REMINDER = (
    "adhd 모드 켜짐: 사용자는 앞선 대화를 거의 기억하지 못한다. 의견이나 결정을 묻는 부분은 adhd-mode 스킬의 "
    "결정 카드로 쓴다(마지막 질문만 읽어도 결정할 수 있게, 추천 선택지를 맨 앞에, 한 번에 3개까지, 내부 용어는 "
    "풀이를 붙여서). 진행 보고와 단순 답은 짧게 쓴다. 스킬 본문이 컨텍스트에 없으면 Skill 도구로 adhd-mode를 "
    "다시 불러온다(플러그인으로 설치했으면 awwsome-skills:adhd-mode). 사용자가 끄라고 하면 첫 줄을 \"adhd 모드를 껐어요.\"로 시작한다."
)

# transcript 안에서 줄바꿈은 JSON 이스케이프(\n, 두 글자)로 저장된다.
PATTERN = re.compile(
    "|".join(
        [
            # 플러그인으로 설치하면 명령이 "/awwsome-skills:adhd"처럼 플러그인 이름을 앞에 달고 기록된다.
            r'"(?:content|text)":"<command-message>(?:[a-z0-9_-]+:)?adhd(?:-mode)?</command-message>\\n'
            r'<command-name>/(?:[a-z0-9_-]+:)?adhd(?:-mode)?</command-name>'
            r'(?:\\n<command-args>(?P<args>[^<"]*)</command-args>)?',
            r'"(?:content|text)":"(?P<skill>Base directory for this skill: )[^"]{0,300}?/adhd-mode\\n',
            r'"(?:content|text)":"(?P<useroff>/?adhd(?: 모드)? ?(?:off|꺼|꺼줘|꺼 줘|끄기|끄자|끝|종료)[.!]?(?:\\n)?")',
            r'"text":"(?P<aioff>adhd 모드를 껐어요)',
        ]
    ).encode("utf-8")
)
OFF_ARGS = {"off", "꺼", "끄기"}
BEFORE, AFTER = 400, 200  # 신호 안의 'adhd' 앞뒤로 볼 바이트 수


def last_signal(mm):
    """파일 끝에서부터 거꾸로 훑어 마지막 신호가 켜짐이면 True, 꺼짐이면 False, 없으면 None."""
    end = len(mm)
    while True:
        i = mm.rfind(b"adhd", 0, end)
        if i < 0:
            return None
        start = max(0, i - BEFORE)
        window = mm[start : i + AFTER]
        rel = i - start
        hit = None
        for m in PATTERN.finditer(window):
            if m.start() <= rel < m.end():
                hit = m
        if hit is not None:
            if hit.group("useroff") or hit.group("aioff"):
                return False
            args = hit.group("args")
            if args is not None and args.decode("utf-8", "replace").strip() in OFF_ARGS:
                return False
            return True
        end = i  # 이 위치는 신호가 아니다. 더 앞을 본다.


def main():
    try:
        data = json.loads(sys.stdin.read() or "{}")
        path = data.get("transcript_path")
        if not path:
            return
        with open(path, "rb") as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                state = last_signal(mm)
        if state:
            print(REMINDER)
    except Exception:
        return


if __name__ == "__main__":
    main()
    sys.exit(0)
