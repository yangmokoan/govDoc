# BKR 테스트 케이스 자동 생성 거버넌스 v1.0

## 1. 목적
BKR CRM 소스코드를 분석하여 JUnit5 기반 단위 테스트 케이스를 자동 생성한다.

## 2. 생성 범위
- Service 레이어 메서드 대상 단위 테스트
- 정상 케이스 (Happy Path) 필수 생성
- 예외 케이스 (Edge Case, Exception) 필수 생성
- Mockito를 활용한 의존성 Mock 처리

## 3. 테스트 작성 규칙
| 항목 | 규칙 |
|---|---|
| 테스트 클래스명 | 대상클래스명 + Test (예: CustomerServiceTest) |
| 테스트 메서드명 | should_결과_when_조건 형식 |
| Given-When-Then | 주석으로 구분 필수 |
| Mock 라이브러리 | Mockito 사용 (BDDMockito 스타일 권장) |
| Assertion | AssertJ 사용 |

## 4. 필수 생성 케이스
- 정상 입력 → 정상 반환
- null 입력 → NullPointerException 또는 커스텀 예외
- 존재하지 않는 ID 조회 → NotFoundException
- 중복 데이터 등록 → DuplicateException

## 5. 심각도 기준 (커버리지 미달 시)
- Critical: 핵심 비즈니스 로직 테스트 0%
- High: 예외 케이스 테스트 누락
- Medium: 경계값 테스트 누락
- Low: 주석 미작성
