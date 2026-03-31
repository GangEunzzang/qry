# TODOS

## P2 — 결과 페이징/스트리밍

**What:** 쿼리 결과를 메모리에 전체 로드하지 않고 페이징 또는 스트리밍 방식으로 처리
**Why:** 현재 결과가 메모리에 전체 복사됨. 10만 행 이상이면 메모리/성능 문제 발생 (Codex outside voice에서 지적)
**Pros:** 대용량 결과 처리 가능, 메모리 예산 준수, UX 개선 (즉각 첫 결과 표시)
**Cons:** 어댑터 인터페이스 변경 필요, 정렬/필터 로직 복잡도 증가
**Context:** widget_results.py에서 _all_rows에 전체 복사 후 정렬/필터. Textual DataTable의 가상 스크롤 활용 가능.
**Effort:** L (human) → M (CC)
**Priority:** P2
**Depends on:** PR #1 머지 후

## P2 — PostgreSQL/MySQL 통합 테스트

**What:** Docker compose로 PostgreSQL/MySQL 테스트 DB 구성 + CI에서 실제 DB 연결 테스트
**Why:** 현재 비-SQLite 테스트가 mock 기반. 실제 DB 없이 멀티 DB 지원을 보장할 수 없음 (Codex outside voice에서 지적)
**Pros:** 실제 DB 동작 검증, 어댑터 버그 조기 발견, PR #2 Table Workbench 품질 보장
**Cons:** CI 시간 증가, Docker 의존성 추가
**Context:** tests/domains/database/test_postgres.py와 test_mysql.py가 mock 기반. pytest-docker 또는 testcontainers-python 사용 가능.
**Effort:** M (human) → S (CC)
**Priority:** P2
**Depends on:** 없음

## P3 — error_position 어댑터 구현

**What:** 각 DB 어댑터에서 SQL 에러 발생 시 error_position 필드를 채우도록 구현
**Why:** QueryResult에 error_position 필드가 있고 에디터에서 표시할 수 있지만, 어댑터가 실제로 값을 채우지 않음 (Codex outside voice에서 지적)
**Pros:** 정확한 에러 위치 표시, 개발자 UX 대폭 향상
**Cons:** DB별 에러 메시지 파싱이 필요 (SQLite/PostgreSQL/MySQL 각각 다른 포맷)
**Context:** shared/models.py:21에 error_position 정의, widget_editor.py:199에서 표시 로직 존재. sqlite.py:64, postgres.py:79, mysql.py:80에서 구현 필요.
**Effort:** M (human) → S (CC)
**Priority:** P3
**Depends on:** 없음
