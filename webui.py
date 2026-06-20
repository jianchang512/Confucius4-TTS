import sys
import time,os,requests
import tempfile
from pathlib import Path

ROOT_DIR=str(Path(__file__).parent.as_posix())
os.environ['HF_HOME'] = ROOT_DIR + "/checkpoints"
os.environ['HF_HUB_CACHE'] = ROOT_DIR + "/checkpoints"
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = 'true'
os.environ['HF_HUB_DOWNLOAD_TIMEOUT'] = "3600"
os.environ["HF_HUB_DISABLE_XET"] = "1"
os.environ['PATH'] = ROOT_DIR + os.pathsep + f'{ROOT_DIR}/tools'

try:
    requests.head('https://huggingface.co', timeout=5)
except:
    os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
    print(f'无法连接 huggingface.co, 使用国内镜像 hf-mirror.com 下载模型')
    
import gradio as gr
import torch
import torchaudio
sys.path.insert(0, ROOT_DIR)
from confuciustts.cli.inference import ConfuciusTTS


DEFAULT_TEXT = "网易Confucius4-TTS 多语言跨语种TTS"

LANGUAGE_CHOICES = [
    "zh", "en", "ja", "ko", "de", "fr", "th", 
    "id", "vi", "es", "pt", "it", "ru", "ms"
]

# 1. 全局初始化模型
print("Initializing ConfuciusTTS model...")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = ConfuciusTTS(
    config_path='config/inference_config.yaml',
    device=device,
)
print(f"Model loaded successfully. sample_rate={model.sample_rate}")


# 2. 推理函数
def synthesize_audio(ref_aud, text, lang):
    """
    接收来自前端的参数并调用模型合成语音
    """
    if not ref_aud:
        raise gr.Error("请上传参考音频 (Please upload a reference audio).")
    if not text.strip():
        raise gr.Error("请输入要合成的文本 (Please enter text to synthesize).")
        
    print(f"Generating TTS | Lang: {lang} | Text: {text}")
    t0 = time.time()
    
    # generate() 方法接收的是文件的路径字符串 (Gradio 设置了 type="filepath")
    audio = model.generate(text, lang, ref_aud, verbose=True)
    print(f"Generated in {time.time() - t0:.3f}s, shape={tuple(audio.shape)}")
    
    # 将输出音频保存到临时目录以便前端界面播放
    temp_dir = tempfile.mkdtemp()
    output_path = str(Path(temp_dir) / "output.wav")
    torchaudio.save(output_path, audio.cpu(), model.sample_rate)
    print(f"Saved generated audio to {output_path}")
    
    return output_path


# 3. 搭建并渲染 Gradio 前端页面
with gr.Blocks(title="Confucius4-TTS", theme=gr.themes.Soft()) as demo:
    gr.Markdown("<h1 style='text-align: center;'>Confucius4-TTS Zero-Shot Synthesis</h1>")
    
    with gr.Row():
        # 左侧输入区域
        with gr.Column(scale=1):
            # type="filepath" 会确保直接传递音频的文件路径给后端函数
            ref_aud = gr.Audio(label="Reference Audio / 参考音频", type="filepath")
            text = gr.Textbox(label="Text / 文本", value=DEFAULT_TEXT, lines=4)
            # 使用截图中的名称 "Language / 语种" 和对应的语种代码数组
            lang = gr.Dropdown(choices=LANGUAGE_CHOICES, label="Language / 语种", value="zh")
            
            submit_btn = gr.Button("Generate / 合成", variant="primary")
            
        # 右侧输出区域
        with gr.Column(scale=1):
            output_audio = gr.Audio(label="Output Audio / 生成音频", type="filepath", interactive=False)
            
    # 4. 绑定点击事件，并开放 api_name 以支持 API 远程调用
    submit_btn.click(
        fn=synthesize_audio,
        inputs=[ref_aud, text, lang],
        outputs=[output_audio],
        api_name="_clone_fn"  # 暴露出可以通过 /run/synthesize 这个 API Endpoint 调用
    )


if __name__ == "__main__":
    # 启动 Gradio 服务
    demo.launch(server_name="0.0.0.0", server_port=7860)