# DATA_TRACKING.md

## 1. 목적

Tracking System은 단순 로그 저장이 아니라,  
**사용자 행동 흐름(Journey)을 모델링하고 상태 전이를 해석하는 시스템**이다.

이 시스템의 목표는 다음과 같다:

- 사용자 행동의 시간 기반 연결 (Event → Journey)
- 행동 전이 구조 분석 (CTR, SR, CR, SHARE 등)
- 실험 / 분석 / 개인화 / 추천 시스템의 기반 데이터 제공
- 시스템 전반에서 사용하는 **횡단 관심사 (Cross-cutting concern)**

> Tracking은 로그가 아니라 “행동 흐름 모델”이다.

---

## 2. 아키텍처 정의

Tracking System은 단일 도메인이 아니라 다음 Subdomain으로 구성된다.

    Tracking System =
        Ingestion + Identity + Journey + Analytics

---

## 3. 패키지 구조

Tracking System은 기존 Hexagonal + DDD 구조를 그대로 따르며  
tracking은 특수 도메인으로 구성된다.

```
app
 ├ domains
 │   ├ tracking
 │   │   ├ ingestion
 │   │   │   ├ domain
 │   │   │   │   ├ entity
 │   │   │   │   ├ value_object
 │   │   │   │   └ service
 │   │   │   │
 │   │   │   ├ application
 │   │   │   │   ├ usecase
 │   │   │   │   ├ request
 │   │   │   │   └ response
 │   │   │   │
 │   │   │   ├ adapter
 │   │   │   │   ├ inbound
 │   │   │   │   │   └ api
 │   │   │   │   │
 │   │   │   │   └ outbound
 │   │   │   │       └ persistence
 │   │   │   │
 │   │   │   └ infrastructure
 │   │   │       ├ orm
 │   │   │       └ mapper
 │   │   │
 │   │   ├ identity
 │   │   │   ├ domain
 │   │   │   ├ application
 │   │   │   ├ adapter
 │   │   │   └ infrastructure
 │   │   │
 │   │   ├ journey
 │   │   │   ├ domain
 │   │   │   ├ application
 │   │   │   ├ adapter
 │   │   │   └ infrastructure
 │   │   │
 │   │   └ analytics
 │   │       ├ domain
 │   │       ├ application
 │   │       ├ adapter
 │   │       └ infrastructure
 │   │
 │   └ <domain_name>
 │       ├ domain
 │       │   ├ entity
 │       │   ├ value_object
 │       │   └ service
 │       │
 │       ├ application
 │       │   ├ usecase
 │       │   ├ request
 │       │   └ response
 │       │
 │       ├ adapter
 │       │   ├ inbound
 │       │   │   └ api
 │       │   │
 │       │   └ outbound
 │       │       ├ persistence
 │       │       └ external
 │       │
 │       └ infrastructure
 │           ├ orm
 │           └ mapper
 │
 ├ infrastructure
 │   ├ config
 │   ├ database
 │   ├ cache
 │   └ external
 │
 └ main.py
```

---

## 4. Subdomain 정의

### 4.1 Ingestion (Event 수집)

#### 역할

- Event 수신 (API)
- Event Schema 검증
- Event 저장 (Append-only)

#### MUST

- 모든 Event는 다음 필드를 포함해야 한다:
  - event_type
  - session_id
  - content_id
  - timestamp
- session_id 없는 Event 저장 금지
- content_id 없는 Event 저장 금지
- Event는 immutable (수정 금지)

#### 금지

- 상태 전이 수행 금지
- Journey 직접 수정 금지

---

### 4.2 Identity (식별)

#### 역할

- 사용자 식별 (Anonymous 포함)
- session_id 관리
- referral_id 관리

#### MUST

- user_id가 없을 경우 session_id를 사용자로 간주
- session_id는 클라이언트에서 생성
- 모든 Event는 session_id를 포함해야 한다

#### Share Tracking

- 공유 시 referral_id 생성
- 유입 시 referral_id 수집

---

### 4.3 Journey (핵심 Domain)

#### 역할

- Event를 시간 순으로 연결
- 사용자 행동 흐름 관리
- 상태 전이 관리

#### Aggregate

    Journey
    - session_id
    - events[]
    - current_stage

#### 상태 정의 (확장 가능)

    NONE → CLICK → SCROLL → CONVERT → SHARE

#### MUST

- 모든 Event는 Journey에 append 되어야 한다
- 상태 전이는 Journey에서만 수행된다
- 시간 순 재구성 가능해야 한다

#### 금지

- Ingestion에서 전이 판단 금지
- Application Layer에서 상태 직접 변경 금지

---

### 4.4 Analytics

#### 역할

- KPI 계산
- 퍼널 분석
- 행동 패턴 분석

#### KPI 예시

    CTR = click / impression
    SR  = scroll / click
    CR  = convert / scroll
    Share = share / convert

#### MUST

- KPI는 동일 session 기준으로 계산해야 한다
- 서로 다른 session 간 전이 분석 금지

---

## 5. Event 규칙

### Event Type (확장 가능)

- IMPRESSION
- CLICK
- SCROLL
- CONVERT
- SHARE
- LAND

### MUST

- Event는 append-only 구조
- Event는 immutable
- 시간 순 정렬 가능해야 한다

---

## 6. 책임 분리 규칙

    Frontend  → Event 생성 및 전송
    Backend   → Event 검증, 연결, 상태 해석

### MUST

- Frontend는 상태 전이를 판단하면 안 된다
- Backend는 Event 없이 상태를 변경하면 안 된다

---

## 7. 확장 원칙

Tracking System은 다음 방향으로 확장 가능해야 한다:

- User 기반 분석 (로그인 도입 시)
- 추천 시스템
- 실시간 스트림 처리 (Kafka 등)
- A/B 테스트 시스템
- 개인화 엔진

### MUST

- Event Schema는 하위 호환성을 유지해야 한다
- Journey 모델은 확장 가능해야 한다
- Subdomain 간 결합은 최소화해야 한다

---

## 8. 금지 사항

다음은 절대 허용되지 않는다:

- 단순 로그 저장 시스템으로 구현
- Event를 독립적으로만 저장하는 구조
- session_id 없이 Event 저장
- content_id 없이 Event 저장
- 상태 전이를 여러 계층에서 수행하는 구조

---

## 9. 최종 원칙

- Event를 쌓지 말고 Journey를 구성하라
- 로그를 저장하지 말고 행동 흐름을 모델링하라
- Tracking은 기능이 아니라 시스템이다
- Tracking은 분석이 아니라 해석이다