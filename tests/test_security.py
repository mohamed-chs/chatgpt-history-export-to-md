import io
from zipfile import ZipFile

import pytest

from convoviz.config import ConvovizConfig
from convoviz.exceptions import InvalidZipError
from convoviz.io.loaders import extract_archive
from convoviz.pipeline import run_pipeline
from convoviz.utils import sanitize


def test_zip_slip_protection(tmp_path):
    # Create a malicious ZIP file in memory
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, "w") as zf:
        # Try to extract outside the folder
        zf.writestr("../evil.txt", "malicious content")
        # Windows-style traversal should also be rejected (even on POSIX)
        zf.writestr("..\\evil2.txt", "malicious content")

    zip_path = tmp_path / "malicious.zip"
    zip_path.write_bytes(zip_buffer.getvalue())

    with pytest.raises(InvalidZipError, match="Malicious path in ZIP"):
        extract_archive(zip_path, tmp_path / "extracted")


def test_zip_slip_protection_absolute_and_drive_paths(tmp_path):
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, "w") as zf:
        zf.writestr("/abs.txt", "malicious content")
        zf.writestr("C:\\evil.txt", "malicious content")
        zf.writestr("\\\\server\\share\\evil.txt", "malicious content")

    zip_path = tmp_path / "malicious_abs.zip"
    zip_path.write_bytes(zip_buffer.getvalue())

    with pytest.raises(InvalidZipError, match="Malicious path in ZIP"):
        extract_archive(zip_path, tmp_path / "extracted")


def test_sanitize_path_traversal():
    assert sanitize("../../etc/passwd") == "etc passwd"
    assert sanitize("..\\..\\windows\\system32") == "windows system32"


def test_sanitize_reserved_names():
    assert sanitize("CON") == "_CON_"
    assert sanitize("aux") == "_aux_"


def test_safe_directory_management(tmp_path):
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    keeper_file = output_dir / "keeper.txt"
    keeper_file.write_text("I should stay")

    # Create managed dirs to be replaced
    markdown_dir = output_dir / "Markdown"
    markdown_dir.mkdir()
    old_file = markdown_dir / "old.md"
    old_file.write_text("I should be deleted")

    # Minimal config to run pipeline
    # We need a dummy input
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    conv_json = input_dir / "conversations.json"
    conv_json.write_text("[]")

    config = ConvovizConfig(input_path=str(input_dir), output_folder=output_dir)

    run_pipeline(config)

    assert keeper_file.exists()
    assert keeper_file.read_text() == "I should stay"
    # New behavior: additive, so old_file should STILL exist
    assert old_file.exists()
    assert old_file.read_text() == "I should be deleted"
    assert (output_dir / "Markdown").exists()
