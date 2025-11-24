"""
PDF 處理模組 - 專門處理趨勢科技技術文檔
用於提取 PDF 文本內容並進行預處理
"""

import pdfplumber
import re
import logging
import json
from typing import List, Optional, Dict, Any
from pathlib import Path
import os

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """PDF 處理器 - 專門處理趨勢科技技術文檔"""
    
    def __init__(self, pdf_path: str):
        """
        初始化 PDF 處理器
        
        Args:
            pdf_path (str): PDF 文件路徑
        """
        self.pdf_path = Path(pdf_path)
        self.text_content = []
        self.total_pages = 0
        self.extracted_pages = 0
        
        # 驗證文件存在
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")
        
        logger.info(f"初始化 PDF 處理器: {pdf_path}")
    
    def extract_text(self) -> str:
        """
        提取 PDF 文本內容
        
        Returns:
            str: 提取的文本內容
        """
        logger.info("開始提取 PDF 文本...")
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                self.total_pages = len(pdf.pages)
                logger.info(f"PDF 總頁數: {self.total_pages}")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        # 提取頁面文本
                        text = page.extract_text()
                        
                        if text and text.strip():
                            # 清理文本
                            cleaned_text = self._clean_page_text(text)
                            
                            # 添加頁碼標記
                            page_marker = f"=== Page {page_num} ===\n"
                            page_content = page_marker + cleaned_text + "\n\n"
                            
                            self.text_content.append(page_content)
                            self.extracted_pages += 1
                            
                            logger.info(f"成功提取第 {page_num} 頁文本 ({len(cleaned_text)} 字符)")
                        else:
                            logger.warning(f"第 {page_num} 頁無文本內容")
                            
                    except Exception as e:
                        logger.error(f"提取第 {page_num} 頁時發生錯誤: {str(e)}")
                        continue
            
            # 合併所有頁面文本
            full_text = ''.join(self.text_content)
            
            logger.info(f"文本提取完成: {self.extracted_pages}/{self.total_pages} 頁成功")
            logger.info(f"總文本長度: {len(full_text)} 字符")
            
            return full_text
            
        except Exception as e:
            logger.error(f"PDF 文本提取失敗: {str(e)}")
            raise
    
    def _clean_page_text(self, text: str) -> str:
        """
        清理頁面文本
        
        Args:
            text (str): 原始頁面文本
            
        Returns:
            str: 清理後的文本
        """
        if not text:
            return ""
        
        # 修復重複字符問題 (如 "SSoolluuttiioonn" -> "Solution")
        text = self._fix_duplicate_characters(text)
        
        # 移除多餘的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除頁眉頁腳等常見噪音
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)  # 移除單獨的頁碼
        
        # 保持技術術語的完整性
        text = re.sub(r'\b(CREM|CRI|AI|ML|XDR|EDR|SAE)\b', r' \1 ', text, flags=re.IGNORECASE)
        
        # 移除特殊字符但保留重要標點
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\"\']', '', text)
        
        # 修復常見的文本問題
        text = re.sub(r'(\w)\.(\w)', r'\1. \2', text)  # 修復句號後缺少空格
        text = re.sub(r'(\w)\,(\w)', r'\1, \2', text)  # 修復逗號後缺少空格
        
        return text.strip()
    
    def _fix_duplicate_characters(self, text: str) -> str:
        """
        修復重複字符問題
        
        Args:
            text (str): 原始文本
            
        Returns:
            str: 修復後的文本
        """
        # 修復常見的重複字符模式
        duplicate_patterns = [
            (r'([A-Z])\1+', r'\1'),  # 修復大寫字母重複
            (r'([a-z])\1+', r'\1'),  # 修復小寫字母重複
            (r'([0-9])\1+', r'\1'),  # 修復數字重複
        ]
        
        for pattern, replacement in duplicate_patterns:
            text = re.sub(pattern, replacement, text)
        
        # 修復特定的技術術語
        term_fixes = {
            'SSoolluuttiioonn': 'Solution',
            'BBrriieeff': 'Brief',
            'TREND VISION ONETM': 'TREND VISION ONE',
            'CCyymmeerr RRiisskk': 'Cyber Risk',
            'EExxppoossuurree': 'Exposure',
            'MMaannaaggeemmeenntt': 'Management',
            'CCRREEM': 'CREM',
            'PPrrooaaccttiivveellyy': 'Proactively',
            'uunnccoovveerr': 'uncover',
            'pprreeddiicctt': 'predict',
            'aasssseessss': 'assess',
            'mmiittiiggaattee': 'mitigate',
            'ccyymmeerr': 'cyber',
            'rriisskkss': 'risks',
            'pprriioorriittiizziinngg': 'prioritizing',
            'iimmppaacctt': 'impact',
            'rreedduucciinngg': 'reducing',
            'eexxppoossuurree': 'exposure',
            'bbuuiillddiinngg': 'building',
            'rreessiilliieennccee': 'resilience',
        }
        
        for wrong, correct in term_fixes.items():
            text = text.replace(wrong, correct)
        
        return text
    
    def get_extraction_stats(self) -> dict:
        """
        獲取提取統計資訊
        
        Returns:
            dict: 提取統計資訊
        """
        return {
            "total_pages": self.total_pages,
            "extracted_pages": self.extracted_pages,
            "success_rate": (self.extracted_pages / self.total_pages * 100) if self.total_pages > 0 else 0,
            "total_text_length": sum(len(text) for text in self.text_content)
        }
    
    def validate_text_quality(self, text: str) -> dict:
        """
        驗證文本品質
        
        Args:
            text (str): 要驗證的文本
            
        Returns:
            dict: 品質評估結果
        """
        if not text:
            return {"quality_score": 0, "issues": ["文本為空"]}
        
        issues = []
        score = 100
        
        # 檢查文本長度
        if len(text) < 100:
            issues.append("文本過短")
            score -= 20
        
        # 檢查技術術語
        crem_terms = ["CREM", "CRI", "Cyber Risk", "Risk Management", "AI", "Machine Learning"]
        found_terms = sum(1 for term in crem_terms if term.lower() in text.lower())
        
        if found_terms < 2:
            issues.append("缺少關鍵技術術語")
            score -= 15
        
        # 檢查文本結構
        sentences = text.split('.')
        if len(sentences) < 5:
            issues.append("句子數量過少")
            score -= 10
        
        # 檢查編碼問題
        if '?' in text or '' in text:
            issues.append("可能存在編碼問題")
            score -= 10
        
        return {
            "quality_score": max(0, score),
            "issues": issues,
            "found_technical_terms": found_terms,
            "sentence_count": len(sentences),
            "text_length": len(text)
        }
    
    def save_extraction_result(self, output_path: str, text: str) -> None:
        """
        保存提取結果
        
        Args:
            output_path (str): 輸出文件路徑
            text (str): 提取的文本
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            logger.info(f"提取結果已保存到: {output_path}")
        except Exception as e:
            logger.error(f"保存提取結果失敗: {str(e)}")
            raise

def extract_pdf_text(pdf_path: str) -> str:
    """
    便捷函數：提取 PDF 文本
    
    Args:
        pdf_path (str): PDF 文件路徑
        
    Returns:
        str: 提取的文本內容
    """
    processor = PDFProcessor(pdf_path)
    return processor.extract_text()

def comprehensive_validation(pdf_path: str, output_dir: str = None) -> Dict[str, Any]:
    """
    綜合驗證 PDF 提取功能
    
    Args:
        pdf_path (str): PDF 文件路徑
        output_dir (str): 輸出目錄（可選）
        
    Returns:
        dict: 完整的驗證結果
    """
    try:
        # 1. 初始化處理器
        processor = PDFProcessor(pdf_path)
        
        # 2. 提取文本
        text = processor.extract_text()
        
        # 3. 獲取統計資訊
        stats = processor.get_extraction_stats()
        
        # 4. 驗證文本品質
        quality = processor.validate_text_quality(text)
        
        # 5. 保存結果（如果指定了輸出目錄）
        if output_dir:
            output_path = Path(output_dir) / "extracted_text.txt"
            processor.save_extraction_result(str(output_path), text)
            
            # 保存驗證報告
            report_path = Path(output_dir) / "validation_report.json"
            report = {
                "extraction_stats": stats,
                "quality_assessment": quality,
                "validation_timestamp": str(Path().cwd()),
                "pdf_path": str(pdf_path)
            }
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 6. 返回完整結果
        return {
            "success": True,
            "extraction_stats": stats,
            "quality_assessment": quality,
            "sample_text": text[:1000] + "..." if len(text) > 1000 else text,
            "technical_terms_found": quality.get("found_technical_terms", 0),
            "quality_score": quality.get("quality_score", 0)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "extraction_stats": {},
            "quality_assessment": {}
        }

if __name__ == "__main__":
    # 測試腳本
    pdf_path = "data/sb-crem.pdf"
    output_dir = "data"
    
    logger.info("=== PDF 文本提取綜合驗證 ===")
    result = comprehensive_validation(pdf_path, output_dir)
    
    if result["success"]:
        logger.info("✅ 提取成功")
        logger.info(f"📊 統計資訊: {result['extraction_stats']}")
        logger.info(f"📈 品質評估: {result['quality_assessment']}")
        logger.info(f"🔍 技術術語數量: {result['technical_terms_found']}")
        logger.info(f"⭐ 品質分數: {result['quality_score']}/100")
        logger.info(f"📝 文本樣本:\n{result['sample_text'][:500]}...")
        
        # 驗證標準檢查
        logger.info("\n=== 驗證標準檢查 ===")
        stats = result['extraction_stats']
        quality = result['quality_assessment']
        
        checks = [
            ("PDF 文本提取成功率 > 95%", stats.get('success_rate', 0) >= 95),
            ("文本長度 > 1000 字符", quality.get('text_length', 0) > 1000),
            ("品質分數 > 80", quality.get('quality_score', 0) > 80),
            ("技術術語數量 >= 2", quality.get('found_technical_terms', 0) >= 2),
            ("句子數量 >= 5", quality.get('sentence_count', 0) >= 5)
        ]
        
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            logger.info(f"{status} {check_name}")
        
        all_passed = all(passed for _, passed in checks)
        logger.info(f"\n🎯 整體驗證結果: {'通過' if all_passed else '需要改進'}")
        
    else:
        logger.error(f"❌ 提取失敗: {result['error']}") 