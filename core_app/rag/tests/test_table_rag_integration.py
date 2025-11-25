"""
表格RAG整合端到端測試
驗證從表格提取到查詢的完整流程
"""

import sys
import unittest
import logging
from pathlib import Path

# 添加模組路徑
sys.path.append(str(Path(__file__).parent.parent))

from processors.table_text_converter import TableTextConverter
from tools.table_vector_integrator import TableVectorIntegrator 
from tools.unified_query_engine import UnifiedQueryEngine

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestTableRAGIntegration(unittest.TestCase):
    """表格RAG整合測試"""
    
    def setUp(self):
        """測試設定"""
        self.test_data_dir = Path("data/processed")
        self.test_vector_dir = Path("vector_store/default_faiss_index")
        
        # 測試檔案路徑
        self.extracted_tables_file = self.test_data_dir / "extracted_tables.json"
        self.table_texts_file = self.test_data_dir / "table_texts.json"
        
        logger.info("設定測試環境...")
    
    def test_01_table_extraction_exists(self):
        """測試1：驗證表格提取檔案存在"""
        logger.info("📋 測試1：檢查表格提取檔案...")
        
        self.assertTrue(
            self.extracted_tables_file.exists(), 
            f"表格提取檔案不存在: {self.extracted_tables_file}"
        )
        
        # 檢查檔案內容
        import json
        with open(self.extracted_tables_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIn("tables", data, "表格資料結構不正確")
        self.assertGreater(len(data["tables"]), 0, "沒有表格資料")
        
        logger.info(f"✅ 找到 {len(data['tables'])} 個表格")
    
    def test_02_table_text_conversion(self):
        """測試2：驗證表格文本轉換功能"""
        logger.info("🔄 測試2：表格文本轉換...")
        
        converter = TableTextConverter()
        
        # 執行轉換
        converted_tables = converter.convert_tables_json_to_text(
            str(self.extracted_tables_file),
            str(self.table_texts_file)
        )
        
        # 驗證結果
        self.assertGreater(len(converted_tables), 0, "沒有轉換任何表格")
        self.assertTrue(self.table_texts_file.exists(), "表格文本檔案未建立")
        
        # 驗證轉換品質
        stats = converter.get_conversion_stats()
        self.assertEqual(
            stats["total_tables"], 
            stats["converted_tables"], 
            "並非所有表格都成功轉換"
        )
        
        logger.info(f"✅ 成功轉換 {len(converted_tables)} 個表格")
    
    def test_03_vector_integration(self):
        """測試3：驗證向量資料庫整合"""
        logger.info("🔗 測試3：向量資料庫整合...")
        
        integrator = TableVectorIntegrator(str(self.test_vector_dir))
        
        # 執行整合
        stats = integrator.integrate_tables_to_vector_db(str(self.table_texts_file))
        
        # 驗證結果
        self.assertGreater(stats["integrated_tables"], 0, "沒有整合任何表格")
        self.assertGreater(stats["vector_count_after"], stats["vector_count_before"], "向量數沒有增加")
        
        logger.info(f"✅ 整合 {stats['integrated_tables']} 個表格，向量數: {stats['vector_count_before']} → {stats['vector_count_after']}")
    
    def test_04_unified_query_functionality(self):
        """測試4：驗證統一查詢功能"""
        logger.info("🔍 測試4：統一查詢功能...")
        
        engine = UnifiedQueryEngine(str(self.test_vector_dir))
        
        # 測試載入向量資料庫
        self.assertTrue(engine.load_vector_db(), "無法載入向量資料庫")
        
        # 測試不同類型的查詢
        test_cases = [
            ("風險事件", "all", "混合查詢"),
            ("table", "table", "表格專用查詢"), 
            ("security policy", "text", "文本專用查詢")
        ]
        
        for query, filter_type, description in test_cases:
            logger.info(f"   測試 {description}: '{query}'")
            
            results = engine.query(query, k=3, filter_type=filter_type)
            
            # 驗證結果
            self.assertIsInstance(results, list, f"{description} 沒有返回列表")
            
            if filter_type == "table":
                # 表格查詢應該只返回表格結果
                for result in results:
                    self.assertEqual(result.content_type, "table", "表格查詢返回了非表格結果")
            elif filter_type == "text":
                # 文本查詢應該只返回文本結果
                for result in results:
                    self.assertEqual(result.content_type, "text", "文本查詢返回了非文本結果")
            
            logger.info(f"     找到 {len(results)} 個結果")
        
        logger.info("✅ 所有查詢測試通過")
    
    def test_05_table_search_quality(self):
        """測試5：驗證表格搜尋品質"""
        logger.info("📊 測試5：表格搜尋品質...")
        
        engine = UnifiedQueryEngine(str(self.test_vector_dir))
        engine.load_vector_db()
        
        # 測試表格特定查詢
        table_queries = [
            "risky events",
            "統計資料", 
            "數據分析",
            "comparison table"
        ]
        
        total_table_results = 0
        
        for query in table_queries:
            results = engine.search_tables_only(query, k=2)
            table_results = [r for r in results if r.content_type == "table"]
            total_table_results += len(table_results)
            
            logger.info(f"   查詢 '{query}': 找到 {len(table_results)} 個表格結果")
        
        # 驗證至少找到一些表格結果
        self.assertGreater(total_table_results, 0, "表格搜尋沒有找到任何表格結果")
        
        logger.info(f"✅ 總共找到 {total_table_results} 個表格搜尋結果")
    
    def test_06_system_performance(self):
        """測試6：驗證系統效能"""
        logger.info("⚡ 測試6：系統效能...")
        
        engine = UnifiedQueryEngine(str(self.test_vector_dir))
        engine.load_vector_db()
        
        # 測試查詢速度
        import time
        
        start_time = time.time()
        results = engine.query("風險管理", k=5)
        end_time = time.time()
        
        query_time = end_time - start_time
        
        # 驗證查詢時間合理（應該在幾秒內）
        self.assertLess(query_time, 10.0, f"查詢時間過長: {query_time:.2f}秒")
        self.assertGreater(len(results), 0, "沒有查詢結果")
        
        logger.info(f"✅ 查詢時間: {query_time:.2f}秒，找到 {len(results)} 個結果")
    
    def test_07_integration_completeness(self):
        """測試7：驗證整合完整性"""
        logger.info("🔍 測試7：整合完整性檢查...")
        
        # 檢查所有必要檔案
        required_files = [
            self.extracted_tables_file,
            self.table_texts_file,
            self.test_vector_dir / "index.faiss",
            self.test_vector_dir / "index.pkl"
        ]
        
        for file_path in required_files:
            self.assertTrue(file_path.exists(), f"必要檔案不存在: {file_path}")
        
        # 檢查向量資料庫
        engine = UnifiedQueryEngine(str(self.test_vector_dir))
        self.assertTrue(engine.load_vector_db(), "向量資料庫載入失敗")
        
        stats = engine.get_query_stats()
        self.assertGreater(stats["vector_count"], 200, "向量資料庫規模不足")  # 應該有文本+表格向量
        
        logger.info(f"✅ 系統完整性檢查通過，向量數: {stats['vector_count']}")


def run_table_rag_tests():
    """執行表格RAG整合測試"""
    print("=" * 80)
    print("🚀 表格RAG系統端到端測試")
    print("=" * 80)
    
    # 建立測試套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTableRAGIntegration)
    
    # 執行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 測試摘要
    print("\n" + "=" * 80)
    print("📊 測試摘要")
    print("=" * 80)
    print(f"總測試數: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失敗: {len(result.failures)}")
    print(f"錯誤: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ 失敗的測試:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 錯誤的測試:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n🎯 成功率: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 所有測試通過！表格RAG系統運作正常！")
    elif success_rate >= 80:
        print("✅ 大部分測試通過，系統基本功能正常")
    else:
        print("⚠️ 多個測試失敗，需要檢查系統問題")
    
    return result


if __name__ == "__main__":
    # 執行測試
    run_table_rag_tests() 