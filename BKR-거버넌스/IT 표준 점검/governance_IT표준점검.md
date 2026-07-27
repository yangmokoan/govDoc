# BKR IT 표준 준수 점검 거버넌스 v1.0

## 1. 목적
BKR CRM 시스템의 소스코드가 BKR IT 표준 가이드라인을 준수하는지 자동으로 점검한다.

## 2. 점검 범위
- 네이밍 컨벤션 (클래스, 메서드, 변수, 상수)
- 레이어 아키텍처 준수 (Controller → Service → Repository)
- 공통 예외 처리 패턴 적용 여부
- 로깅 표준 준수 (SLF4J + Logback 사용 여부)
- API 응답 형식 표준 (공통 ResponseWrapper 사용 여부)

## 3. 네이밍 컨벤션 규칙
| 대상 | 규칙 | 예시 |
|---|---|---|
| 클래스 | PascalCase | `CustomerService` |
| 메서드 | camelCase | `findCustomerById` |
| 상수 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| DB 컬럼 | snake_case | `customer_id` |
| 패키지 | 소문자 | `com.bkr.crm.service` |

## 4. 레이어 아키텍처
- Controller는 Service만 호출 가능, Repository 직접 호출 금지
- Service는 여러 Repository 조합 가능
- Repository는 DB 접근만 담당, 비즈니스 로직 포함 금지

## 5. 심각도 기준
- Critical: 아키텍처 위반, 보안 관련 표준 미준수
- High: 공통 모듈 미사용, 예외 처리 누락
- Medium: 네이밍 컨벤션 위반
- Low: 코드 스타일, 주석 미작성
