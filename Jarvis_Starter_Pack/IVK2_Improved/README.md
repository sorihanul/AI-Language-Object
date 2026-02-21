# IVK2 Improved v0.1

Lightweight local search index for Obsidian-like vaults.

## Why this version
- No raw text in index (signature + tags + tiny lex sketch only)
- Incremental rebuild (mtime/size skip)
- SQLite compact storage + `vacuum`

## Commands

### Build index
```powershell
python F:\LLM\Jarvis_Starter_Pack\IVK2_Improved\ivk2_improved.py build F:\LLM\Jay_Publishing --db F:\LLM\Output\ivk2\index.sqlite
```

### Query
```powershell
python F:\LLM\Jarvis_Starter_Pack\IVK2_Improved\ivk2_improved.py query "프롬프트 설계 원칙" --db F:\LLM\Output\ivk2\index.sqlite -k 10
```

### Stats
```powershell
python F:\LLM\Jarvis_Starter_Pack\IVK2_Improved\ivk2_improved.py stats --db F:\LLM\Output\ivk2\index.sqlite
```

### Compact DB
```powershell
python F:\LLM\Jarvis_Starter_Pack\IVK2_Improved\ivk2_improved.py vacuum --db F:\LLM\Output\ivk2\index.sqlite
```

## Dual Profile (for large vault)
- guide: `DUAL_PROFILE.md`
- build script: `run_ivk2_dual_profile.bat`
- merged query command:
```powershell
python F:\LLM\Jarvis_Starter_Pack\IVK2_Improved\ivk2_improved.py query-dual "질문" --hot-db F:\LLM\Output\ivk2\hot.sqlite --cold-db F:\LLM\Output\ivk2\cold.sqlite -k 10
```

## Notes
- Intended for internal/local corpus search.
- For latest web facts, use web search separately.
