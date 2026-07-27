"""
BKR 테스트 케이스 생성 보조 스크립트
Java Service 파일에서 메서드 시그니처를 추출하여
Claude Code의 테스트 케이스 생성을 보조한다.
"""

import re
from dataclasses import dataclass, field


@dataclass
class MethodInfo:
    name: str
    return_type: str
    params: list[str]
    throws: list[str]
    line: int
    is_void: bool = False


# Java 메서드 시그니처 패턴
METHOD_PATTERN = re.compile(
    r'(?:public|protected)\s+'          # 접근 제어자
    r'(?:(?!class|interface)\S+)\s+'    # 반환 타입
    r'(\w+)\s*\('                        # 메서드명
    r'([^)]*)\)'                         # 파라미터
    r'(?:\s*throws\s+([\w,\s]+))?'      # throws 절 (선택)
    r'\s*\{'                             # 메서드 시작
)


def extract_methods(file_path: str) -> list[dict]:
    """
    Java 파일에서 public/protected 메서드 정보 추출.
    반환값: MethodInfo 딕셔너리 리스트
    """
    results = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        return [{"error": str(e)}]

    for i, line in enumerate(lines, start=1):
        match = METHOD_PATTERN.search(line)
        if not match:
            continue

        method_name = match.group(1)
        params_raw  = match.group(2).strip()
        throws_raw  = match.group(3)

        # 생성자 제외 (대문자로 시작하는 경우)
        if method_name[0].isupper():
            continue

        params = [p.strip() for p in params_raw.split(",") if p.strip()] if params_raw else []
        throws = [t.strip() for t in throws_raw.split(",")] if throws_raw else []

        # void 여부
        is_void = "void" in line[:line.index(method_name)]

        results.append({
            "name":        method_name,
            "params":      params,
            "throws":      throws,
            "line":        i,
            "is_void":     is_void,
            "raw":         line.strip(),
        })

    return results


def suggest_test_cases(method: dict) -> list[str]:
    """
    메서드 정보를 기반으로 생성할 테스트 케이스 명 제안.
    """
    name = method["name"]
    cases = [f"should_return_result_when_{name}_called_with_valid_input"]

    # 파라미터가 있으면 null 케이스 추가
    if method["params"]:
        cases.append(f"should_throw_exception_when_{name}_called_with_null_input")

    # throws 선언이 있으면 예외 케이스 추가
    for ex in method["throws"]:
        ex_short = ex.replace("Exception", "").lower()
        cases.append(f"should_throw_{ex_short}_exception_when_{name}_fails")

    # find/get 계열이면 NotFound 케이스 추가
    if name.startswith(("find", "get", "fetch")):
        cases.append(f"should_throw_not_found_when_{name}_with_nonexistent_id")

    return cases


if __name__ == "__main__":
    import sys, json
    if len(sys.argv) > 1:
        methods = extract_methods(sys.argv[1])
        for m in methods:
            m["suggested_tests"] = suggest_test_cases(m)
        print(json.dumps(methods, ensure_ascii=False, indent=2))
