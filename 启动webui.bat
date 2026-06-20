@echo off
chcp 65001

title 网易Confucius4-TTS 整合包 0621 --by pyvideotrans.com

set https_proxy=http://127.0.0.1:10808

rem 如果你能科学上网并且速度较快，可删掉下方这行，直接从外网源站下载模型
set NO_PROXY=localhost,127.0.0.1,api.gradio.app
set GRADIO_ANALYTICS_ENABLED=False

echo 开始启动,用时可能较久，请耐心等待...
echo.

call runtime\python webui.py

pause