# 테스트 전략 (쉽게 정리)

## 우리가 확인하려는 것
- 작은 단위(유닛/슬라이스)에서 바로 실패를 잡는다.
- 정말 중요한 흐름만 통합 테스트로 확인한다.
- 배포 직후에 살아있는지(스모크) 꼭 본다.
- Gradle 태스크를 `test`(빠른 것) / `integrationTest`(통합)로 나눠서 실수 줄인다.

## 어떤 테스트를 돌리는지
### 백엔드(Spring Boot)
- **서비스 유닛(Mock)**: 돈/주식 계산, 토큰 만료·검증 같은 로직을 가짜 리포지토리로 확인.
- **리포지토리 슬라이스(@DataJpaTest)**:
  - 거래 조회: 사용자/종목 필터, 최근순 정렬, DTO 매핑이 맞는지.
  - 종목 조회: 날짜 필터+페이지, 티커 검색이 맞는지.
- **컨트롤러 슬라이스(@WebMvcTest)**: `/api/accounts/holdings/{ticker}`에 대해
  - 잘못된 요청이면 400, 토큰 없으면 401, 권한 없으면 403, 정상은 200.
- **통합(Testcontainers, 딱 2~3개)**:
  - 로그인→토큰 재발급.
  - 주문 생성/취소 happy path.
  - 테스트용 MySQL/Redis 컨테이너, 최소 샘플 데이터.

### 프론트엔드(최소)
- 상태관리 1~2개, 로그인 폼 검증 정도만 단위 테스트. 나머지는 스모크/E2E로 대체 가능.

### 스모크(배포 직후)
- `/actuator/health`, 핵심 API 2~3개 200, 프론트 `/` 200, 가능하면 WebSocket 첫 메시지 수신.
- 실패하면: 컨테이너 로그를 보고 롤백할지 결정(자동 아니어도 기준은 적어둔다).

## Gradle은 이렇게 나눈다
- `test`: 유닛 + 슬라이스만.
- `integrationTest`: 통합만(별도 소스세트나 JUnit Tag로 분리).
- 의존성 예시: `org.testcontainers:mysql`, `org.testcontainers:junit-jupiter` (+ Redis 필요 시 추가).
- 실행 예시: `./gradlew test`, `./gradlew integrationTest`

## Jenkins는 이렇게 돈다
1) Unit Tests: `./gradlew test` (빠른 실패)
2) Integration Tests: `./gradlew integrationTest` (DB/Redis 필요, master 배포 전 필수 권장)
3) Build: 빌드/이미지 생성
4) Deploy: 기존 배포 단계
5) Smoke: `scripts/health-check.sh` 확장본 실행, 실패 시 로그 확인·롤백 기준 적용

## 현실 운영 팁
- 통합이 느리면: 스테이징까지 자동, 프로덕션은 수동 승인.
- 무거운 Spark/Python 테스트는 야간이나 별도 파이프라인으로.
- `-Djunit.jupiter.tags=`로 나눠도 되지만, 실제 운영에선 태스크 분리가 더 안전하다.
