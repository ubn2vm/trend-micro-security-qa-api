"""
RAG 系統增量更新管理器
- 支援新增文件到現有向量資料庫
- 避免重複處理已存在的文件
- 維護文件版本控制
"""

import json
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# 修改這裡：使用系統路徑導入
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from processors.text_processor import CREMTextProcessor
from processors.pdf_processor import extract_pdf_text  # 使用函數而不是類別

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FileMetadata:
    """文件元資料"""
    filename: str
    file_hash: str
    file_size: int
    last_modified: str
    processed_date: str
    chunk_count: int
    source_type: str
    version: int = 1

class IncrementalRAGUpdater:
    """增量 RAG 更新器"""
    
    def __init__(self, data_dir: str, vector_dir: str):
        self.data_dir = Path(data_dir)
        self.vector_dir = Path(vector_dir)
        self.metadata_file = self.data_dir / "processed_files.json"
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.text_processor = CREMTextProcessor()
        # 移除 self.pdf_processor，我們會直接使用函數
        self.processed_files: Dict[str, FileMetadata] = self._load_processed_files()
    
    def _load_processed_files(self) -> Dict[str, FileMetadata]:
        """載入已處理文件的元資料"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {k: FileMetadata(**v) for k, v in data.items()}
        return {}
    
    def _save_processed_files(self) -> None:
        """儲存已處理文件的元資料"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump({k: asdict(v) for k, v in self.processed_files.items()}, f, indent=2)
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """計算文件雜湊值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """獲取文件的詳細資訊"""
        stat = file_path.stat()
        return {
            "file_hash": self._calculate_file_hash(file_path),
            "file_size": stat.st_size,
            "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "filename": file_path.name
        }
    
    def _detect_file_changes(self, file_path: Path) -> Dict[str, Any]:
        """檢測文件變更情況"""
        if not file_path.exists():
            return {"status": "not_found", "changes": ["文件不存在"]}
        
        filename = file_path.name
        current_info = self._get_file_info(file_path)
        
        # 新文件
        if filename not in self.processed_files:
            return {
                "status": "new",
                "changes": ["新文件"],
                "current_info": current_info
            }
        
        old_metadata = self.processed_files[filename]
        changes = []
        
        # 檢查內容變更
        if current_info["file_hash"] != old_metadata.file_hash:
            changes.append("文件內容已變更")
        
        # 檢查檔案大小變更
        if current_info["file_size"] != old_metadata.file_size:
            changes.append("檔案大小已變更")
        
        # 檢查修改時間變更
        if current_info["last_modified"] != old_metadata.last_modified:
            changes.append("修改時間已變更")
        
        if changes:
            return {
                "status": "modified",
                "changes": changes,
                "old_metadata": old_metadata,
                "current_info": current_info
            }
        else:
            return {
                "status": "unchanged",
                "changes": ["文件未變更"],
                "old_metadata": old_metadata,
                "current_info": current_info
            }
    
    def _load_existing_vector_db(self) -> Optional[FAISS]:
        """載入現有的向量資料庫"""
        if (self.vector_dir / "index.faiss").exists():
            logger.info("檢查現有向量資料庫...")
            
            # 檢查檔案完整性
            faiss_file = self.vector_dir / "index.faiss"
            pkl_file = self.vector_dir / "index.pkl"
            
            if not faiss_file.exists() or not pkl_file.exists():
                logger.warning("向量資料庫檔案不完整，將建立新的")
                return None
            
            try:
                # 嘗試載入
                vector_db = FAISS.load_local(
                    str(self.vector_dir), 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("✅ 成功載入現有向量資料庫")
                return vector_db
                
            except Exception as e:
                logger.warning(f"載入向量資料庫失敗: {e}")
                logger.info("將建立新的向量資料庫，但保留文件處理記錄")
                return None
        
        logger.info("沒有找到現有向量資料庫，將建立新的")
        return None
    
    def _process_file(self, file_path: Path) -> List[Document]:
        """處理文件並返回分塊"""
        logger.info(f"處理文件: {file_path.name}")
        
        if file_path.suffix.lower() == '.pdf':
            # 處理 PDF 文件 - 使用函數而不是類別
            try:
                extracted_text = extract_pdf_text(str(file_path))
                cleaned_text = self.text_processor.clean_text(extracted_text)
                chunks = self.text_processor.chunk_text(cleaned_text)
            except Exception as e:
                logger.error(f"PDF 處理失敗: {e}")
                # 如果 PDF 處理失敗，嘗試使用 pdfplumber 直接處理
                import pdfplumber
                try:
                    with pdfplumber.open(file_path) as pdf:
                        text_parts = []
                        for page in pdf.pages:
                            text = page.extract_text()
                            if text:
                                text_parts.append(text)
                        extracted_text = '\n\n'.join(text_parts)
                        cleaned_text = self.text_processor.clean_text(extracted_text)
                        chunks = self.text_processor.chunk_text(cleaned_text)
                except Exception as e2:
                    logger.error(f"備用 PDF 處理也失敗: {e2}")
                    return []
        else:
            # 處理文本文件
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            cleaned_text = self.text_processor.clean_text(text)
            chunks = self.text_processor.chunk_text(cleaned_text)
        
        # 更新元資料
        for chunk in chunks:
            chunk.metadata['source'] = file_path.name
            chunk.metadata['processed_date'] = datetime.now().isoformat()
        
        return chunks
    
    def update_knowledge_base(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """增量更新知識庫"""
        logger.info("開始增量更新知識庫...")
        
        # 載入現有向量資料庫
        vector_db = self._load_existing_vector_db()
        
        if force_rebuild:
            logger.info("強制重建模式：清除所有處理記錄")
            self.processed_files.clear()
            vector_db = None
        elif vector_db is None:
            logger.info("無法載入現有向量資料庫，但保留文件處理記錄")
            # 不刪除 processed_files，保持增量記錄
        
        # 掃描 data/source 目錄中的文件
        source_dir = self.data_dir / "source"
        if not source_dir.exists():
            logger.warning(f"源資料目錄不存在: {source_dir}")
            source_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"已建立源資料目錄: {source_dir}")
        
        all_files = [f for f in source_dir.glob("*") 
                    if f.is_file() and f.suffix.lower() in ['.pdf', '.txt']]
        
        # 檢測文件變更
        file_changes = {}
        files_to_process = []
        
        for file_path in all_files:
            change_info = self._detect_file_changes(file_path)
            file_changes[file_path.name] = change_info
            
            if change_info["status"] in ["new", "modified"]:
                files_to_process.append(file_path)
                logger.info(f"檢測到變更: {file_path.name} - {', '.join(change_info['changes'])}")
            elif change_info["status"] == "unchanged":
                logger.info(f"文件未變更: {file_path.name}")
        
        if not files_to_process and not force_rebuild:
            logger.info("沒有文件需要處理")
            return {
                "status": "no_updates_needed", 
                "processed_files": 0,
                "new_chunks": 0,
                "total_files": len(self.processed_files),
                "vector_count": vector_db.index.ntotal if vector_db else 0,
                "file_changes": file_changes
            }
        
        # 處理需要更新的文件
        all_new_chunks = []
        processed_count = 0
        
        for file_path in files_to_process:
            try:
                chunks = self._process_file(file_path)
                all_new_chunks.extend(chunks)
                
                # 更新文件元資料
                current_info = file_changes[file_path.name]["current_info"]
                old_metadata = file_changes[file_path.name].get("old_metadata")
                
                new_version = 1
                if old_metadata:
                    new_version = old_metadata.version + 1
                
                self.processed_files[file_path.name] = FileMetadata(
                    filename=file_path.name,
                    file_hash=current_info["file_hash"],
                    file_size=current_info["file_size"],
                    last_modified=current_info["last_modified"],
                    processed_date=datetime.now().isoformat(),
                    chunk_count=len(chunks),
                    source_type=file_path.suffix.lower()[1:],
                    version=new_version
                )
                
                processed_count += 1
                logger.info(f"成功處理 {file_path.name} (版本 {new_version}): {len(chunks)} 個分塊")
                
            except Exception as e:
                logger.error(f"處理文件 {file_path.name} 時發生錯誤: {e}")
                continue
        
        # 更新向量資料庫
        if all_new_chunks:
            if vector_db is None:
                logger.info("建立新的向量資料庫...")
                vector_db = FAISS.from_documents(all_new_chunks, self.embeddings)
            else:
                logger.info(f"將 {len(all_new_chunks)} 個新分塊加入現有向量資料庫...")
                vector_db.add_documents(all_new_chunks)
            
            # 儲存更新後的向量資料庫
            self.vector_dir.mkdir(parents=True, exist_ok=True)
            vector_db.save_local(str(self.vector_dir))
            
            # 儲存文件元資料
            self._save_processed_files()
        
        # 統計資訊
        stats = {
            "status": "updated",
            "processed_files": processed_count,
            "new_chunks": len(all_new_chunks),
            "total_files": len(self.processed_files),
            "vector_count": vector_db.index.ntotal if vector_db else 0,
            "vector_dim": vector_db.index.d if vector_db else 0,
            "file_changes": file_changes
        }
        
        logger.info(f"增量更新完成: {stats}")
        return stats
    
    def get_processed_files_info(self) -> Dict[str, Any]:
        """獲取已處理文件的詳細資訊"""
        return {
            "total_files": len(self.processed_files),
            "files": [asdict(metadata) for metadata in self.processed_files.values()]
        }

def incremental_update_knowledge_base():
    """執行增量更新知識庫"""
    data_dir = "data"
    vector_dir = "vector_store/crem_faiss_index"
    
    updater = IncrementalRAGUpdater(data_dir, vector_dir)
    stats = updater.update_knowledge_base()
    
    logger.info("=== 增量更新完成 ===")
    logger.info(f"狀態: {stats['status']}")
    logger.info(f"處理文件數: {stats['processed_files']}")
    logger.info(f"新分塊數: {stats['new_chunks']}")
    logger.info(f"總文件數: {stats['total_files']}")
    logger.info(f"向量數量: {stats['vector_count']}")
    
    return stats

if __name__ == "__main__":
    incremental_update_knowledge_base() 