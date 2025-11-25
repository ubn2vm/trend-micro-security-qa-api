from pathlib import Path

import pytest

from scripts.init_rag import check_documents


def test_check_documents_reports_existing_and_missing(tmp_path: Path) -> None:
    """檢查只提供單一 PDF 時的已存在與缺失列表"""
    (tmp_path / "ddi_6.8.sp1_ag.pdf").write_text("demo pdf")

    existing, missing = check_documents(tmp_path)

    assert [doc for doc, _ in existing] == ["ddi_6.8.sp1_ag.pdf"]
    assert missing == ["ddi_6.8.sp1_syslog.pdf"]


def test_check_documents_records_file_size(tmp_path: Path) -> None:
    """驗證返回的已存在清單包含檔案大小資訊"""
    sample = tmp_path / "ddi_6.8.sp1_syslog.pdf"
    sample.write_bytes(b"x" * 1024)

    existing, missing = check_documents(tmp_path)

    assert missing == ["ddi_6.8.sp1_ag.pdf"]
    assert existing[0][0] == "ddi_6.8.sp1_syslog.pdf"
    assert existing[0][1] >= 0.0009  # 大約 1KB

