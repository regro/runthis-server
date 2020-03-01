@echo off
call :s_which py.exe
if not "%_path%" == "" (
  py -3 -m runthis.server %*
) else (
  python -m runthis.server %*
)

goto :eof

:s_which
  setlocal
  endlocal & set _path=%~$PATH:1
  goto :eof
