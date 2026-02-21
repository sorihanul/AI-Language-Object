# IVK2 Dual Profile (Hot/Cold)

## Purpose
대용량 볼트에서 인덱스와 검색 성능을 안정화하기 위한 이중 인덱스 운용.

- Hot: 최근 변경 파일 (예: 30일 이내)
- Cold: 장기 보관 파일 (예: 30일 초과)

## Build (one command)
```powershell
F:\LLM\Jarvis_Starter_Pack\IVK2_Improved\run_ivk2_dual_profile.bat F:\LLM\YourVault 30
```

## Query merged results
```powershell
python F:\LLM\Jarvis_Starter_Pack\IVK2_Improved\ivk2_improved.py query-dual "질문" --hot-db F:\LLM\Output\ivk2\hot.sqlite --cold-db F:\LLM\Output\ivk2\cold.sqlite -k 10
```

## Notes
- hot 결과에 기본 가중치(1.08)를 준다.
- 필요하면 `--hot-weight`로 조정한다.
- 저장 용량이 커지면 `vacuum`으로 압축한다.
