# -*- coding: utf-8 -*-
import gradio as gr
import requests
import threading
import time
import os
import re

API_URL = os.getenv("API_URL", "http://localhost:8000/ask")

# 建議問題清單
SUGGESTED_QUESTIONS = [
    "什麼是 Virtual Analyzer？它在 Deep Discovery Inspector (DDI) 中扮演什麼角色？",
    "匯入至 Deep Discovery Inspector 內部 Virtual Analyzer 的自訂 OVA 映像檔，其檔案大小限制為何？",
    "Suricata 如何支援 JA3 和 JA4 指紋識別？如何在配置中啟用它們？"
]

# 儲存對話歷史
chat_history = []

# 動態 Prompt 模板
ENHANCED_PROMPT_TEMPLATE = """
你是一個趨勢科技資安技術專家，專門回答關於網路安全的問題。

系統資訊：您正在使用一個完整的知識庫系統，基於檢索到的相關資料進行分析。

基於以下檢索到的相關資料，準確回答用戶的問題：

=== 檢索結果 ({result_count}個結果) ===
{context}

=== 用戶問題 ===
{question}

=== 回答指導原則 ===
1. **充分利用檢索結果**: 基於提供的{result_count}個檢索結果進行全面分析
2. **表格數據判斷**: 仔細檢查檢索結果，只有當內容明確包含數字、統計、百分比、排名等具體數據時才提供數據洞察
3. **專業術語準確**: 正確使用網路安全等專業術語
4. **結構化回答**: 提供清晰的摘要和詳細說明
5. **來源透明**: 在文末簡潔列出主要資料來源

=== 回答格式要求 ===
**📋 摘要**
[簡潔摘要，突出核心要點]

**🔍 詳細分析**
[基於檢索結果的詳細分析和解釋]

**💡 關鍵發現**
- [要點1]
- [要點2] 
- [要點3]

**📊 數據洞察** (重要：只有當檢索結果包含明確的數字統計、表格數據、百分比、排名等具體數據時才包含此部分，否則完全跳過)
[整理相關統計和表格資料]

**📚 資料來源**
[簡潔列出主要資料來源文件名稱]

重要提醒：如果檢索結果沒有包含具體的統計數據、數字或表格內容，請完全省略「📊 數據洞察」部分，直接從「💡 關鍵發現」跳到「📚 資料來源」。

請開始回答：
"""

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
            response = requests.post(API_URL, json={"question": question}, timeout=15)
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "[無回應]")
                citations = data.get("citations", [])
                
                # ✅ 調試：打印收到的數據
                print(f"Debug - Citations received: {len(citations)} items")
                print(f"Debug - Answer length: {len(answer)} characters")
                print(f"Debug - Answer contains '📋 摘要': {'📋 摘要' in answer}")
                print(f"Debug - Answer contains '📚 資料來源': {'📚 資料來源' in answer}")
                print(f"Debug - Answer contains '```': {'```' in answer}")
                print(f"Debug - Answer preview (first 500 chars):\n{answer[:500]}")
                
                # ✅ 保存原始答案（用於調試）
                original_answer = answer
                
                # ✅ 修改檢查條件：總是添加詳細的引用信息
                if citations:
                    # 檢查是否LLM回答已經包含詳細的資料來源（有代碼塊）
                    has_detailed_sources = "📚 資料來源" in answer and "```" in answer
                    
                    # 只有在沒有詳細引用時才添加
                    if not has_detailed_sources:
                        # 檢查是否LLM回答已經包含簡單的資料來源
                        has_simple_sources = "📚 資料來源" in answer
                        
                        if has_simple_sources:
                            # 如果有簡單資料來源，替換為詳細版本
                            # 先找到 "📚 資料來源" 的位置，保留之前的內容（包括摘要）
                            source_index = answer.find("📚 資料來源")
                            if source_index > 0:
                                # 保留摘要等內容，替換資料來源部分
                                # 確保保留完整的摘要、詳細分析等內容
                                answer_before_source = answer[:source_index].rstrip()
                                print(f"Debug - Found '📚 資料來源' at index {source_index}")
                                print(f"Debug - Content before source (first 300 chars):\n{answer_before_source[:300]}")
                                print(f"Debug - Content before source contains '📋 摘要': {'📋 摘要' in answer_before_source}")
                                
                                # ✅ 確保摘要沒有被移除
                                if "📋 摘要" not in answer_before_source and "📋 摘要" in original_answer:
                                    print("⚠️ WARNING: 摘要可能在替換過程中被移除了！")
                                    # 嘗試從原始答案中恢復摘要
                                    original_summary_index = original_answer.find("📋 摘要")
                                    if original_summary_index >= 0:
                                        # 找到摘要的結束位置（下一個主要部分）
                                        next_section = original_answer.find("🔍 詳細分析", original_summary_index)
                                        if next_section == -1:
                                            next_section = original_answer.find("💡 關鍵發現", original_summary_index)
                                        if next_section == -1:
                                            next_section = source_index
                                        
                                        if next_section > original_summary_index:
                                            summary_section = original_answer[original_summary_index:next_section].strip()
                                            # 如果 answer_before_source 中沒有摘要，添加回去
                                            if "📋 摘要" not in answer_before_source:
                                                answer_before_source = summary_section + "\n\n" + answer_before_source
                                
                                answer = answer_before_source + "\n\n" + "─" * 50 + "\n" + "📚 **資料來源與引用**\n\n"
                            else:
                                # 如果找不到資料來源標記，直接添加
                                answer += "\n\n" + "─" * 50 + "\n"
                                answer += "📚 **資料來源與引用**\n\n"
                        else:
                            # 如果完全沒有資料來源，添加
                            answer += "\n\n" + "─" * 50 + "\n"
                            answer += "📚 **資料來源與引用**\n\n"
                    
                    # ✅ 最終檢查：確保摘要還在
                    if "📋 摘要" in original_answer and "📋 摘要" not in answer:
                        print("⚠️ ERROR: 摘要在處理過程中被移除了！恢復原始答案中的摘要...")
                        # 從原始答案中提取摘要部分
                        summary_start = original_answer.find("📋 摘要")
                        if summary_start >= 0:
                            # 找到摘要的結束位置
                            next_section = original_answer.find("🔍 詳細分析", summary_start)
                            if next_section == -1:
                                next_section = original_answer.find("💡 關鍵發現", summary_start)
                            if next_section == -1:
                                next_section = original_answer.find("📚 資料來源", summary_start)
                            
                            if next_section > summary_start:
                                summary_section = original_answer[summary_start:next_section].strip()
                                # 在答案開頭插入摘要
                                answer = summary_section + "\n\n" + answer
                    
                    # 只有在沒有詳細引用時才添加
                    if "```" not in answer:
                        # 去重並顯示引用內容
                        seen_sources = set()
                        for citation in citations:
                            source_file = citation.get("source", "unknown")
                            content = citation.get("content", "")
                            content_type = citation.get("content_type", "text")
                            
                            if source_file not in seen_sources:
                                seen_sources.add(source_file)
                                
                                # 獲取 metadata（如果可用）
                                citation_metadata = citation.get("metadata", {})
                                
                                # 顯示文件名（不顯示頁碼）
                                type_emoji = "📄" if content_type == "text" else "📊"
                                answer += f"**{type_emoji} {source_file}**\n"
                                
                                # 清理引用內容：使用 TextProcessor 進行完整清理
                                try:
                                    from core_app.rag.processors.text_processor import TextProcessor
                                    text_processor = TextProcessor()
                                    cleaned_content = text_processor.clean_citation_content(content)
                                except Exception as e:
                                    # 如果導入失敗，使用簡單的清理方法
                                    cleaned_content = content.strip()
                                    
                                    # 移除開頭的單個點號或奇怪的格式字符
                                    if cleaned_content.startswith('.'):
                                        cleaned_content = cleaned_content[1:].strip()
                                    if cleaned_content.startswith('。'):
                                        cleaned_content = cleaned_content[1:].strip()
                                    
                                    # 修復格式問題
                                    cleaned_content = re.sub(r'(\d+)\.\s+(\d+)', r'\1.\2', cleaned_content)
                                    cleaned_content = re.sub(r'\boveriden\b', 'overridden', cleaned_content, flags=re.IGNORECASE)
                                    cleaned_content = re.sub(r'\boverrid\b', 'overridden', cleaned_content, flags=re.IGNORECASE)
                                    cleaned_content = re.sub(r'\bloging\b', 'logging', cleaned_content, flags=re.IGNORECASE)
                                    cleaned_content = re.sub(r'\bcontinuesonextpage\b', '[內容繼續到下一頁]', cleaned_content, flags=re.IGNORECASE)
                                    # 修復雙斜線
                                    cleaned_content = re.sub(r'/+', '/', cleaned_content)
                                    # 移除多餘的空白字符
                                    cleaned_content = re.sub(r'\s+', ' ', cleaned_content).strip()
                                
                                # ===== 改善引用內容顯示：只顯示 filename 配置項和描述 =====
                                display_content = ""
                                
                                # 1. 優先提取 filename 配置項和其描述
                                # 匹配 "filename: /var/log/suricata.log Filename and location on disk."
                                # 更精確的正則：filename: 路徑 Filename 描述（直到下一個配置項或句號）
                                filename_pattern = r'filename:\s*([^\s\n]+(?:\s+[^\s\n]+)*?)\s+([Ff]ilename[^\.]+?)(?:\s+\w+:|\.|$)'
                                filename_match = re.search(filename_pattern, cleaned_content, re.IGNORECASE)
                                
                                if filename_match:
                                    # 提取 filename 配置項的值（路徑）
                                    filename_value = filename_match.group(1).strip()
                                    filename_value = re.sub(r'\s+', ' ', filename_value)  # 清理多餘空格
                                    
                                    # 提取描述（Filename and location on disk.）
                                    description = filename_match.group(2).strip()
                                    description = re.sub(r'\s+', ' ', description)  # 清理多餘空格
                                    # 確保描述以句號結尾
                                    if not description.endswith('.'):
                                        description += "."
                                    
                                    # 組合顯示內容：filename: /var/log/suricata.log\n\nFilename and location on disk.
                                    display_content = f"filename: {filename_value}\n\n{description}"
                                else:
                                    # 如果沒有找到 Filename 描述，嘗試只提取 filename 配置項
                                    filename_simple = re.search(r'filename:\s*([^\s\n]+(?:\s+[^\s\n]+)*?)(?:\s+\w+:|\.|$)', cleaned_content, re.IGNORECASE)
                                    if filename_simple:
                                        filename_value = filename_simple.group(1).strip()
                                        filename_value = re.sub(r'\s+', ' ', filename_value)
                                        display_content = f"filename: {filename_value}"
                                
                                # 2. 如果沒有找到 filename，嘗試提取其他路徑相關內容
                                if not display_content:
                                    # 查找包含 /var/log 的句子
                                    path_match = re.search(r'([^\n]{0,100}/var/log[^\n]{0,100})', cleaned_content, re.IGNORECASE)
                                    if path_match:
                                        display_content = path_match.group(1).strip()
                                        # 清理
                                        display_content = re.sub(r'\s+', ' ', display_content)
                                
                                # 3. 如果還是沒有，顯示前200字符
                                if not display_content:
                                    display_content = cleaned_content[:200].strip()
                                    # 在句子邊界截斷
                                    last_period = display_content.rfind('.')
                                    if last_period > 100:
                                        display_content = display_content[:last_period + 1]
                                    else:
                                        display_content += "..."
                                
                                # 如果還沒有提取到內容，使用備用邏輯（但應該不會執行到這裡）
                                if not display_content:
                                    # 只顯示前200字符作為備用
                                    display_content = cleaned_content[:200].strip()
                                    last_period = display_content.rfind('.')
                                    if last_period > 100:
                                        display_content = display_content[:last_period + 1]
                                    else:
                                        display_content += "..."
                                
                                # 顯示引用內容
                                answer += f"```\n{display_content}\n```\n"
                                
                                # ===== 方案3：改善搜索提示（提取更精確的關鍵詞）=====
                                keywords = []
                                
                                # 1. 優先提取完整路徑（最精確）
                                path_patterns = [
                                    (r'/var/log/suricata(?:/suricata\.log)?', '/var/log/suricata'),
                                    (r'/var/log(?:/suricata)?', '/var/log'),
                                    (r'var/log/suricata', '/var/log/suricata'),
                                    (r'suricata\.log', 'suricata.log'),
                                ]
                                
                                for pattern, keyword in path_patterns:
                                    if re.search(pattern, cleaned_content, re.IGNORECASE):
                                        if keyword not in keywords:
                                            keywords.append(keyword)
                                
                                # 2. 提取配置項名稱（如果存在）
                                config_items = re.findall(r'(\w+):\s*[^\n]+', cleaned_content)
                                for item in config_items[:3]:  # 只取前3個
                                    if len(item) > 3 and item.lower() not in ['the', 'and', 'for', 'with', 'use', 'output', 'enabled']:
                                        if item.lower() in ['filename', 'location', 'path', 'level', 'syslog']:
                                            keywords.append(item)
                                
                                # 3. 提取完整的短語（如果包含關鍵詞）
                                if "log directory" in cleaned_content.lower():
                                    # 嘗試提取包含 "log directory" 的完整短語
                                    match = re.search(r'([^.]{0,50}log\s+directory[^.]{0,50})', cleaned_content, re.IGNORECASE)
                                    if match:
                                        phrase = match.group(1).strip()
                                        if len(phrase) > 10 and len(phrase) < 80:
                                            keywords.append(f'"{phrase}"')  # 用引號標記完整短語
                                
                                # 4. 提取技術術語
                                if "default log" in cleaned_content.lower():
                                    keywords.append("default log")
                                if "log path" in cleaned_content.lower():
                                    keywords.append("log path")
                                
                                # 5. 提取配置相關的完整短語
                                # 例如："filename: /var/log/suricata.log"
                                filename_match = re.search(r'filename:\s*([^\n]{10,60})', cleaned_content, re.IGNORECASE)
                                if filename_match:
                                    filename_phrase = filename_match.group(0).strip()
                                    if len(filename_phrase) < 80:
                                        keywords.append(f'"{filename_phrase}"')
                                
                                # 6. 如果沒有找到具體關鍵詞，提取前幾個有意義的單詞
                                if not keywords:
                                    words = re.findall(r'\b[A-Z][a-z]+\b|\b[a-z]{4,}\b', cleaned_content)
                                    meaningful_words = [w for w in words[:5] if w.lower() not in ['the', 'and', 'for', 'with', 'this', 'that', 'from', 'that']]
                                    keywords.extend(meaningful_words)
                                
                                # 移除搜索提示（根據用戶要求）
                                
                                if len(cleaned_content) > 1200:
                                    answer += f"*（完整內容長度: {len(cleaned_content)} 字符，以上為摘要）*\n"
                                
                                answer += "\n"
                
                result["answer"] = answer
            else:
                result["answer"] = f"[API 錯誤] 狀態碼: {response.status_code}"
        except Exception as e:
            result["answer"] = f"[連線失敗] {str(e)}"
            print(f"Error in fetch: {e}")  # 調試信息
        finally:
            done.set()

    thread = threading.Thread(target=fetch)
    thread.start()
    for _ in range(50):
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
            <h1 style="color: #111;">趨勢科技技術知識問答助手</h1>
            <p style="color: #222;">基於 AI 技術的技術文檔、研究報告與產品資訊平台</p>
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
                placeholder="例如：什麼是VisionOne？",
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
    server_name="0.0.0.0",
    server_port=7860,
    share=False,
    show_error=True
)