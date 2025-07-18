"""
表格文本轉換器
將提取的表格資料轉換為可向量化的文本格式，用於RAG查詢
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TableTextData:
    """表格文本化資料結構"""
    table_id: str
    content: str
    metadata: Dict[str, Any]

class TableTextConverter:
    """表格轉文本轉換器"""
    
    def __init__(self):
        self.conversion_stats = {
            "total_tables": 0,
            "converted_tables": 0,
            "total_text_length": 0
        }
    
    def convert_table_to_text(self, table_data: Dict[str, Any]) -> str:
        """
        將單個表格轉換為結構化文本
        
        Args:
            table_data: 表格資料字典
            
        Returns:
            結構化的文本描述
        
        >>> converter = TableTextConverter()
        >>> table = {
        ...     "title": "Test_Table",
        ...     "headers": ["名稱", "數值"],
        ...     "rows": [["項目A", "100"], ["項目B", "200"]],
        ...     "table_type": "comparison",
        ...     "source_page": 1
        ... }
        >>> text = converter.convert_table_to_text(table)
        >>> "表格標題: Test_Table" in text
        True
        >>> "項目A: 100" in text
        True
        """
        try:
            # 基本資訊
            title = table_data.get("title", "未命名表格")
            table_type = table_data.get("table_type", "一般")
            page = table_data.get("source_page", "未知")
            
            # 建構文本描述
            text_parts = [
                f"表格標題: {title}",
                f"表格類型: {table_type}",
                f"來源頁面: 第{page}頁",
                f"資料提取方法: {table_data.get('extractor_method', '未知')}",
                f"信心度: {table_data.get('confidence', 0):.1f}%"
            ]
            
            # 表格內容
            headers = table_data.get("headers", [])
            rows = table_data.get("rows", [])
            
            if headers:
                text_parts.append(f"表格欄位: {', '.join(str(h) for h in headers if h)}")
            
            # 轉換表格內容為可搜尋的文本
            if rows:
                text_parts.append("表格內容:")
                for i, row in enumerate(rows):
                    if len(row) >= len(headers):
                        # 建立欄位-值對應
                        row_text = []
                        for j, cell in enumerate(row):
                            if j < len(headers) and headers[j] and cell:
                                row_text.append(f"{headers[j]}: {cell}")
                        if row_text:
                            text_parts.append(f"  {', '.join(row_text)}")
                    else:
                        # 簡單連接
                        row_text = ', '.join(str(cell) for cell in row if cell)
                        if row_text:
                            text_parts.append(f"  {row_text}")
            
            # 額外的搜尋關鍵字（基於表格類型）
            text_parts.append(self._generate_search_keywords(table_data))
            
            return "\n".join(text_parts)
            
        except Exception as e:
            logger.warning(f"轉換表格失敗: {e}")
            return f"表格: {table_data.get('title', '轉換失敗')}"
    
    def _generate_search_keywords(self, table_data: Dict[str, Any]) -> str:
        """
        根據表格內容生成搜尋關鍵字
        
        Args:
            table_data: 表格資料
            
        Returns:
            關鍵字字串
        """
        keywords = []
        
        # 基於表格類型的關鍵字
        table_type = table_data.get("table_type", "")
        type_keywords = {
            "comparison": ["比較", "對比", "分析"],
            "statistical": ["統計", "數據", "數字"],
            "timeline": ["時間", "日期", "歷程"],
            "financial": ["財務", "金額", "成本"]
        }
        keywords.extend(type_keywords.get(table_type, []))
        
        # 從表格內容提取關鍵字
        headers = table_data.get("headers", [])
        rows = table_data.get("rows", [])
        
        # 添加標題中的關鍵字
        for header in headers:
            if header and len(str(header)) > 1:
                keywords.append(str(header))
        
        # 從前幾行資料提取關鍵詞
        for row in rows[:3]:  # 只處理前3行避免過長
            for cell in row:
                if cell and len(str(cell)) > 1 and len(str(cell)) < 20:
                    keywords.append(str(cell))
        
        if keywords:
            return f"搜尋關鍵字: {', '.join(keywords[:10])}"  # 限制關鍵字數量
        return ""
    
    def convert_tables_json_to_text(self, json_path: str, output_path: str = None) -> List[TableTextData]:
        """
        將表格JSON檔案轉換為文本資料
        
        Args:
            json_path: 表格JSON檔案路徑
            output_path: 輸出檔案路徑（可選）
            
        Returns:
            轉換後的文本資料列表
        """
        logger.info(f"開始轉換表格JSON: {json_path}")
        
        # 讀取表格資料
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tables = data.get("tables", [])
        self.conversion_stats["total_tables"] = len(tables)
        
        converted_tables = []
        
        for i, table in enumerate(tables):
            try:
                # 轉換為文本
                text_content = self.convert_table_to_text(table)
                
                # 建立文本資料物件
                table_text = TableTextData(
                    table_id=f"table_{i+1}_{table.get('title', 'unknown')}",
                    content=text_content,
                    metadata={
                        "original_table_data": table,
                        "source_page": table.get("source_page"),
                        "source_file": table.get("source_file"),
                        "table_type": table.get("table_type"),
                        "confidence": table.get("confidence"),
                        "extractor_method": table.get("extractor_method"),
                        "conversion_date": datetime.now().isoformat()
                    }
                )
                
                converted_tables.append(table_text)
                self.conversion_stats["converted_tables"] += 1
                self.conversion_stats["total_text_length"] += len(text_content)
                
            except Exception as e:
                logger.warning(f"轉換第{i+1}個表格失敗: {e}")
        
        # 儲存結果
        if output_path:
            self.save_converted_tables(converted_tables, output_path)
        
        logger.info(f"轉換完成: {self.conversion_stats['converted_tables']}/{self.conversion_stats['total_tables']} 個表格")
        logger.info(f"總文本長度: {self.conversion_stats['total_text_length']} 字元")
        
        return converted_tables
    
    def save_converted_tables(self, converted_tables: List[TableTextData], output_path: str) -> None:
        """
        儲存轉換後的表格文本
        
        Args:
            converted_tables: 轉換後的表格文本列表
            output_path: 輸出檔案路徑
        """
        output_data = {
            "conversion_date": datetime.now().isoformat(),
            "total_tables": len(converted_tables),
            "conversion_stats": self.conversion_stats,
            "table_texts": [
                {
                    "table_id": table.table_id,
                    "content": table.content,
                    "metadata": table.metadata
                }
                for table in converted_tables
            ]
        }
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"表格文本已儲存到: {output_path}")
    
    def get_conversion_stats(self) -> Dict[str, Any]:
        """獲取轉換統計資訊"""
        return self.conversion_stats.copy()


def convert_tables_to_text_demo():
    """Demo函數：轉換表格為文本"""
    converter = TableTextConverter()
    
    # 輸入和輸出路徑
    json_path = "data/processed/extracted_tables.json"
    output_path = "data/processed/table_texts.json"
    
    try:
        # 執行轉換
        converted_tables = converter.convert_tables_json_to_text(json_path, output_path)
        
        # 顯示統計
        stats = converter.get_conversion_stats()
        logger.info("=== 轉換統計 ===")
        logger.info(f"總表格數: {stats['total_tables']}")
        logger.info(f"成功轉換: {stats['converted_tables']}")
        logger.info(f"總文本長度: {stats['total_text_length']} 字元")
        
        # 顯示前3個範例
        logger.info("=== 轉換範例 ===")
        for i, table_text in enumerate(converted_tables[:3]):
            logger.info(f"\n表格 {i+1}:")
            logger.info(f"ID: {table_text.table_id}")
            logger.info(f"內容預覽: {table_text.content[:200]}...")
        
        return converted_tables, stats
        
    except Exception as e:
        logger.error(f"轉換失敗: {e}")
        return [], {}


if __name__ == "__main__":
    convert_tables_to_text_demo() 