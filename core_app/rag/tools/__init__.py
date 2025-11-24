"""
RAG 系統工具模組
包含知識庫更新和管理工具
"""

from .incremental_updater import IncrementalRAGUpdater
from .vector_db_builder import VectorDatabaseBuilder
# 向後兼容：保留舊的類名別名
from .vector_db_builder import VectorDatabaseBuilder as KnowledgeBaseBuilder

__all__ = [
    'IncrementalRAGUpdater',
    'VectorDatabaseBuilder',
    'KnowledgeBaseBuilder',  # 向後兼容別名
] 