"""
混合策略表格提取器
結合多種 PDF 處理函式庫，提供最佳的表格提取效果
"""

import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import pandas as pd
from datetime import datetime

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TableData:
    """表格資料結構"""
    title: str
    headers: List[str]
    rows: List[List[str]]
    source_page: int
    source_file: str
    table_type: str
    confidence: float
    extractor_method: str
    metadata: Dict[str, Any]

class AdvancedTableExtractor:
    """進階表格提取器 - 混合策略"""
    
    def __init__(self):
        self.available_extractors = self._check_available_extractors()
        logger.info(f"可用的提取器: {list(self.available_extractors.keys())}")
    
    def _check_available_extractors(self) -> Dict[str, bool]:
        """檢查可用的提取器"""
        extractors = {}
        
        # 檢查 camelot
        try:
            import camelot
            extractors['camelot'] = True
            logger.info("✅ camelot 可用")
        except ImportError:
            extractors['camelot'] = False
            logger.warning("❌ camelot 不可用")
        
        # 檢查 pdfplumber
        try:
            import pdfplumber
            extractors['pdfplumber'] = True
            logger.info("✅ pdfplumber 可用")
        except ImportError:
            extractors['pdfplumber'] = False
            logger.warning("❌ pdfplumber 不可用")
        
        # 檢查 PyMuPDF
        try:
            import fitz
            extractors['pymupdf'] = True
            logger.info("✅ PyMuPDF 可用")
        except ImportError:
            extractors['pymupdf'] = False
            logger.warning("❌ PyMuPDF 不可用")
        
        # 檢查 tabula
        try:
            import tabula
            extractors['tabula'] = True
            logger.info("✅ tabula 可用")
        except ImportError:
            extractors['tabula'] = False
            logger.warning("❌ tabula 不可用")
        
        return extractors
    
    def extract_tables(self, pdf_path: str) -> List[TableData]:
        """
        使用混合策略提取表格
        
        Args:
            pdf_path: PDF 檔案路徑
            
        Returns:
            提取的表格列表
        """
        logger.info(f"開始提取表格: {pdf_path}")
        all_tables = []
        
        # 策略 1: camelot (最準確的表格提取)
        if self.available_extractors.get('camelot', False):
            try:
                tables = self._extract_with_camelot(pdf_path)
                all_tables.extend(tables)
                logger.info(f"Camelot 提取到 {len(tables)} 個表格")
            except Exception as e:
                logger.warning(f"Camelot 提取失敗: {e}")
        
        # 策略 2: pdfplumber (平衡型選擇)
        if self.available_extractors.get('pdfplumber', False):
            try:
                tables = self._extract_with_pdfplumber(pdf_path)
                all_tables.extend(tables)
                logger.info(f"PDFPlumber 提取到 {len(tables)} 個表格")
            except Exception as e:
                logger.warning(f"PDFPlumber 提取失敗: {e}")
        
        # 策略 3: PyMuPDF (快速文本基礎提取)
        if self.available_extractors.get('pymupdf', False):
            try:
                tables = self._extract_with_pymupdf(pdf_path)
                all_tables.extend(tables)
                logger.info(f"PyMuPDF 提取到 {len(tables)} 個表格")
            except Exception as e:
                logger.warning(f"PyMuPDF 提取失敗: {e}")
        
        # 策略 4: tabula (備用方案)
        if self.available_extractors.get('tabula', False) and len(all_tables) < 2:
            try:
                tables = self._extract_with_tabula(pdf_path)
                all_tables.extend(tables)
                logger.info(f"Tabula 提取到 {len(tables)} 個表格")
            except Exception as e:
                logger.warning(f"Tabula 提取失敗: {e}")
        
        # 去重和合併
        unique_tables = self._deduplicate_tables(all_tables)
        logger.info(f"最終提取到 {len(unique_tables)} 個獨特表格")
        
        return unique_tables
    
    def _extract_with_camelot(self, pdf_path: str) -> List[TableData]:
        """使用 camelot 提取表格"""
        import camelot
        
        # 嘗試不同的提取策略
        strategies = [
            {'flavor': 'lattice'},  # 有邊框的表格
            {'flavor': 'stream'},   # 無邊框的表格
        ]
        
        all_tables = []
        
        for strategy in strategies:
            try:
                tables = camelot.read_pdf(pdf_path, pages='all', **strategy)
                
                for i, table in enumerate(tables):
                    if table.accuracy > 0.5:  # 只保留準確度較高的表格
                        df = table.df
                        
                        # 清理空行和空列
                        df = df.replace('', pd.NA).dropna(how='all').dropna(axis=1, how='all')
                        
                        if len(df) > 1:  # 至少要有標題和一行資料
                            table_data = TableData(
                                title=f"Camelot_Table_{table.page}_{i+1}",
                                headers=df.iloc[0].fillna('').tolist(),
                                rows=df.iloc[1:].fillna('').values.tolist(),
                                source_page=table.page,
                                source_file=pdf_path,
                                table_type=self._classify_table_type(df),
                                confidence=table.accuracy,
                                extractor_method='camelot',
                                metadata={
                                    'whitespace': table.whitespace,
                                    'order': table.order,
                                    'flavor': strategy['flavor']
                                }
                            )
                            all_tables.append(table_data)
                
            except Exception as e:
                logger.warning(f"Camelot {strategy} 策略失敗: {e}")
                continue
        
        return all_tables
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> List[TableData]:
        """使用 pdfplumber 提取表格"""
        import pdfplumber
        
        tables = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                try:
                    # 提取表格
                    page_tables = page.extract_tables()
                    
                    for i, table in enumerate(page_tables):
                        if table and len(table) > 1:
                            # 清理表格資料
                            cleaned_table = self._clean_table_data(table)
                            
                            if len(cleaned_table) > 1:
                                table_data = TableData(
                                    title=f"PDFPlumber_Table_{page_num+1}_{i+1}",
                                    headers=cleaned_table[0],
                                    rows=cleaned_table[1:],
                                    source_page=page_num + 1,
                                    source_file=pdf_path,
                                    table_type=self._classify_table_type(cleaned_table),
                                    confidence=0.8,
                                    extractor_method='pdfplumber',
                                    metadata={
                                        'page_width': page.width,
                                        'page_height': page.height
                                    }
                                )
                                tables.append(table_data)
                
                except Exception as e:
                    logger.warning(f"PDFPlumber 第 {page_num+1} 頁提取失敗: {e}")
                    continue
        
        return tables
    
    def _extract_with_pymupdf(self, pdf_path: str) -> List[TableData]:
        """使用 PyMuPDF 提取表格"""
        import fitz
        
        tables = []
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            try:
                page = doc[page_num]
                text = page.get_text()
                
                # 使用正則表達式尋找表格模式
                table_patterns = self._find_table_patterns_in_text(text)
                
                for i, pattern in enumerate(table_patterns):
                    if len(pattern['rows']) > 1:
                        table_data = TableData(
                            title=f"PyMuPDF_Table_{page_num+1}_{i+1}",
                            headers=pattern['headers'],
                            rows=pattern['rows'],
                            source_page=page_num + 1,
                            source_file=pdf_path,
                            table_type=self._classify_table_type(pattern['data']),
                            confidence=pattern['confidence'],
                            extractor_method='pymupdf',
                            metadata={
                                'extraction_method': 'text_pattern',
                                'pattern_type': pattern['type']
                            }
                        )
                        tables.append(table_data)
                
            except Exception as e:
                logger.warning(f"PyMuPDF 第 {page_num+1} 頁提取失敗: {e}")
                continue
        
        doc.close()
        return tables
    
    def _extract_with_tabula(self, pdf_path: str) -> List[TableData]:
        """使用 tabula 提取表格"""
        import tabula
        
        tables = []
        
        try:
            # 提取所有表格
            dfs = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
            
            for i, df in enumerate(dfs):
                if len(df) > 1:
                    # 清理資料
                    df = df.dropna(how='all').dropna(axis=1, how='all')
                    
                    if len(df) > 1:
                        table_data = TableData(
                            title=f"Tabula_Table_{i+1}",
                            headers=df.columns.tolist(),
                            rows=df.values.tolist(),
                            source_page=1,  # tabula 不提供頁面資訊
                            source_file=pdf_path,
                            table_type=self._classify_table_type(df),
                            confidence=0.7,
                            extractor_method='tabula',
                            metadata={'columns': len(df.columns), 'rows': len(df)}
                        )
                        tables.append(table_data)
        
        except Exception as e:
            logger.warning(f"Tabula 提取失敗: {e}")
        
        return tables
    
    def _find_table_patterns_in_text(self, text: str) -> List[Dict[str, Any]]:
        """在文本中尋找表格模式"""
        patterns = []
        
        # 模式 1: 以數字開頭的表格行
        lines = text.split('\n')
        table_lines = []
        current_table = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_table:
                    if len(current_table) > 2:  # 至少要有標題和兩行資料
                        patterns.append(self._parse_text_table(current_table))
                    current_table = []
                continue
            
            # 檢查是否為表格行（包含多個以空格或製表符分隔的項目）
            if self._is_table_line(line):
                current_table.append(line)
            else:
                if current_table:
                    if len(current_table) > 2:
                        patterns.append(self._parse_text_table(current_table))
                    current_table = []
        
        # 處理最後一個表格
        if current_table and len(current_table) > 2:
            patterns.append(self._parse_text_table(current_table))
        
        return patterns
    
    def _is_table_line(self, line: str) -> bool:
        """判斷是否為表格行"""
        # 檢查是否包含多個以空格分隔的項目
        parts = re.split(r'\s{2,}|\t', line)  # 兩個或更多空格，或製表符
        
        if len(parts) >= 2:
            # 檢查是否包含數字（表格通常包含數值資料）
            has_number = any(re.search(r'\d', part) for part in parts)
            return has_number
        
        return False
    
    def _parse_text_table(self, table_lines: List[str]) -> Dict[str, Any]:
        """解析文本表格"""
        rows = []
        for line in table_lines:
            # 分割行（使用多個空格或製表符作為分隔符）
            parts = re.split(r'\s{2,}|\t', line.strip())
            rows.append([part.strip() for part in parts if part.strip()])
        
        # 假設第一行是標題
        headers = rows[0] if rows else []
        data_rows = rows[1:] if len(rows) > 1 else []
        
        # 計算信心度
        confidence = self._calculate_text_table_confidence(rows)
        
        return {
            'headers': headers,
            'rows': data_rows,
            'data': rows,
            'confidence': confidence,
            'type': 'text_pattern'
        }
    
    def _calculate_text_table_confidence(self, rows: List[List[str]]) -> float:
        """計算文本表格的信心度"""
        if not rows or len(rows) < 2:
            return 0.0
        
        confidence = 0.5  # 基礎信心度
        
        # 檢查列數一致性
        col_counts = [len(row) for row in rows]
        if len(set(col_counts)) == 1:  # 所有行的列數相同
            confidence += 0.2
        
        # 檢查數值資料比例
        total_cells = sum(len(row) for row in rows)
        numeric_cells = sum(1 for row in rows for cell in row if re.search(r'\d', cell))
        
        if total_cells > 0:
            numeric_ratio = numeric_cells / total_cells
            confidence += numeric_ratio * 0.3
        
        return min(confidence, 1.0)
    
    def _clean_table_data(self, table: List[List[str]]) -> List[List[str]]:
        """清理表格資料"""
        cleaned = []
        for row in table:
            if row and any(cell and str(cell).strip() for cell in row):
                # 清理每個單元格
                cleaned_row = [str(cell).strip() if cell else '' for cell in row]
                cleaned.append(cleaned_row)
        return cleaned
    
    def _classify_table_type(self, data) -> str:
        """分類表格類型"""
        try:
            if isinstance(data, pd.DataFrame):
                df = data
            elif isinstance(data, list) and data:
                df = pd.DataFrame(data[1:], columns=data[0] if data else [])
            else:
                return 'unknown'
            
            # 檢查是否為時間序列表格
            if self._is_time_series_table(df):
                return 'time_series'
            # 檢查是否為比較表格
            elif self._is_comparison_table(df):
                return 'comparison'
            # 檢查是否為統計表格
            elif self._is_statistical_table(df):
                return 'statistical'
            else:
                return 'general'
        
        except Exception:
            return 'unknown'
    
    def _is_time_series_table(self, df: pd.DataFrame) -> bool:
        """檢查是否為時間序列表格"""
        if len(df.columns) == 0:
            return False
        
        # 檢查第一列是否包含年份或日期
        first_col = df.iloc[:, 0].astype(str)
        year_pattern = r'\b(20\d{2}|19\d{2})\b'
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        
        year_matches = first_col.str.contains(year_pattern, na=False).sum()
        date_matches = first_col.str.contains(date_pattern, na=False).sum()
        
        return (year_matches / len(first_col)) > 0.3 or (date_matches / len(first_col)) > 0.3
    
    def _is_comparison_table(self, df: pd.DataFrame) -> bool:
        """檢查是否為比較表格"""
        # 檢查是否有多個數值列
        numeric_cols = 0
        for col in df.columns:
            try:
                pd.to_numeric(df[col], errors='coerce')
                if df[col].notna().sum() > len(df) * 0.5:  # 至少 50% 是數值
                    numeric_cols += 1
            except:
                continue
        
        return numeric_cols >= 2
    
    def _is_statistical_table(self, df: pd.DataFrame) -> bool:
        """檢查是否為統計表格"""
        # 檢查是否包含統計關鍵字
        statistical_keywords = ['總計', '平均', '最大', '最小', '標準差', 'mean', 'average', 'total', 'sum']
        
        text_content = ' '.join([str(cell) for row in df.values for cell in row])
        
        for keyword in statistical_keywords:
            if keyword.lower() in text_content.lower():
                return True
        
        return False
    
    def _deduplicate_tables(self, tables: List[TableData]) -> List[TableData]:
        """去除重複表格"""
        unique_tables = []
        
        for table in tables:
            if not self._is_duplicate_table(table, unique_tables):
                unique_tables.append(table)
            else:
                logger.debug(f"移除重複表格: {table.title}")
        
        return unique_tables
    
    def _is_duplicate_table(self, table: TableData, existing_tables: List[TableData]) -> bool:
        """檢查是否為重複表格"""
        for existing in existing_tables:
            # 檢查頁面和大小
            if (table.source_page == existing.source_page and
                len(table.rows) == len(existing.rows) and
                len(table.headers) == len(existing.headers)):
                
                # 檢查內容相似度
                if self._calculate_table_similarity(table, existing) > 0.8:
                    return True
        
        return False
    
    def _calculate_table_similarity(self, table1: TableData, table2: TableData) -> float:
        """計算表格相似度"""
        # 比較標題
        header_similarity = self._calculate_text_similarity(
            ' '.join(table1.headers), 
            ' '.join(table2.headers)
        )
        
        # 比較第一行資料
        if table1.rows and table2.rows:
            row_similarity = self._calculate_text_similarity(
                ' '.join(table1.rows[0]), 
                ' '.join(table2.rows[0])
            )
        else:
            row_similarity = 0.0
        
        return (header_similarity + row_similarity) / 2
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """計算文本相似度"""
        if not text1 or not text2:
            return 0.0
        
        # 簡單的字符相似度計算
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        
        if not set1 and not set2:
            return 1.0
        elif not set1 or not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def save_tables_to_json(self, tables: List[TableData], output_path: str) -> None:
        """將表格儲存為 JSON 格式"""
        tables_data = [asdict(table) for table in tables]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'extraction_date': datetime.now().isoformat(),
                'total_tables': len(tables),
                'tables': tables_data
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"表格資料已儲存到: {output_path}")
    
    def generate_extraction_report(self, tables: List[TableData]) -> Dict[str, Any]:
        """生成提取報告"""
        report = {
            'total_tables': len(tables),
            'extraction_methods': {},
            'table_types': {},
            'confidence_distribution': {
                'high (>0.8)': 0,
                'medium (0.5-0.8)': 0,
                'low (<0.5)': 0
            },
            'pages_with_tables': set(),
            'average_confidence': 0.0
        }
        
        total_confidence = 0.0
        
        for table in tables:
            # 統計提取方法
            method = table.extractor_method
            report['extraction_methods'][method] = report['extraction_methods'].get(method, 0) + 1
            
            # 統計表格類型
            table_type = table.table_type
            report['table_types'][table_type] = report['table_types'].get(table_type, 0) + 1
            
            # 統計信心度分布
            if table.confidence > 0.8:
                report['confidence_distribution']['high (>0.8)'] += 1
            elif table.confidence >= 0.5:
                report['confidence_distribution']['medium (0.5-0.8)'] += 1
            else:
                report['confidence_distribution']['low (<0.5)'] += 1
            
            # 記錄包含表格的頁面
            report['pages_with_tables'].add(table.source_page)
            
            total_confidence += table.confidence
        
        # 計算平均信心度
        if tables:
            report['average_confidence'] = total_confidence / len(tables)
        
        # 轉換 set 為 list 以便序列化
        report['pages_with_tables'] = sorted(list(report['pages_with_tables']))
        
        return report


def test_table_extractor():
    """測試表格提取器"""
    extractor = AdvancedTableExtractor()
    
    # 測試檔案路徑
    test_pdf = "../data/source/Research-Risk-Report-2025.pdf"
    
    if Path(test_pdf).exists():
        logger.info(f"測試檔案: {test_pdf}")
        
        # 提取表格
        tables = extractor.extract_tables(test_pdf)
        
        # 生成報告
        report = extractor.generate_extraction_report(tables)
        
        logger.info("=== 提取報告 ===")
        logger.info(f"總表格數: {report['total_tables']}")
        logger.info(f"提取方法: {report['extraction_methods']}")
        logger.info(f"表格類型: {report['table_types']}")
        logger.info(f"平均信心度: {report['average_confidence']:.2f}")
        
        # 儲存結果
        extractor.save_tables_to_json(tables, "../data/processed/extracted_tables.json")
        
        return tables, report
    else:
        logger.error(f"測試檔案不存在: {test_pdf}")
        return [], {}


if __name__ == "__main__":
    test_table_extractor() 