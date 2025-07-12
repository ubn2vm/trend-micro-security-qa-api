"""
文本處理模組 - 專門處理 CREM 技術文檔的清理與分塊
用於文本清理、智能分塊和品質驗證
"""

import re
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CREMTextProcessor:
    """CREM 文本處理器 - 專門處理趨勢科技技術文檔"""
    
    def __init__(self):
        """初始化文本處理器"""
        self.technical_terms = [
            "CREM", "CRI", "Cyber Risk", "Risk Management", "AI", "Machine Learning",
            "XDR", "EDR", "SAE", "Trend Vision One", "Exposure Management",
            "Threat Detection", "Security Operations", "SOC", "Incident Response",
            "Vulnerability Management", "Compliance", "Governance", "Automation"
        ]
        
        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )
        
        logger.info("初始化 CREM 文本處理器")
    
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
        
        # 1. 移除頁碼標記
        text = re.sub(r'=== Page \d+ ===\n', '', text)
        
        # 2. 移除多餘的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 3. 移除特殊字符但保留重要標點
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\"\']', '', text)
        
        # 4. 保護技術術語
        text = self._protect_technical_terms(text)
        
        # 5. 修復常見的文本問題
        text = self._fix_common_issues(text)
        
        # 6. 移除重複內容
        text = self._remove_duplicates(text)
        
        # 7. 標準化格式
        text = self._normalize_format(text)
        
        logger.info(f"文本清理完成，長度: {len(text)} 字符")
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
    
    def chunk_text(self, text: str) -> List[Document]:
        """
        智能分塊文本
        
        Args:
            text (str): 清理後的文本
            
        Returns:
            List[Document]: 分塊後的文檔列表
        """
        if not text:
            return []
        
        logger.info("開始文本分塊...")
        
        try:
            # 使用 LangChain 的文本分割器
            chunks = self.text_splitter.split_text(text)
            
            # 轉換為 Document 對象
            documents = []
            for i, chunk in enumerate(chunks):
                if chunk.strip():  # 只保留非空塊
                    doc = Document(
                        page_content=chunk.strip(),
                        metadata={
                            "chunk_id": i,
                            "source": "sb-crem.pdf",
                            "chunk_size": len(chunk),
                            "technical_terms": self._extract_technical_terms(chunk)
                        }
                    )
                    documents.append(doc)
            
            logger.info(f"文本分塊完成，共 {len(documents)} 個塊")
            return documents
            
        except Exception as e:
            logger.error(f"文本分塊失敗: {str(e)}")
            raise
    
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
        processor = CREMTextProcessor()
        
        # 3. 清理文本
        cleaned_text = processor.clean_text(text)
        
        # 4. 分塊文本
        chunks = processor.chunk_text(cleaned_text)
        
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
    
    print("=== 文本清理與分塊測試 ===")
    result = process_text_file(input_path, output_dir)
    
    if result["success"]:
        print("✅ 處理成功")
        print(f"📊 清理後文本長度: {result['cleaned_text_length']} 字符")
        print(f"📦 分塊數量: {result['chunks_count']}")
        print(f"📈 品質評估: {result['validation']}")
        print(f"📝 分塊樣本:")
        for i, sample in enumerate(result['sample_chunks'], 1):
            print(f"   塊 {i}: {sample}")
        
        # 驗證標準檢查
        print("\n=== 驗證標準檢查 ===")
        validation = result['validation']
        
        checks = [
            ("分塊數量 > 0", validation['total_chunks'] > 0),
            ("平均長度 200-1000 字符", 200 <= validation['average_length'] <= 1000),
            ("品質分數 > 80", validation['quality_score'] > 80),
            ("技術術語覆蓋率 > 50%", validation['technical_terms_count'] >= validation['total_chunks'] * 0.5)
        ]
        
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}")
        
        all_passed = all(passed for _, passed in checks)
        print(f"\n🎯 整體驗證結果: {'通過' if all_passed else '需要改進'}")
        
    else:
        print(f"❌ 處理失敗: {result['error']}") 