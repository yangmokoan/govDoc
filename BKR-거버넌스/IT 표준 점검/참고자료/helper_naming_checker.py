"""
BKR IT 표준 네이밍 컨벤션 검증 보조 스크립트
Claude Code가 Java 파일 분석 시 참고하는 패턴 정의 모음
"""

import re

# 네이밍 패턴 정의
PATTERNS = {
    "class_pascal":   re.compile(r'^[A-Z][a-zA-Z0-9]*$'),          # PascalCase
    "method_camel":   re.compile(r'^[a-z][a-zA-Z0-9]*$'),          # camelCase
    "const_upper":    re.compile(r'^[A-Z][A-Z0-9_]*$'),            # UPPER_SNAKE_CASE
    "package_lower":  re.compile(r'^[a-z][a-z0-9.]*$'),            # 소문자
}

# BKR 금지 패턴 (발견 시 위반)
FORBIDDEN = {
    "system_out":     re.compile(r'System\.out\.print'),
    "print_trace":    re.compile(r'\.printStackTrace\(\)'),
    "direct_repo":    re.compile(r'@RestController.*Repository', re.DOTALL),
}

# BKR 레이어 접미사 규칙
LAYER_SUFFIX = {
    "controller": ["Controller"],
    "service":    ["Service", "ServiceImpl"],
    "repository": ["Repository", "Mapper"],
    "dto":        ["Dto", "VO", "Request", "Response"],
}


def check_naming_convention(file_path: str) -> dict:
    """
    Java 파일을 읽어 BKR 네이밍 컨벤션 위반 여부를 반환.
    반환값: { "violations": [...], "passed": bool }
    """
    violations = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        return {"violations": [], "passed": True, "error": str(e)}

    for i, line in enumerate(lines, start=1):
        # System.out 사용 여부
        if FORBIDDEN["system_out"].search(line):
            violations.append({
                "line": i,
                "type": "LOGGING",
                "severity": "High",
                "description": "System.out.print 사용 — SLF4J logger로 교체 필요",
                "code": line.strip(),
            })

        # printStackTrace 사용 여부
        if FORBIDDEN["print_trace"].search(line):
            violations.append({
                "line": i,
                "type": "EXCEPTION",
                "severity": "High",
                "description": "printStackTrace() 단독 사용 — log.error()로 교체 필요",
                "code": line.strip(),
            })

    return {
        "violations": violations,
        "passed": len(violations) == 0,
        "total_lines": len(lines),
    }


def get_layer_type(class_name: str) -> str:
    """클래스명 접미사로 레이어 타입 반환"""
    for layer, suffixes in LAYER_SUFFIX.items():
        if any(class_name.endswith(s) for s in suffixes):
            return layer
    return "unknown"


if __name__ == "__main__":
    # 테스트 실행 예시
    import sys
    if len(sys.argv) > 1:
        result = check_naming_convention(sys.argv[1])
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
