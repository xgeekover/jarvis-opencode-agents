---
name: spring-boot-reviewer
description: Review Spring Boot code for layered-architecture violations, transaction boundaries, DTO/entity leakage, SOLID, error handling and tests. Use after writing or changing controllers, services, or repositories.
---

# Spring Boot Reviewer

Review the target Java code against the project's own backend conventions. Read the project's rules first (`AGENTS.md`, architecture or API-contract docs). The checklist below is the default; follow the project's rules where they differ.

## Checklist
1. 레이어 준수: Controller → Service → Repository → Domain 순서를 지키는가. Controller가 Repository를 직접 호출하거나 비즈니스 로직을 담고 있지 않은가.
2. 트랜잭션 경계: @Transactional이 Service 계층에 올바르게 선언됐는가. 읽기 전용 메서드에 readOnly=true가 붙어 있는가. 트랜잭션 범위가 필요 이상으로 넓지 않은가.
3. DTO/엔티티 분리: 컨트롤러가 엔티티를 직접 요청/응답으로 노출하지 않고 DTO(예: Java record)를 쓰는가.
4. SOLID: 서비스가 비대해지지 않았는가(SRP). 의존성이 인터페이스를 향하는가(DIP).
5. 예외 처리: 프로젝트가 정한 에러 응답 규약(프로젝트의 API 계약 문서, 또는 RFC 9457 Problem Details)을 따르는가. 예외를 삼키지 않는가.
6. 테스트: JUnit 5 + Mockito 단위 테스트, 필요 시 @SpringBootTest 통합 테스트가 있는가.

## Output
심각도순으로 file:line + 문제 + 수정안을 보고한다. 프로젝트 규칙에 심각도 기준이 있으면 그것을 따르고, 없으면 레이어 위반은 high로 취급한다.
