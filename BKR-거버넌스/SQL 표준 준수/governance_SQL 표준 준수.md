# BKR SQL 거버넌스 기준 To-Be 쿼리 평가 분석 보고서

> 기준 문서: `BKR_GVN_DE_SQL표준_가이드_v0.9_20260508.docx`  
> 평가 대상: `BK_CRM_API` (To-Be) MyBatis XML mapper  
> 분석일: 2026-06-30

---

## 1. 거버넌스 핵심 기준 요약

| 항목 | 기준 |
|------|------|
| SQL 표준 | ANSI SQL:2016 |
| 대상 DBMS | Oracle 21c 이상, MySQL 8.0 이상, PostgreSQL 16 이상 |
| 키워드 | 대문자 |
| 테이블/컬럼명 | 대문자 스네이크 케이스 |
| 금지 Oracle 전용 문법 | ROWNUM, NVL, DECODE, SYSDATE, TO_DATE, (+) 조인, CONNECT BY, SELECT * |
| JOIN | 반드시 ANSI 명시적 JOIN (INNER JOIN ... ON) |
| NULL 처리 | COALESCE() 표준 |
| 날짜 | DATE 'YYYY-MM-DD' 표준 |
| 행 제한 | FETCH FIRST n ROWS ONLY |
| 바인드 변수 | 반드시 사용 (#{...}) |
| WHERE 없는 DML | UPDATE/DELETE에 WHERE 없음 → 즉시 반려 |
| SELECT * | 금지 |
| 암시적 형변환 | 금지 |
| 컬럼 가공 | WHERE 절 좌변 컬럼에 함수 적용 금지 |
| DISTINCT | 가급적 지양 |
| 대량 DML | 10,000건 이상 단일 처리 금지, 배치 분할 필수 |
| SQL ID 주석 | `/* 서비스ID */` 형식 블록 주석 |

---

## 2. 평가 대상 파일

| 파일 | 도메인 | 주요 기능 |
|------|--------|---------|
| MEM0010001_DAO.oracle.xml | 회원(MEM) | 로그인 로그, 선호팝업, 최종로그인 업데이트 |
| ORD0010001_DAO.oracle.xml | 주문(ORD) | 주문내역 조회, 메뉴카테고리 판매여부 |
| ORD0010006_DAO.oracle.xml | 주문(ORD) | 주문번호 채번, 점포정보, 임시주문 등록 |
| RIM0010001_DAO.oracle.xml | 데이터수신(RIM) | 메뉴마스터 MERGE, 메뉴플래그 관리 |
| RIM0010002_DAO.oracle.xml | 데이터수신(RIM) | 메뉴가격 MERGE |
| CCT0010001_DAO.oracle.xml | 공통코드(CCT) | 다중 공통코드 조회 |
| XP0010001_DAO.oracle.xml | 경험(XP) | 뱃지 이미지 경로 조회 |
| MBR0010001_DAO.oracle.xml | 멤버십(MBR) | 회원 등급 조회 |
| CPN0010001_DAO.oracle.xml | 쿠폰(CPN) | 쿠폰 목록 조회, 마이픽 프로모션 |
| MemberInfoDAO.oracle.xml | 공통(comm) | 회원 정보 다양한 조건별 조회/수정 |

---

## 3. 위반 사항 상세 분석

### 🔴 Critical — 즉시 반려 수준

#### 3.1 Oracle 전용 함수 `SYSDATE` 광범위 사용
**기준:** `SYSDATE` → `CURRENT_DATE` 또는 `CURRENT_TIMESTAMP` 대체 필수  
**발견 위치 (전 파일에 걸쳐 다수):**

| 파일 | 쿼리 ID | 위반 내용 |
|------|---------|---------|
| MEM0010001 | `v000` | `SYSDATE` (INSERT 시 등록일시) |
| MEM0010001 | `selectYnPreferencePopup` | `TRUNC(SYSDATE)` |
| MEM0010001 | `updateMemberLastLoginDate` | `DT_LAST_LOGIN = SYSDATE` |
| ORD0010001 | `v000` | `ADD_MONTHS(SYSDATE, -3)` |
| ORD0010006 | `getStoreInfo` | `TO_CHAR(SYSDATE, 'd')`, `TO_CHAR(SYSDATE, 'HH24MI')` |
| ORD0010006 | `insertOrderKingTmp` | `NVL(#{receiveTime},SYSDATE)`, `REG_DATE=SYSDATE` |
| RIM0010001 | `saveMenuMst` | `UPD_DATE=SYSDATE` |
| RIM0010001 | `saveOptionMenuOmni` | `UPD_DATE=SYSDATE` |
| RIM0010001 | `insertMenuFlag` | `REG_DATE=SYSDATE`, `UPD_DATE=SYSDATE` |
| RIM0010002 | `saveMenuPrc` | `REG_DATE=SYSDATE`, `UPD_DATE=SYSDATE` |
| CPN0010001 | `selectMyPickDrinkChoicePromo` | `SYSDATE BETWEEN ...` |
| MemberInfoDAO | `getMemberDelHistory` | `TRUNC(SYSDATE - 89)` |
| MemberInfoDAO | `selectAgreeVer` | `SYSDATE >=`, `>= SYSDATE` |

**권장 대체:**
```sql
-- 현재 일시
SYSDATE → CURRENT_TIMESTAMP

-- 날짜 비교 (DATE 타입 컬럼)
TRUNC(SYSDATE) → CURRENT_DATE

-- 날짜 가감
ADD_MONTHS(SYSDATE, -3) → CURRENT_DATE - INTERVAL '3' MONTH
SYSDATE - 89 → CURRENT_DATE - INTERVAL '89' DAY
```

---

#### 3.2 Oracle 전용 함수 `NVL` 사용
**기준:** `NVL(col, val)` → `COALESCE(col, val)` 대체 필수

| 파일 | 쿼리 ID | 위반 내용 |
|------|---------|---------|
| ORD0010006 | `insertOrderKingTmp` | `NVL(#{receiveTime},SYSDATE)` |
| ORD0010006 | `getStoreInfo` | (내부 NVL 다수) |
| RIM0010001 | `updateCoverMenuType` | `NVL(COVER_MENU_TYPE, 0)` |
| RIM0010001 | `saveOptionMenuOmni` | `NVL2(#{OMNI_MENU_NM}, ...)` |
| CCT0010001 | `v000` | `NVL(#{CD_TYPE}, '1')` 등 다수 |
| CPN0010001 | `selectOmniCouponList` | `NVL(TM.COVER_MENU_CD, TM.MENU_CD)` 등 다수 |
| MemberInfoDAO | 다수 SELECT | `NVL(TB.YN_SMS_RECV,'N')` 등 다수 |

**권장 대체:**
```sql
NVL(col, val)       → COALESCE(col, val)
NVL2(col, v1, v2)   → CASE WHEN col IS NOT NULL THEN v1 ELSE v2 END
```

---

#### 3.3 Oracle 전용 `ROWNUM` 사용
**기준:** `ROWNUM <= n` → `FETCH FIRST n ROWS ONLY` 대체 필수

| 파일 | 쿼리 ID | 위반 내용 |
|------|---------|---------|
| MEM0010001 | `selectBkrLoginCount` | `AND ROWNUM <= 3` |
| MemberInfoDAO | `getMemberDelHistory` | `AND ROWNUM = 1` |

**권장 대체:**
```sql
-- ROWNUM <= 3
FETCH FIRST 3 ROWS ONLY

-- ROWNUM = 1 (단건 취득)
FETCH FIRST 1 ROW ONLY
```

---

#### 3.4 Oracle 전용 시퀀스 문법 `SEQUENCE.NEXTVAL FROM DUAL`
**기준:** DBMS 종속 문법 → 이식성 없음

| 파일 | 쿼리 ID | 위반 내용 |
|------|---------|---------|
| MEM0010001 | `v000` | `SEQ_TBS_MEMBER_LOGIN_LOG.NEXTVAL FROM DUAL` |
| ORD0010006 | `getOrderNo` | `SEQ_TBS_ORDER_MAIN.NEXTVAL AS orderNo FROM DUAL` |

**참고:** 현재 대상 DBMS가 Oracle로 고정된 경우 단기적으로는 허용 가능하나, 거버넌스 기준상 명시적 위반.

---

#### 3.5 `SELECT *` 사용
**기준:** 명시적 컬럼 나열 필수, SELECT * 금지

| 파일 | 쿼리 ID | 위반 내용 |
|------|---------|---------|
| ORD0010006 | `getStoreInfo` | `SELECT *` (서브쿼리 외부 SELECT) |

---

#### 3.6 Oracle 전용 `TO_DATE`, `TO_CHAR` 광범위 사용
**기준:** 날짜 리터럴은 `DATE 'YYYY-MM-DD'` 표준 사용

| 파일 | 쿼리 ID | 위반 내용 |
|------|---------|---------|
| MEM0010001 | `selectYnPreferencePopup` | `TRUNC(SYSDATE)` 비교 |
| ORD0010006 | `getStoreInfo` | `TO_CHAR(SYSDATE, 'd')`, `TO_CHAR(SYSDATE, 'HH24MI')` |
| ORD0010006 | `getEtcAddMenuData` | `TO_CHAR(SYSDATE,'YYYYMMDD')` |
| CPN0010001 | `selectMyPickDrinkChoicePromo` | `TO_DATE(FNSH_DT || '235959', ...)` |
| CPN0010001 | `selectMyPickDSalePromoList` | `TO_DATE(START_DT, 'YYYYMMDD')` 등 |
| MemberInfoDAO | `getMemberDelHistory` | `TRUNC(SYSDATE - 89)` |
| MemberInfoDAO | `selectAgreeVer` | `TO_DATE(... \|\| '000000', 'YYYYMMDDHH24MISS')` |

---

### 🟡 Warning — 개선 권고

#### 3.7 SQL ID 주석 누락 또는 불일치
**기준:** 모든 SQL에 `/* SQL_ID */` 형식 블록 주석 필수

| 파일 | 상태 |
|------|------|
| MEM0010001 | SQL ID 주석 없음 |
| ORD0010001 | 서브쿼리 내 `/* 킹오더 주문 */` 등 설명 주석은 있으나 SQL ID 주석 없음 |
| RIM0010001 | SQL ID 주석 없음 |
| CPN0010001 | SQL ID 주석 없음 |
| CCT0010001 | `:NO_STAMP_RECODE` (Oracle 스타일 바인드) 혼용 — `#{NO_STAMP_RECODE}` 로 통일 필요 |

---

#### 3.8 스칼라 서브쿼리 사용
**기준:** SELECT 절 스칼라 서브쿼리는 행마다 실행되므로 대용량 시 JOIN으로 변환 권고

| 파일 | 쿼리 ID | 위반 내용 |
|------|---------|---------|
| CPN0010001 | `selectMyPickDrinkChoicePromo` | SELECT 절 내 스칼라 서브쿼리 (이미지 URL 조회) |
| CPN0010001 | `selectMyPickDSalePromoList` | SELECT 절 내 스칼라 서브쿼리 (이미지 URL 조회) |
| MemberInfoDAO | 다수 SELECT | LISTAGG 서브쿼리 (SNS 목록 집계) — LEFT JOIN으로 구성됨 → 양호 |

**권장 대체:**
```sql
-- 스칼라 서브쿼리 → LEFT JOIN으로 변환
LEFT OUTER JOIN (
    SELECT A.ID_BIZ_KEY, B.DS_FILE_PATH
      FROM SYS_ATTACH_LINK A
      LEFT OUTER JOIN SYS_ATTACH B ON A.ID_ATTACH = B.ID_ATTACH
     WHERE A.TP_BIZ = 'COUPON_APP'
) IMG ON IMG.ID_BIZ_KEY = '0001'
```

---

#### 3.9 테이블 별칭이 의미 없거나 단순 알파벳 사용
**기준:** 단순 A, B, C 지양, 의미있는 대문자 약어 권장

| 파일 | 위반 내용 |
|------|---------|
| ORD0010001 | `FROM TBS_MENU TM, TBS_MENU TM2` — TM2는 의미가 불명확 |
| CPN0010001 | `A`, `B`, `S` 등 단순 알파벳 별칭 다수 |
| MemberInfoDAO | `A1`, `S` 등 단순 별칭 사용 |

---

#### 3.10 `WHERE 1=1` 패턴 사용
**기준:** 동적 SQL에서 관용적으로 허용되나 거버넌스 문서는 CTE + CASE WHEN 또는 정적 SQL 분리를 권고

| 파일 | 쿼리 ID | 위반 내용 |
|------|---------|---------|
| MemberInfoDAO | `getMemberDelHistory` | `WHERE 1=1` + 동적 AND 조건 |

---

#### 3.11 날짜 문자열 비교 — 인덱스 미사용 위험
**기준:** WHERE 절 컬럼에 함수 적용 금지 (인덱스 미사용)

| 파일 | 쿼리 ID | 위반 내용 |
|------|---------|---------|
| ORD0010006 | `getEtcAddMenuData` | `MP.START_DT <= TO_CHAR(SYSDATE,'YYYYMMDD')` — 날짜 문자열 비교로 타입 불일치 가능 |
| CPN0010001 | `selectMyPickDrinkChoicePromo` | `SYSDATE BETWEEN TO_DATE(START_DT, 'YYYYMMDD') AND ...` — 컬럼에 함수 적용 |

---

#### 3.12 `LISTAGG` 사용 (Oracle 전용 집계 함수)
**기준:** Oracle 전용 집계 함수 — 이식성 없음

| 파일 | 쿼리 ID | 위반 내용 |
|------|---------|---------|
| MemberInfoDAO | 회원 SELECT 공통 패턴 | `LISTAGG(A.TP_SNS,',') WITHIN GROUP (ORDER BY A.TP_SNS)` |

**권장 대체:**
- PostgreSQL: `STRING_AGG(col, ',' ORDER BY col)`
- MySQL: `GROUP_CONCAT(col ORDER BY col SEPARATOR ',')`
- 단기적으로 Oracle 고정 환경이면 허용 가능, 장기적으로 이식성 확보 시 수정 필요

---

#### 3.13 Oracle MERGE INTO 문법 — MySQL 미지원
**기준:** MySQL에서는 `MERGE` 미지원 → `INSERT ... ON DUPLICATE KEY UPDATE` 또는 `REPLACE INTO` 사용

| 파일 | 쿼리 ID | 상태 |
|------|---------|------|
| RIM0010001 | `saveMenuMst`, `saveMenuOmni`, `insertMenuCondiment`, `updateCoverMenuType` | Oracle MERGE INTO — Oracle 환경 전용 |
| RIM0010002 | `saveMenuPrc` | Oracle MERGE INTO — Oracle 환경 전용 |

**참고:** 파일명이 `*.oracle.xml`이므로 Oracle DB 전용임을 명시함. 거버넌스 기준 위반이나 의도적 분리로 볼 수 있음.

---

### 🟢 준수 사항 (양호)

| 항목 | 상태 |
|------|------|
| ANSI 명시적 JOIN 사용 | ✅ 대부분의 파일에서 `INNER JOIN ... ON`, `LEFT OUTER JOIN ... ON` 사용 |
| 바인드 변수 `#{...}` 사용 | ✅ 리터럴 직접 삽입 없이 MyBatis 바인드 변수 적용 |
| WHERE 없는 DML 없음 | ✅ UPDATE/DELETE 모두 WHERE 조건 포함 |
| MyBatis foreach 활용 | ✅ 동적 IN 절에 foreach 사용 |
| CASE WHEN 사용 | ✅ DECODE 대신 CASE WHEN 사용 |
| INSERT 컬럼 목록 명시 | ✅ INSERT INTO ... (col1, col2, ...) VALUES (...) 형식 준수 |
| 파일명 DB 구분 | ✅ `*.oracle.xml`, `*.mariadb.xml` 명시적 구분 |

---

## 4. 위반 건수 요약

| 심각도 | 항목 | 발견 건수 | 비고 |
|--------|------|---------|------|
| 🔴 Critical | SYSDATE 사용 | 13+ 개 쿼리 | Oracle 전용 |
| 🔴 Critical | NVL 사용 | 10+ 개 쿼리 | Oracle 전용 |
| 🔴 Critical | ROWNUM 사용 | 2 개 쿼리 | Oracle 전용 |
| 🔴 Critical | NEXTVAL FROM DUAL | 2 개 쿼리 | Oracle 전용 |
| 🔴 Critical | SELECT * | 1 개 쿼리 | |
| 🔴 Critical | TO_DATE / TO_CHAR | 10+ 개 쿼리 | Oracle 전용 |
| 🟡 Warning | SQL ID 주석 누락 | 전 파일 | |
| 🟡 Warning | 스칼라 서브쿼리 | 2 개 쿼리 | 대용량 시 성능 위험 |
| 🟡 Warning | 단순 테이블 별칭 | 다수 | |
| 🟡 Warning | WHERE 1=1 패턴 | 1 개 쿼리 | |
| 🟡 Warning | 날짜 문자열 비교 | 2+ 개 쿼리 | 인덱스 미사용 위험 |
| 🟡 Warning | LISTAGG | 1 개 쿼리 | Oracle 전용 집계 함수 |
| 🟡 Warning | Oracle MERGE INTO | 5 개 쿼리 | oracle.xml 의도적 분리 |

---

## 5. 개선 우선순위 및 권고사항

### 우선순위 1 (즉시 수정)
1. **`NVL` → `COALESCE`** 전체 치환 — 영향도 낮고 기계적 치환 가능
2. **`ROWNUM` → `FETCH FIRST n ROWS ONLY`** 치환

### 우선순위 2 (단계적 개선)
3. **`SYSDATE` → `CURRENT_TIMESTAMP` / `CURRENT_DATE`** 치환
   - INSERT의 감사 컬럼(REG_DATE, UPD_DATE)은 Java 애플리케이션에서 `LocalDateTime.now()` 바인드 변수로 처리하는 방식도 권장
4. **`TO_DATE` / `TO_CHAR`** 날짜 비교 → `DATE 'YYYY-MM-DD'` 표준 또는 바인드 변수로 전환
5. **SQL ID 주석** 전 파일 추가

### 우선순위 3 (아키텍처 검토)
6. **스칼라 서브쿼리 → LEFT JOIN** 전환 (CPN0010001 등 대용량 조회)
7. **`LISTAGG`** — 멀티 DB 지원 계획 시 DB별 분리 대응

### 현행 유지 가능 항목
- `MERGE INTO` — `*.oracle.xml` 파일에만 존재, Oracle DB 전용 의도적 분리이므로 현행 유지 가능
- `NEXTVAL FROM DUAL` — Oracle DB 고정 환경에서 단기 허용 가능

---

## 6. 참고: 파일명 DB 구분 체계 (현재 구조)

현재 To-Be 코드는 파일명으로 DB를 명시적으로 구분하고 있습니다:

| 확장자 패턴 | DB | 비고 |
|------------|-----|------|
| `*_DAO.oracle.xml` | Oracle DB | crm-api, bkr-comm 대부분 |
| `*_DAO.mariadb.xml` | MariaDB | PSH(푸시), CTT(일부), INF(일부) |
| `*_DAO.xml` | DB 무관 | bkr-core 시퀀스 등 |

이 체계는 거버넌스 문서의 "DBMS별 분리" 원칙에 부합하는 좋은 설계이나,  
`*.oracle.xml` 파일 내에서도 ANSI 표준 문법 사용 여부는 별개의 기준으로 적용되어야 합니다.
