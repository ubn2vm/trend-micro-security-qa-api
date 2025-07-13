# -*- coding: utf-8 -*-
import gradio as gr
import requests
import threading
import time

API_URL = "http://localhost:8000/ask"

# 建議問題清單
SUGGESTED_QUESTIONS = [
    "Trend Vision One CREM 解決方案的主要目標是什麼？",
    "CREM 如何幫助安全團隊獲得更全面的風險視圖？",
    "CREM 如何整合不同的安全領域？",
    "CREM 如何利用「威脅情報」和「AI」來提供其宣稱的「無與倫比的風險情報優勢」？"
]

# 儲存對話歷史
chat_history = []

# 問答主函式，支援 loading 與超時提示

def ask_ai(question, history, status_box):
    if not question.strip():
        return history, "", gr.update(interactive=True), ""
    answer = ""
    status = ""
    done = threading.Event()
    result = {}

    def fetch():
        try:
            response = requests.post(API_URL, json={"question": question}, timeout=10)
            if response.status_code == 200:
                result["answer"] = response.json().get("answer", "[無回應]")
            else:
                result["answer"] = f"[API 錯誤] 狀態碼: {response.status_code}"
        except Exception as e:
            result["answer"] = f"[連線失敗] {str(e)}"
        finally:
            done.set()

    thread = threading.Thread(target=fetch)
    thread.start()
    # 3 秒內沒回應顯示提示
    for _ in range(30):
        if done.is_set():
            break
        time.sleep(0.1)
    if not done.is_set():
        status = "AI 正在思考，請稍候..."
    thread.join()
    answer = result.get("answer", "[無回應]")
    history.append((question, answer))
    return history, "", gr.update(interactive=True), status

def clear_history():
    return [], "", gr.update(interactive=True), ""

def fill_suggestion(s, history, status_box):
    # 點擊建議問題時自動填入輸入框
    return history, s, gr.update(interactive=True), ""

custom_css = """
.gradio-container {
    font-family: 'Noto Sans TC', 'Montserrat', 'Segoe UI', 'Arial', sans-serif;
    background: #fff !important;
}
.main-header {
    background: #fff;
    color: #111;
    border-radius: 12px;
    padding: 32px 24px 18px 24px;
    margin-bottom: 24px;
}
.main-header h1 {
    font-family: 'Noto Sans TC', 'Montserrat', 'Segoe UI', 'Arial', sans-serif;
    font-weight: 900;
    font-size: 2.6em;
    letter-spacing: 2px;
    color: #111;
    margin-bottom: 12px;
}
.main-header p {
    font-family: 'Noto Sans TC', 'Montserrat', 'Segoe UI', 'Arial', sans-serif;
    font-weight: 400;
    font-size: 1.15em;
    color: #222;
    letter-spacing: 1px;
}
.chat-label, .custom-label {
    background: #fff;
    color: #D71920;
    border: 2px solid #D71920;
    padding: 7px 18px;
    border-radius: 12px;
    font-weight: bold;
    font-size: 15px;
    display: inline-block;
    margin-bottom: 10px;
    box-shadow: 0 2px 8px rgba(215, 25, 32, 0.08);
    letter-spacing: 1px;
}
.gr-chatbot {
    min-height: 80px !important;
    max-height: 400px !important;
    height: auto !important;
    overflow-y: auto !important;
    border-radius: 12px !important;
    border: 1.5px solid #D71920 !important;
    box-shadow: 0 2px 8px rgba(215, 25, 32, 0.08);
}
.svelte-bnzux8, .svelte-1svsvh2, .svelte-g3p8na, .svelte-gj7l6, .gr-column {
    height: auto !important;
    min-height: 0 !important;
    max-height: none !important;
    flex: unset !important;
}
.suggestion-box {
    background: #111;
    border-radius: 12px;
    padding: 18px 18px 10px 18px;
    margin-top: 18px;
    display: flex;
    gap: 0;
    align-items: center;
}
.suggestion-box h4 {
    color: #fff;
    margin: 0 18px 0 0;
    font-weight: bold;
    font-size: 16px;
    letter-spacing: 1px;
}
.suggestion-btn {
    background: #111 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: bold !important;
    font-size: 15px !important;
    margin: 0 0 0 0 !important;
    padding: 10px 24px !important;
    letter-spacing: 1px;
    border-right: 1px solid #eee !important;
    transition: background 0.2s, color 0.2s;
}
.suggestion-btn-active {
    background: #D71920 !important;
    color: #fff !important;
}
.suggestion-btn:last-of-type {
    border-right: none !important;
}
.gradio-button {
    background: #D71920 !important;
    color: #fff !important;
    border-radius: 12px !important;
    font-weight: bold !important;
    font-size: 16px !important;
    letter-spacing: 1px;
    border: none !important;
    padding: 12px 32px !important;
    transition: background 0.2s, color 0.2s;
}
.gradio-button:hover {
    background: #111 !important;
    color: #fff !important;
}
.clear-button {
    background: #111 !important;
    color: #fff !important;
    border-radius: 12px !important;
    font-weight: bold !important;
    font-size: 16px !important;
    letter-spacing: 1px;
    border: none !important;
    padding: 12px 32px !important;
    transition: background 0.2s, color 0.2s;
}
.clear-button:hover {
    background: #D71920 !important;
    color: #fff !important;
}
.textbox-container {
    border: 2px solid #D71920 !important;
    border-radius: 12px !important;
    background: #fff !important;
}
.textbox-container:focus-within {
    border-color: #111 !important;
    box-shadow: 0 0 0 2px rgba(17, 17, 17, 0.08) !important;
}
.status-box {
    color: #D71920;
    font-size: 14px;
    font-weight: bold;
    margin-top: 8px;
    min-height: 20px;
    letter-spacing: 1px;
}
"""

with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as demo:
    gr.HTML("""
        <div class="main-header">
            <h1 style="color: #111;">趨勢科技CREM智能問答</h1>
            <p style="color: #222;">基於 AI 技術的CREM產品資訊平台</p>
        </div>
    """)
    # 狀態：目前選中的建議問題 index
    selected_suggestion_idx = gr.State(-1)
    # 先建立建議問題按鈕，暫存到 list
    suggestion_btns = []
    with gr.Row() as suggestion_row:
        gr.HTML('<div class="suggestion-box"><h4>建議問題</h4></div>')
        for i, q in enumerate(SUGGESTED_QUESTIONS):
            btn = gr.Button(q, elem_id=f"suggestion-btn-{i}", elem_classes=["suggestion-btn"])
            suggestion_btns.append(btn)
    with gr.Column():
        gr.HTML('<div class="chat-label">對話歷史</div>')
        chatbot = gr.Chatbot(
            show_label=False,
            container=True,
            bubble_full_width=False,
            min_height=80,
            max_height=400
        )
        with gr.Row():
            gr.HTML('<div class="custom-label">請輸入您的資安問題</div>')
            msg = gr.Textbox(
                placeholder="例如：什麼是CREM？",
                lines=3,
                scale=4,
                container=True,
                show_label=False
            )
            submit_btn = gr.Button("發送", variant="primary", scale=1, elem_classes=["gradio-button"])
        status_box = gr.HTML("", elem_classes=["status-box"])
        with gr.Row():
            clear_btn = gr.Button("清除對話記錄", variant="secondary", elem_classes=["clear-button"])
            gr.HTML("<div style='text-align: center; color: #D71920; font-size: 12px; font-weight: bold; margin-top: 10px;'>Powered by Google Gemini API</div>")
    # 互動元件都定義好後，再掛事件
    def update_suggestion_btns(idx):
        # 依據 idx 動態更新按鈕 class
        btn_updates = []
        for i in range(len(SUGGESTED_QUESTIONS)):
            if idx >= 0 and i == idx:
                btn_updates.append(gr.update(elem_classes=["suggestion-btn", "suggestion-btn-active"]))
            else:
                btn_updates.append(gr.update(elem_classes=["suggestion-btn"]))
        return btn_updates
    for i, btn in enumerate(suggestion_btns):
        def on_suggestion_click(idx=i):
            def inner(history, msg_val, submit_btn_val, status_box_val, selected_idx):
                # 點擊時更新 index 並填入輸入框
                return [
                    *([history, SUGGESTED_QUESTIONS[idx], submit_btn_val, status_box_val] + update_suggestion_btns(idx)),
                    idx
                ]
            return inner
        btn.click(
            on_suggestion_click(i),
            inputs=[chatbot, msg, submit_btn, status_box, selected_suggestion_idx],
            outputs=[chatbot, msg, submit_btn, status_box] + suggestion_btns + [selected_suggestion_idx]
        )

    # 事件處理
    submit_btn.click(
        ask_ai,
        inputs=[msg, chatbot, status_box],
        outputs=[chatbot, msg, submit_btn, status_box],
        show_progress=True
    )
    msg.submit(
        ask_ai,
        inputs=[msg, chatbot, status_box],
        outputs=[chatbot, msg, submit_btn, status_box],
        show_progress=True
    )
    clear_btn.click(
        clear_history,
        outputs=[chatbot, msg, submit_btn, status_box]
    )

demo.launch(
    server_name="127.0.0.1",
    server_port=7860,
    share=False,
    show_error=True
)