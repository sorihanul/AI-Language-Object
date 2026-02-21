@echo off
setlocal
if "%~1"=="" (
  echo Usage: run_ivk2_dual_profile.bat ROOT_PATH [HOT_DAYS]
  exit /b 1
)
set ROOT=%~1
set HOT_DAYS=%~2
if "%HOT_DAYS%"=="" set HOT_DAYS=30

python F:\LLM\Jarvis_Starter_Pack\IVK2_Improved\ivk2_improved.py build "%ROOT%" --db F:\LLM\Output\ivk2\hot.sqlite --mtime-days-max %HOT_DAYS%
python F:\LLM\Jarvis_Starter_Pack\IVK2_Improved\ivk2_improved.py build "%ROOT%" --db F:\LLM\Output\ivk2\cold.sqlite --mtime-days-min %HOT_DAYS%

echo Done. hot/cold indexes built.
endlocal
