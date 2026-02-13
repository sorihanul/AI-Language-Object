# AILO-H Memory Garbage Collector Protocol (MGC-P) v1.0 (PUBLIC)

## 1. 개요 (Overview)
본 프로토콜은 `AILO-H v1.0`의 **Autonomous Memory** 시스템에서 발생하는 데이터 엔트로피(무질서도)를 관리하기 위한 표준 절차이다. '스스로 진화하는 AI'는 필연적으로 대량의 시도(Trial)와 실패(Failure) 데이터를 생성하므로, 인지 부하인 **"Cognitive Mass"**를 최적화된 상태로 유지해야 한다.

## 2. 데이터 등급 및 보존 정책 (Retention Rules)

가비지 컬렉터(GC)는 각 메모리 항목(Entry)의 **Score(유용성 점수)**와 **Age(생성 경과 시간)**를 기준으로 생존 여부를 결정한다.

| 등급 (Tier) | 점수 범위 (Score) | 보존 정책 (Policy) | 비고 |
| :--- | :--- | :--- | :--- |
| **Platinum** | `0.95 <= Score <= 1.0` | **Forever (영구 보존)** | 시스템의 핵심 자산 (Best Practices) |
| **Gold** | `0.90 <= Score < 0.95` | **30 Days (한달 보존)** | 우수한 참조 자료, 주기적 압축 대상 |
| **Silver** | `0.80 <= Score < 0.90` | **7 Days (일주일 보존)** | 단기 기억, 반복 패턴 발견 시 승격 가능 |
| **Noise** | `Score < 0.80` | **Purge (즉시/24h 삭제)** | 실패한 시도, 잘못된 추론 |

## 3. 실행 프로세스 (Execution Cycle)

1.  **Load**: `auto_mined.jsonl` 파일을 로드한다.
2.  **Scan**: 각 라인(JSON 객체)의 `score`와 `ts`(Timestamp) 필드를 파싱한다.
3.  **Evaluate**:
    *   현재 시간(`NOW`)과 `ts`의 차이를 계산하여 `Age`를 도출한다.
    *   `Score`에 따른 등급을 판정한다.
    *   보존 정책 위반 시 `DELETE` 마킹한다.
4.  **Action**:
    *   삭제 대상이 아닌 항목들만 임시 리스트에 담는다.
    *   `auto_mined.jsonl`을 덮어쓰기(Overwrite)한다.
5.  **Report**: 삭제된 항목 수와 확보된 용량을 로그로 남긴다.
    *   Public-friendly log path: `f:\LLM\Output\Jarvis_Starter_Pack\gc_report.log`

## 4. 예외 처리 (Exceptions)
*   **Manual Override**: `keep_forever: true` 플래그가 있는 항목은 점수와 무관하게 보존한다.
*   **Format Error**: 파싱 불가능한 라인(Corrupted Data)은 별도 `corrupted.dump` 파일로 이동 후 메인 파일에서 제거한다.

## 5. 트리거 (Trigger)
*   **Night Owl Workflow**: 매주 정기 점검 시 실행.
*   **Disk Constraint**: 디스크 용량 부족 경고(Red Alert) 시 긴급 실행.
*   **Command**: `/gc` 명령어로 수동 실행.

