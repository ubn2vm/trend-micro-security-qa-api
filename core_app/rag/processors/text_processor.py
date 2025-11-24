"""
文本處理模組 - 專門處理技術文檔的清理與分塊
用於文本清理、智能分塊和品質驗證
"""

import re
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextProcessor:
    """文本處理器 - 專門處理趨勢科技技術文檔"""
    
    def __init__(self):
        """初始化文本處理器"""
        self.technical_terms = [
            "CREM", "CRI", "Cyber Risk", "Risk Management", "AI", "Machine Learning",
            "XDR", "EDR", "SAE", "Trend Vision One", "Exposure Management",
            "Threat Detection", "Security Operations", "SOC", "Incident Response",
            "Vulnerability Management", "Compliance", "Governance", "Automation",
            # 網路設備和產品縮寫
            "DDI", "Deep Discovery Inspector", "Deep Discovery", "Discovery Inspector",
            # 日誌和事件相關
            "Event ID", "syslog", "Suricata", "log format", "event parsing",
            "log directory", "log path", "/var/log", "var/log", "suricata.log",
            "default log", "預設日誌", "日誌目錄", "日誌路徑",
            # 錯誤碼相關
            "error code", "network error", "0x80070005",
            # 故障排除相關
            "troubleshooting", "故障排除", "administration console", "log on", "login",
            "credentials", "network cable", "cannot log on", "access management interface",
            "authentication", "network connection",
            # CEF 格式相關
            "CEF", "Common Event Format", "CEF format", "CEF key", "CEF欄位", "CEF field",
            "threat log", "威脅日誌", "Attack Phase", "攻擊階段", "cs6Label", "pAttackPhase",
            "cs6", "field mapping", "欄位映射", "對應", "mapping"
        ]
        
        # 縮寫到完整形式的映射（用於查詢擴展）
        self.abbreviation_map = {
            "DDI": "Deep Discovery Inspector",
            "CREM": "Cyber Risk Exposure Management",
            "CRI": "Cyber Risk Index",
            "XDR": "Extended Detection and Response",
            "EDR": "Endpoint Detection and Response",
            "SAE": "Security Analytics Engine",
            "SOC": "Security Operations Center"
        }
        
        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )
        
        logger.info("初始化 文本處理器")
    
    def clean_citation_content(self, text: str) -> str:
        """
        清理引用內容，移除格式問題，使其更容易在原文中找到
        
        Args:
            text: 原始文本
            
        Returns:
            清理後的文本
        """
        if not text:
            return text
        
        cleaned = text.strip()
        
        # 移除開頭的奇怪字符（點號、句號等）
        while cleaned and cleaned[0] in ['.', '。', '·', '•', ' ']:
            cleaned = cleaned[1:].strip()
        
        # 修復常見的格式問題
        import re
        
        # ===== 方案2：修復路徑格式問題（PDF 提取時空格被移除的情況）=====
        # 修復 "varlogSuricata. log" -> "/var/log/suricata.log"
        # 先修復雙斜線問題（避免重複修復）
        cleaned = re.sub(r'/+', '/', cleaned)  # 將多個斜線合併為單個
        
        path_fixes = [
            (r'\bvarlog([Ss]uricata)\.?\s*log\b', r'/var/log/suricata.log'),  # 統一為小寫
            (r'\bvar/log([Ss]uricata)\.?\s*log\b', r'/var/log/suricata.log'),
            (r'\bvar/log\s+([Ss]uricata)\b', r'/var/log/suricata'),
            (r'\b([Vv]ar)\s*/\s*([Ll]og)\b', r'/var/log'),  # 統一為小寫
            (r'\b([Vv]ar)\s+([Ll]og)\b', r'/var/log'),      # 統一為小寫
            (r'\b([Vv]ar)\s*log\b', r'/var/log'),          # 統一為小寫
            (r'\bvar\s*log\s*([Ss]uricata)\b', r'/var/log/suricata'),  # 統一為小寫
            # 修復已經有斜線但格式錯誤的情況
            (r'//+var/log', r'/var/log'),  # 修復雙斜線
            (r'/var/log/([Ss]uricata)\.log', r'/var/log/suricata.log'),  # 統一大小寫
        ]
        for pattern, replacement in path_fixes:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        
        # 再次確保沒有雙斜線
        cleaned = re.sub(r'/+', '/', cleaned)
        
        # 修復配置項格式（如 "filename:" 後面的路徑）
        # "filename: varlogSuricata. log" -> "filename: /var/log/suricata.log"
        cleaned = re.sub(r'filename:\s*([^\s]+)\s+([Ff]ilename)', r'filename: \1\n\2', cleaned)
        
        # 修復路徑中的點號問題（如 "varlogSuricata. log"）
        cleaned = re.sub(r'([Vv]ar[/\s]*[Ll]og[/\s]*[Ss]uricata)\.\s*log', r'\1.log', cleaned)
        
        # 修復版本號中的空格（如 "pre-7. 0" -> "pre-7.0"）
        cleaned = re.sub(r'(\d+)\.\s+(\d+)', r'\1.\2', cleaned)
        
        # 修復常見的拼寫錯誤（PDF 提取時產生的）
        spelling_fixes = {
            r'\boveriden\b': 'overridden',
            r'\boverrid\b': 'overridden',  # 處理截斷的情況
            r'\bdiferent\b': 'different',  # 新增：修復 "diferent"
            r'\bdisc\b': 'disk',          # "disc" -> "disk" (在 "location on disc" 中)
            r'\bloging\b': 'logging',
            r'\bal\b': 'all',  # "al disabled" -> "all disabled"
            r'\bwil\b': 'will',
            r'\bcontinuesonextpage\b': '[內容繼續到下一頁]',
        }
        for pattern, replacement in spelling_fixes.items():
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        
        # 修復配置項格式問題
        # "filename: varlogSuricata. log Filename" -> "filename: /var/log/suricata.log\nFilename"
        cleaned = re.sub(r'(filename:\s*)([^\n]+?)(\s+[Ff]ilename)', 
                        lambda m: f"{m.group(1)}{m.group(2).strip()}\n{m.group(3)}", 
                        cleaned)
        
        # 改善配置項格式：將配置項分行顯示，讓結構更清晰
        # 匹配 "key: value description" 格式
        # 將配置項分行，但保留描述在同一行
        config_pattern = r'(\w+):\s*([^\n\.]+?)(?=\s+\w+:|\.|$)'
        def format_config_item(match):
            key = match.group(1)
            value = match.group(2).strip()
            # 如果值很長，嘗試在適當位置換行
            if len(value) > 60:
                # 嘗試在句子邊界換行
                space_pos = value.rfind(' ', 0, 60)
                if space_pos > 20:
                    value = value[:space_pos] + '\n  ' + value[space_pos+1:]
            return f"{key}: {value}"
        
        # 先處理明顯的配置項（以冒號結尾的）
        cleaned = re.sub(r'(\w+):\s*([^\n]+?)(?=\s+\w+:|$)', format_config_item, cleaned)
        
        # 移除多餘的空白字符，但保留換行
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)  # 將多個空格/製表符合併為單個空格
        cleaned = re.sub(r' *\n *', '\n', cleaned)  # 清理換行周圍的空格
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)  # 將多個換行合併為最多兩個
        
        # 移除開頭和結尾的空白
        cleaned = cleaned.strip()
        
        return cleaned
    
    def clean_text(self, text: str) -> str:
        """
        清理文本內容
        
        Args:
            text (str): 原始文本
            
        Returns:
            str: 清理後的文本
        """
        if not text:
            return ""
        
        logger.info("開始清理文本...")
        
        # 1. 先保護頁碼標記（臨時替換，避免被清理掉）
        # 使用特殊標記來保護頁碼標記
        page_marker_pattern = r'=== Page (\d+) ==='
        protected_markers = {}
        marker_counter = 0
        
        def protect_marker(match):
            nonlocal marker_counter
            page_num = match.group(1)
            marker_id = f"__PAGE_MARKER_{marker_counter}__"
            protected_markers[marker_id] = f"=== Page {page_num} ===\n"
            marker_counter += 1
            return marker_id
        
        # 保護所有頁碼標記
        text = re.sub(page_marker_pattern, protect_marker, text)
        
        # 2. 移除多餘的空白字符（但保留換行，因為頁碼標記需要換行）
        # 先將多個連續空格合併為單個空格
        text = re.sub(r'[ \t]+', ' ', text)
        # 清理換行周圍的空格，但保留換行本身
        text = re.sub(r' *\n *', '\n', text)
        # 將多個連續換行合併為最多兩個
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 3. 移除特殊字符但保留重要標點（不包括 =，因為頁碼標記需要）
        # 注意：這裡不清理，因為頁碼標記已經被保護了
        # 只清理非頁碼標記區域的特殊字符
        def clean_non_marker(match):
            content = match.group(0)
            # 如果包含保護標記，不清理
            if any(marker_id in content for marker_id in protected_markers):
                return content
            # 否則清理特殊字符
            return re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\"\']', '', content)
        
        # 分段處理：只在非頁碼標記區域清理
        parts = re.split(r'(__PAGE_MARKER_\d+__)', text)
        cleaned_parts = []
        for part in parts:
            if part.startswith('__PAGE_MARKER_') and part.endswith('__'):
                # 這是保護標記，直接保留
                cleaned_parts.append(part)
            else:
                # 這是普通文本，清理特殊字符
                cleaned_parts.append(re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\"\']', '', part))
        
        text = ''.join(cleaned_parts)
        
        # 4. 恢復頁碼標記
        for marker_id, original_marker in protected_markers.items():
            text = text.replace(marker_id, original_marker)
        
        # 5. 保護技術術語
        text = self._protect_technical_terms(text)
        
        # 6. 修復常見的文本問題
        text = self._fix_common_issues(text)
        
        # 7. 移除重複內容（但要保護頁碼標記）
        # 再次保護頁碼標記，因為 _remove_duplicates 可能會影響它們
        text = re.sub(page_marker_pattern, protect_marker, text)
        text = self._remove_duplicates(text)
        # 恢復頁碼標記
        for marker_id, original_marker in protected_markers.items():
            text = text.replace(marker_id, original_marker)
        
        # 8. 標準化格式
        text = self._normalize_format(text)
        
        logger.info(f"文本清理完成，長度: {len(text)} 字符，保護了 {len(protected_markers)} 個頁碼標記")
        return text.strip()
    
    def _protect_technical_terms(self, text: str) -> str:
        """
        保護技術術語不被清理掉
        
        Args:
            text (str): 原始文本
            
        Returns:
            str: 保護後的文本
        """
        # 為技術術語添加特殊標記
        for term in self.technical_terms:
            if term.lower() in text.lower():
                # 使用正則表達式進行大小寫不敏感的替換
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                text = pattern.sub(f"__{term.upper()}__", text)
        
        return text
    
    def _fix_common_issues(self, text: str) -> str:
        """
        修復常見的文本問題
        
        Args:
            text (str): 原始文本
            
        Returns:
            str: 修復後的文本
        """
        # 修復句號後缺少空格
        text = re.sub(r'(\w)\.(\w)', r'\1. \2', text)
        
        # 修復逗號後缺少空格
        text = re.sub(r'(\w)\,(\w)', r'\1, \2', text)
        
        # 修復冒號後缺少空格
        text = re.sub(r'(\w)\:(\w)', r'\1: \2', text)
        
        # 修復分號後缺少空格
        text = re.sub(r'(\w)\;(\w)', r'\1; \2', text)
        
        # 移除多餘的標點符號
        text = re.sub(r'[\.\,\;\:\!\?]{2,}', '.', text)
        
        return text
    
    def _remove_duplicates(self, text: str) -> str:
        """
        移除重複內容
        
        Args:
            text (str): 原始文本
            
        Returns:
            str: 去重後的文本
        """
        # 移除連續的相同句子
        sentences = text.split('.')
        unique_sentences = []
        prev_sentence = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sentence != prev_sentence:
                unique_sentences.append(sentence)
                prev_sentence = sentence
        
        return '. '.join(unique_sentences)
    
    def _normalize_format(self, text: str) -> str:
        """
        標準化文本格式
        
        Args:
            text (str): 原始文本
            
        Returns:
            str: 標準化後的文本
        """
        # 恢復技術術語標記
        for term in self.technical_terms:
            text = text.replace(f"__{term.upper()}__", term)
        
        # 確保句子以句號結尾
        if text and not text.endswith('.'):
            text += '.'
        
        return text
    
    def chunk_text(self, text: str, source_path: Optional[str] = None) -> List[Document]:
        """
        智能分塊文本（改進版：在分割前預處理頁碼）
        
        Args:
            text (str): 清理後的文本（包含 === Page X === 標記）
            source_path (Optional[str]): 原始文件路徑，用於記錄 metadata.source
            
        Returns:
            List[Document]: 分塊後的文檔列表（每個 chunk 都包含頁碼信息）
        """
        if not text:
            return []
        
        logger.info("開始文本分塊...")

        # 根據來源路徑決定 metadata.source；預設值避免硬編寫死來源
        source_name = None
        if source_path:
            try:
                source_name = Path(source_path).name or str(source_path)
            except Exception:
                source_name = str(source_path)
        if not source_name:
            source_name = "unknown"
        
        try:
            # ===== 步驟 1：在分割前建立頁碼位置映射表 =====
            import re
            page_markers = []
            
            # 找到所有頁碼標記的位置
            for match in re.finditer(r'=== Page (\d+) ===', text):
                page_markers.append({
                    'position': match.start(),  # 標記在文本中的位置
                    'page_num': int(match.group(1)),  # 頁碼數字
                    'end_position': match.end()  # 標記結束位置
                })
            
            logger.info(f"找到 {len(page_markers)} 個頁碼標記")
            
            # 建立頁碼映射：每個字符位置對應的頁碼
            # 使用區間映射，每個區間對應一個頁碼
            page_ranges = []
            if page_markers:
                # 第一個頁碼標記之前的所有內容屬於第一頁（如果有的話）
                if page_markers[0]['position'] > 0:
                    page_ranges.append({
                        'start': 0,
                        'end': page_markers[0]['position'],
                        'page': page_markers[0]['page_num']  # 使用第一個頁碼
                    })
                
                # 處理每個頁碼標記之間的內容
                for i in range(len(page_markers)):
                    current_marker = page_markers[i]
                    page_num = current_marker['page_num']
                    
                    # 確定這個頁碼標記之後的內容範圍
                    start_pos = current_marker['end_position']
                    
                    # 結束位置：下一個頁碼標記的位置，或者文本結尾
                    if i + 1 < len(page_markers):
                        end_pos = page_markers[i + 1]['position']
                    else:
                        end_pos = len(text)
                    
                    page_ranges.append({
                        'start': start_pos,
                        'end': end_pos,
                        'page': page_num
                    })
            
            # ===== 步驟 2：分割文本 =====
            chunks = self.text_splitter.split_text(text)
            
            # ===== 步驟 3：為每個 chunk 分配頁碼 =====
            documents = []
            
            for i, chunk in enumerate(chunks):
                if chunk.strip():  # 只保留非空塊
                    # 方法 1：嘗試從 chunk 內容中直接提取頁碼（如果包含標記）
                    page_num = self._extract_page_number(chunk)
                    
                    # 方法 2：如果沒有找到，根據 chunk 在原文中的位置推斷頁碼
                    if not page_num and page_ranges:
                        # 找到這個 chunk 在原文中的起始位置
                        # 使用 chunk 的前 100 字符來定位（避免因為清理導致找不到）
                        chunk_prefix = chunk[:100].strip()
                        chunk_start_in_text = text.find(chunk_prefix)
                        
                        if chunk_start_in_text >= 0:
                            # 查找這個位置屬於哪個頁碼範圍
                            for page_range in page_ranges:
                                if page_range['start'] <= chunk_start_in_text < page_range['end']:
                                    page_num = page_range['page']
                                    break
                        
                        # 如果還是找不到，嘗試使用 chunk 的末尾位置
                        if not page_num:
                            chunk_suffix = chunk[-100:].strip()
                            if chunk_suffix:
                                chunk_end_in_text = text.rfind(chunk_suffix)
                                if chunk_end_in_text >= 0:
                                    for page_range in page_ranges:
                                        if page_range['start'] <= chunk_end_in_text < page_range['end']:
                                            page_num = page_range['page']
                                            break
                        
                        # 如果還是找不到，使用最接近的頁碼標記
                        if not page_num and page_markers:
                            # 使用 chunk 的中間位置
                            chunk_mid = chunk[len(chunk)//2:len(chunk)//2+50] if len(chunk) > 50 else chunk
                            chunk_mid_in_text = text.find(chunk_mid)
                            if chunk_mid_in_text >= 0:
                                # 找到最接近的頁碼標記
                                closest_marker = None
                                min_distance = float('inf')
                                for marker in page_markers:
                                    distance = abs(marker['position'] - chunk_mid_in_text)
                                    if distance < min_distance:
                                        min_distance = distance
                                        closest_marker = marker
                                if closest_marker:
                                    page_num = closest_marker['page_num']
                    
                    # 清理 chunk 內容（移除頁碼標記，但保留在 metadata 中）
                    cleaned_chunk = chunk.strip()
                    # 移除頁碼標記，但保留內容
                    cleaned_chunk = re.sub(r'=== Page \d+ ===\s*\n?', '', cleaned_chunk)
                    
                    metadata = {
                        "chunk_id": i,
                        "source": source_name,
                        "chunk_size": len(chunk),
                        "technical_terms": self._extract_technical_terms(chunk)
                    }
                    
                    # 如果找到頁碼，添加到 metadata
                    if page_num:
                        metadata["page"] = page_num
                        metadata["source_page"] = page_num
                    else:
                        # 如果還是沒有頁碼，記錄警告
                        logger.warning(f"Chunk {i} 無法確定頁碼，chunk 前 50 字符: {chunk[:50]}")
                    
                    doc = Document(
                        page_content=cleaned_chunk.strip(),
                        metadata=metadata
                    )
                    documents.append(doc)
            
            # 統計頁碼分配情況
            chunks_with_page = sum(1 for doc in documents if 'page' in doc.metadata)
            logger.info(f"文本分塊完成，共 {len(documents)} 個塊，其中 {chunks_with_page} 個包含頁碼信息 ({chunks_with_page/len(documents)*100:.1f}%)")
            
            return documents
            
        except Exception as e:
            logger.error(f"文本分塊失敗: {str(e)}")
            raise
    
    def _extract_page_number(self, text: str) -> Optional[int]:
        """
        從文本中提取頁碼
        
        Args:
            text: 文本內容
            
        Returns:
            頁碼（如果找到），否則 None
        """
        import re
        # 匹配 === Page X === 格式
        page_match = re.search(r'=== Page (\d+) ===', text)
        if page_match:
            return int(page_match.group(1))
        return None
    
    def _extract_technical_terms(self, text: str) -> List[str]:
        """
        提取文本中的技術術語
        
        Args:
            text (str): 文本內容
            
        Returns:
            List[str]: 找到的技術術語列表
        """
        found_terms = []
        for term in self.technical_terms:
            if term.lower() in text.lower():
                found_terms.append(term)
        return found_terms
    
    def validate_chunks(self, chunks: List[Document]) -> Dict[str, Any]:
        """
        驗證分塊品質
        
        Args:
            chunks (List[Document]): 分塊列表
            
        Returns:
            Dict[str, Any]: 驗證結果
        """
        if not chunks:
            return {"quality_score": 0, "issues": ["無分塊內容"]}
        
        total_chunks = len(chunks)
        total_length = sum(len(chunk.page_content) for chunk in chunks)
        avg_length = total_length / total_chunks if total_chunks > 0 else 0
        
        # 統計技術術語
        technical_terms_count = sum(
            len(chunk.metadata.get("technical_terms", [])) 
            for chunk in chunks
        )
        
        # 檢查分塊大小分布
        size_distribution = {
            "small": sum(1 for chunk in chunks if len(chunk.page_content) < 200),
            "medium": sum(1 for chunk in chunks if 200 <= len(chunk.page_content) <= 800),
            "large": sum(1 for chunk in chunks if len(chunk.page_content) > 800)
        }
        
        # 計算品質分數
        score = 100
        
        # 檢查平均長度
        if avg_length < 200:
            score -= 20
        elif avg_length > 1000:
            score -= 10
        
        # 檢查技術術語覆蓋
        if technical_terms_count < total_chunks * 0.5:
            score -= 15
        
        # 檢查分塊大小分布
        if size_distribution["small"] > total_chunks * 0.3:
            score -= 10
        
        return {
            "quality_score": max(0, score),
            "total_chunks": total_chunks,
            "total_length": total_length,
            "average_length": avg_length,
            "technical_terms_count": technical_terms_count,
            "size_distribution": size_distribution,
            "issues": []
        }
    
    def save_chunks(self, chunks: List[Document], output_path: str) -> None:
        """
        保存分塊結果
        
        Args:
            chunks (List[Document]): 分塊列表
            output_path (str): 輸出文件路徑
        """
        try:
            # 轉換為可序列化的格式
            serializable_chunks = []
            for chunk in chunks:
                serializable_chunks.append({
                    "content": chunk.page_content,
                    "metadata": chunk.metadata
                })
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_chunks, f, indent=2, ensure_ascii=False)
            
            logger.info(f"分塊結果已保存到: {output_path}")
            
        except Exception as e:
            logger.error(f"保存分塊結果失敗: {str(e)}")
            raise

def process_text_file(input_path: str, output_dir: str = None) -> Dict[str, Any]:
    """
    處理文本文件的完整流程
    
    Args:
        input_path (str): 輸入文件路徑
        output_dir (str): 輸出目錄（可選）
        
    Returns:
        Dict[str, Any]: 處理結果
    """
    try:
        # 1. 讀取文本文件
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # 2. 初始化處理器
        processor = TextProcessor()
        
        # 3. 清理文本
        cleaned_text = processor.clean_text(text)
        
        # 4. 分塊文本
        chunks = processor.chunk_text(cleaned_text, source_path=input_path)
        
        # 5. 驗證分塊品質
        validation = processor.validate_chunks(chunks)
        
        # 6. 保存結果（如果指定了輸出目錄）
        if output_dir:
            # 保存清理後的文本
            cleaned_path = Path(output_dir) / "cleaned_text.txt"
            with open(cleaned_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
            
            # 保存分塊結果
            chunks_path = Path(output_dir) / "text_chunks.json"
            processor.save_chunks(chunks, str(chunks_path))
            
            # 保存處理報告
            report_path = Path(output_dir) / "text_processing_report.json"
            report = {
                "input_file": input_path,
                "cleaned_text_length": len(cleaned_text),
                "chunks_count": len(chunks),
                "validation": validation,
                "processing_timestamp": str(Path().cwd())
            }
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "cleaned_text_length": len(cleaned_text),
            "chunks_count": len(chunks),
            "validation": validation,
            "sample_chunks": [chunk.page_content[:200] + "..." for chunk in chunks[:3]]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # 測試腳本
    input_path = "data/extracted_text.txt"
    output_dir = "data"
    
    logger.info("=== 文本清理與分塊測試 ===")
    result = process_text_file(input_path, output_dir)
    
    if result["success"]:
        logger.info("✅ 處理成功")
        logger.info(f"📊 清理後文本長度: {result['cleaned_text_length']} 字符")
        logger.info(f"📦 分塊數量: {result['chunks_count']}")
        logger.info(f"📈 品質評估: {result['validation']}")
        logger.info(f"📝 分塊樣本:")
        for i, sample in enumerate(result['sample_chunks'], 1):
            logger.info(f"   塊 {i}: {sample}")
        
        # 驗證標準檢查
        logger.info("\n=== 驗證標準檢查 ===")
        validation = result['validation']
        
        checks = [
            ("分塊數量 > 0", validation['total_chunks'] > 0),
            ("平均長度 200-1000 字符", 200 <= validation['average_length'] <= 1000),
            ("品質分數 > 80", validation['quality_score'] > 80),
            ("技術術語覆蓋率 > 50%", validation['technical_terms_count'] >= validation['total_chunks'] * 0.5)
        ]
        
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            logger.info(f"{status} {check_name}")
        
        all_passed = all(passed for _, passed in checks)
        logger.info(f"\n🎯 整體驗證結果: {'通過' if all_passed else '需要改進'}")
        
    else:
        logger.error(f"❌ 處理失敗: {result['error']}") 