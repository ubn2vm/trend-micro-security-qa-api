"""
測試新的資料夾結構
"""

import logging
from pathlib import Path

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def test_structure():
    """測試新的資料夾結構"""
    logger.info("開始測試新的資料夾結構...")
    
    # 檢查 data 目錄
    data_dir = Path("data")
    logger.info(f"data 目錄存在: {data_dir.exists()}")
    
    if data_dir.exists():
        logger.info("data 目錄內容:")
        for item in data_dir.iterdir():
            logger.info(f"  - {item.name} ({'目錄' if item.is_dir() else '檔案'})")
    
    # 檢查 source 目錄
    source_dir = data_dir / "source"
    logger.info(f"source 目錄存在: {source_dir.exists()}")
    
    if source_dir.exists():
        logger.info("source 目錄內容:")
        for item in source_dir.iterdir():
            logger.info(f"  - {item.name} ({'目錄' if item.is_dir() else '檔案'})")
    
    # 檢查 PDF 檔案
    pdf_files = list(source_dir.glob("*.pdf"))
    logger.info(f"找到 {len(pdf_files)} 個 PDF 檔案:")
    for pdf_file in pdf_files:
        logger.info(f"  - {pdf_file.name}")

if __name__ == "__main__":
    test_structure() 