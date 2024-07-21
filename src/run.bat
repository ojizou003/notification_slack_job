@REM run.bat

@echo off

cd /d %~dp0

conda activate n_slack_nj & python main.py & python deactivate
