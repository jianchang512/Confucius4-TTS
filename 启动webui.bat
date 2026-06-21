@echo off
chcp 65001

title 网易Confucius4-TTS 整合包 0621 --by pyvideotrans.com

set NO_PROXY=localhost,127.0.0.1,api.gradio.app
set GRADIO_ANALYTICS_ENABLED=False

echo.

call runtime\python webui.py

pause