"""
增量更新器的單元測試
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from core_app.rag.incremental_updater import IncrementalRAGUpdater, FileMetadata

class TestIncrementalRAGUpdater:
    """測試增量更新器"""
    
    @pytest.fixture
    def temp_dirs(self):
        """建立臨時目錄"""
        temp_dir = tempfile.mkdtemp()
        data_dir = Path(temp_dir) / "data"
        vector_dir = Path(temp_dir) / "vector_store"
        data_dir.mkdir()
        vector_dir.mkdir()
        
        yield data_dir, vector_dir
        
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def updater(self, temp_dirs):
        """建立測試用的更新器"""
        data_dir, vector_dir = temp_dirs
        return IncrementalRAGUpdater(str(data_dir), str(vector_dir))
    
    def test_init_updater(self, updater):
        """測試更新器初始化"""
        assert updater.data_dir.exists()
        assert updater.vector_dir.exists()
        assert len(updater.processed_files) == 0
    
    def test_calculate_file_hash(self, updater, temp_dirs):
        """測試文件雜湊計算"""
        data_dir, _ = temp_dirs
        test_file = data_dir / "test.txt"
        test_file.write_text("test content")
        
        hash1 = updater._calculate_file_hash(test_file)
        hash2 = updater._calculate_file_hash(test_file)
        
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 雜湊長度
    
    def test_detect_file_changes_new_file(self, updater, temp_dirs):
        """測試新文件檢測"""
        data_dir, _ = temp_dirs
        test_file = data_dir / "test.txt"
        test_file.write_text("test content")
        
        change_info = updater._detect_file_changes(test_file)
        
        assert change_info["status"] == "new"
        assert "新文件" in change_info["changes"]
    
    def test_detect_file_changes_modified_content(self, updater, temp_dirs):
        """測試文件內容變更檢測"""
        data_dir, _ = temp_dirs
        test_file = data_dir / "test.txt"
        test_file.write_text("original content")
        
        # 模擬已處理的文件
        file_hash = updater._calculate_file_hash(test_file)
        updater.processed_files[test_file.name] = FileMetadata(
            filename=test_file.name,
            file_hash=file_hash,
            file_size=test_file.stat().st_size,
            last_modified="2024-01-01T00:00:00",
            processed_date="2024-01-01T00:00:00",
            chunk_count=1,
            source_type="txt",
            version=1
        )
        
        # 修改文件內容
        test_file.write_text("modified content")
        
        change_info = updater._detect_file_changes(test_file)
        
        assert change_info["status"] == "modified"
        assert "文件內容已變更" in change_info["changes"]

def test_file_metadata_serialization():
    """測試文件元資料序列化"""
    metadata = FileMetadata(
        filename="test.pdf",
        file_hash="abc123",
        file_size=1024,
        last_modified="2024-01-01T00:00:00",
        processed_date="2024-01-01T00:00:00",
        chunk_count=10,
        source_type="pdf",
        version=1
    )
    
    # 測試可以轉換為字典
    from dataclasses import asdict
    metadata_dict = asdict(metadata)
    
    assert metadata_dict["filename"] == "test.pdf"
    assert metadata_dict["file_hash"] == "abc123"
    assert metadata_dict["chunk_count"] == 10 