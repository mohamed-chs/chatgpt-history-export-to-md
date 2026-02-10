"""Tests for the writers module."""

from datetime import UTC, datetime
from pathlib import Path

from convoviz.config import (
    AuthorHeaders,
    ConversationConfig,
    FolderOrganization,
    YAMLConfig,
)
from convoviz.io.writers import get_date_folder_path, save_collection, save_conversation
from convoviz.models import Conversation, ConversationCollection


def create_conversation(
    title: str,
    create_time: datetime,
    conversation_id: str,
) -> Conversation:
    """Create a minimal conversation for testing."""
    return Conversation(
        title=title,
        create_time=create_time,
        update_time=create_time,
        mapping={
            "root": {
                "id": "root",
                "message": None,
                "parent": None,
                "children": ["user_node"],
            },
            "user_node": {
                "id": "user_node",
                "message": {
                    "id": "user_node",
                    "author": {"role": "user", "metadata": {}},
                    "create_time": create_time.timestamp(),
                    "update_time": create_time.timestamp(),
                    "content": {"content_type": "text", "parts": ["Hello"]},
                    "status": "finished_successfully",
                    "end_turn": True,
                    "weight": 1.0,
                    "metadata": {},
                    "recipient": "all",
                },
                "parent": "root",
                "children": [],
            },
        },
        current_node="user_node",
        conversation_id=conversation_id,
    )


class TestGetDateFolderPath:
    """Tests for get_date_folder_path function."""

    def test_january(self) -> None:
        """Test path for early January date."""
        conv = create_conversation(
            "Test",
            datetime(2024, 1, 3, 10, 0, tzinfo=UTC),
            "test1",
        )
        path = get_date_folder_path(conv)
        assert path == Path("2024/01-January")

    def test_january_late(self) -> None:
        """Test path for late January (same month folder)."""
        conv = create_conversation(
            "Test",
            datetime(2024, 1, 28, 10, 0, tzinfo=UTC),
            "test2",
        )
        path = get_date_folder_path(conv)
        assert path == Path("2024/01-January")

    def test_march(self) -> None:
        """Test path for mid-March date."""
        conv = create_conversation(
            "Test",
            datetime(2024, 3, 18, 10, 0, tzinfo=UTC),
            "test3",
        )
        path = get_date_folder_path(conv)
        assert path == Path("2024/03-March")

    def test_december(self) -> None:
        """Test path for end of December."""
        conv = create_conversation(
            "Test",
            datetime(2024, 12, 30, 10, 0, tzinfo=UTC),
            "test4",
        )
        path = get_date_folder_path(conv)
        assert path == Path("2024/12-December")

    def test_different_years(self) -> None:
        """Test that different years produce different paths."""
        conv_2023 = create_conversation(
            "Test",
            datetime(2023, 6, 15, 10, 0, tzinfo=UTC),
            "test5",
        )
        conv_2024 = create_conversation(
            "Test",
            datetime(2024, 6, 15, 10, 0, tzinfo=UTC),
            "test6",
        )
        assert get_date_folder_path(conv_2023) == Path("2023/06-June")
        assert get_date_folder_path(conv_2024) == Path("2024/06-June")


class TestSaveCollectionWithDateOrganization:
    """Tests for save_collection with date organization."""

    def test_flat_organization(self, tmp_path: Path) -> None:
        """Test that flat organization puts all files in root directory."""
        conv1 = create_conversation(
            "Conv Jan",
            datetime(2024, 1, 5, 10, 0, tzinfo=UTC),
            "conv1",
        )
        conv2 = create_conversation(
            "Conv Mar",
            datetime(2024, 3, 15, 10, 0, tzinfo=UTC),
            "conv2",
        )
        collection = ConversationCollection(conversations=[conv1, conv2])

        save_collection(
            collection,
            tmp_path,
            ConversationConfig(),
            AuthorHeaders(),
            folder_organization=FolderOrganization.FLAT,
        )

        # Files should be in root directory
        assert (tmp_path / "Conv Jan.md").exists()
        assert (tmp_path / "Conv Mar.md").exists()

    def test_date_organization(self, tmp_path: Path) -> None:
        """Test that date organization creates nested folders."""
        conv1 = create_conversation(
            "Conv Jan",
            datetime(2024, 1, 5, 10, 0, tzinfo=UTC),
            "conv1",
        )
        conv2 = create_conversation(
            "Conv Mar",
            datetime(2024, 3, 15, 10, 0, tzinfo=UTC),
            "conv2",
        )
        collection = ConversationCollection(conversations=[conv1, conv2])

        save_collection(
            collection,
            tmp_path,
            ConversationConfig(),
            AuthorHeaders(),
            folder_organization=FolderOrganization.DATE,
        )

        # Files should be in date folders (year/month, no week)
        assert (tmp_path / "2024" / "01-January" / "Conv Jan.md").exists()
        assert (tmp_path / "2024" / "03-March" / "Conv Mar.md").exists()

    def test_date_organization_multiple_same_month(self, tmp_path: Path) -> None:
        """Test multiple conversations in the same month."""
        conv1 = create_conversation(
            "Early Month Chat",
            datetime(2024, 3, 8, 10, 0, tzinfo=UTC),
            "conv1",
        )
        conv2 = create_conversation(
            "Late Month Chat",
            datetime(2024, 3, 22, 10, 0, tzinfo=UTC),
            "conv2",
        )
        collection = ConversationCollection(conversations=[conv1, conv2])

        save_collection(
            collection,
            tmp_path,
            ConversationConfig(),
            AuthorHeaders(),
            folder_organization=FolderOrganization.DATE,
        )

        # Both should be in the same month folder
        month_folder = tmp_path / "2024" / "03-March"
        assert (month_folder / "Early Month Chat.md").exists()
        assert (month_folder / "Late Month Chat.md").exists()

    def test_date_organization_different_years(self, tmp_path: Path) -> None:
        """Test conversations spanning different years."""
        conv_2023 = create_conversation(
            "Old Chat",
            datetime(2023, 12, 20, 10, 0, tzinfo=UTC),
            "conv1",
        )
        conv_2024 = create_conversation(
            "New Chat",
            datetime(2024, 1, 5, 10, 0, tzinfo=UTC),
            "conv2",
        )
        collection = ConversationCollection(conversations=[conv_2023, conv_2024])

        save_collection(
            collection,
            tmp_path,
            ConversationConfig(),
            AuthorHeaders(),
            folder_organization=FolderOrganization.DATE,
        )

        assert (tmp_path / "2023" / "12-December" / "Old Chat.md").exists()
        assert (tmp_path / "2024" / "01-January" / "New Chat.md").exists()

    def test_date_organization_generates_index_files(self, tmp_path: Path) -> None:
        """Test that date organization generates _index.md files."""
        conv1 = create_conversation(
            "Chat One",
            datetime(2024, 1, 5, 10, 0, tzinfo=UTC),
            "conv1",
        )
        conv2 = create_conversation(
            "Chat Two",
            datetime(2024, 1, 15, 10, 0, tzinfo=UTC),
            "conv2",
        )
        conv3 = create_conversation(
            "Chat Three",
            datetime(2024, 3, 10, 10, 0, tzinfo=UTC),
            "conv3",
        )
        collection = ConversationCollection(conversations=[conv1, conv2, conv3])

        save_collection(
            collection,
            tmp_path,
            ConversationConfig(),
            AuthorHeaders(),
            folder_organization=FolderOrganization.DATE,
        )

        # Check year index
        year_index = tmp_path / "2024" / "_index.md"
        assert year_index.exists()
        year_content = year_index.read_text()
        assert "# 2024" in year_content
        assert "[January]" in year_content
        assert "[March]" in year_content

        # Check month index
        jan_index = tmp_path / "2024" / "01-January" / "_index.md"
        assert jan_index.exists()
        jan_content = jan_index.read_text()
        assert "# January 2024" in jan_content
        assert "[Chat One]" in jan_content
        assert "[Chat Two]" in jan_content

    def test_index_uses_original_title(self, tmp_path: Path) -> None:
        """Test that _index.md uses the original title even if filename is sanitized."""
        original_title = "My @Title's Case"
        # Sanitize would be "My Title s Case" (since @ removed, ' replaced by space)
        conv = create_conversation(
            original_title,
            datetime(2024, 1, 5, 10, 0, tzinfo=UTC),
            "conv1",
        )
        collection = ConversationCollection(conversations=[conv])

        save_collection(
            collection,
            tmp_path,
            ConversationConfig(),
            AuthorHeaders(),
            folder_organization=FolderOrganization.DATE,
        )

        jan_index = tmp_path / "2024" / "01-January" / "_index.md"
        assert jan_index.exists()
        jan_content = jan_index.read_text()

        # Link should be [Original Title](sanitized_filename.md)
        # Sanitized filename: "My Title s Case.md" (quoted)
        expected_link = f"[{original_title}](My%20Title%20s%20Case.md)"
        assert expected_link in jan_content

    def test_flat_organization_no_index_files(self, tmp_path: Path) -> None:
        """Test that flat organization does not generate index files."""
        conv = create_conversation(
            "Test Chat",
            datetime(2024, 1, 5, 10, 0, tzinfo=UTC),
            "conv1",
        )
        collection = ConversationCollection(conversations=[conv])

        save_collection(
            collection,
            tmp_path,
            ConversationConfig(),
            AuthorHeaders(),
            folder_organization=FolderOrganization.FLAT,
        )

        # No index files should be created in flat mode
        assert not (tmp_path / "_index.md").exists()
        assert not list(tmp_path.glob("**/_index.md"))

    def test_prepend_timestamp_to_filename(self, tmp_path: Path) -> None:
        """Test that timestamps are prepended to filenames when requested."""
        conv = create_conversation(
            "My Chat",
            datetime(2024, 3, 21, 15, 30, 5, tzinfo=UTC),
            "conv1",
        )
        collection = ConversationCollection(conversations=[conv])

        save_collection(
            collection,
            tmp_path,
            ConversationConfig(),
            AuthorHeaders(),
            folder_organization=FolderOrganization.FLAT,
            prepend_timestamp=True,
        )

        expected_filename = "2024-03-21_15-30-05 - My Chat.md"
        assert (tmp_path / expected_filename).exists()


def test_save_conversation_overwrite_with_large_frontmatter(tmp_path: Path) -> None:
    """Ensure conversation ID detection works even with large frontmatter."""
    ts = datetime(2024, 1, 1, 10, 0, tzinfo=UTC)
    large_text = "x" * 6000
    conv = Conversation(
        title="Big YAML",
        create_time=ts,
        update_time=ts,
        mapping={
            "root": {
                "id": "root",
                "message": None,
                "parent": None,
                "children": ["sys_node"],
            },
            "sys_node": {
                "id": "sys_node",
                "message": {
                    "id": "sys_node",
                    "author": {"role": "system", "metadata": {}},
                    "create_time": ts.timestamp(),
                    "update_time": ts.timestamp(),
                    "content": {"content_type": "text", "parts": ["System"]},
                    "status": "finished_successfully",
                    "end_turn": True,
                    "weight": 1.0,
                    "metadata": {
                        "is_user_system_message": True,
                        "user_context_message_data": {"about_user": large_text},
                    },
                    "recipient": "all",
                },
                "parent": "root",
                "children": ["user_node"],
            },
            "user_node": {
                "id": "user_node",
                "message": {
                    "id": "user_node",
                    "author": {"role": "user", "metadata": {}},
                    "create_time": ts.timestamp(),
                    "update_time": ts.timestamp(),
                    "content": {"content_type": "text", "parts": ["Hello"]},
                    "status": "finished_successfully",
                    "end_turn": True,
                    "weight": 1.0,
                    "metadata": {},
                    "recipient": "all",
                },
                "parent": "sys_node",
                "children": [],
            },
        },
        current_node="user_node",
        conversation_id="big_yaml_conv",
    )

    config = ConversationConfig(yaml=YAMLConfig(custom_instructions=True))
    headers = AuthorHeaders()
    path = tmp_path / "Big YAML.md"

    save_conversation(conv, path, config, headers)
    save_conversation(conv, path, config, headers)

    assert path.exists()
    assert not (tmp_path / "Big YAML (1).md").exists()


class TestSaveConversation:
    """Tests for save_conversation function."""

    def test_save_creates_file(self, tmp_path: Path) -> None:
        """Test that save_conversation creates a file."""
        conv = create_conversation(
            "Test Conv",
            datetime(2024, 1, 5, 10, 0, tzinfo=UTC),
            "conv1",
        )
        filepath = tmp_path / "test.md"

        result = save_conversation(
            conv,
            filepath,
            ConversationConfig(),
            AuthorHeaders(),
        )

        assert result.exists()
        assert result == filepath

    def test_save_handles_conflict_different_id(self, tmp_path: Path) -> None:
        """Test that same title but different ID results in increments."""
        # Save first conversation
        conv1 = create_conversation(
            "Test Conv",
            datetime(2024, 1, 5, 10, 0, tzinfo=UTC),
            "id1",
        )
        filepath = tmp_path / "test.md"
        save_conversation(conv1, filepath, ConversationConfig(), AuthorHeaders())

        # Save second conversation with SAME title but DIFFERENT id
        conv2 = create_conversation(
            "Test Conv",
            datetime(2024, 1, 5, 10, 0, tzinfo=UTC),
            "id2",
        )
        result = save_conversation(
            conv2,
            filepath,
            ConversationConfig(),
            AuthorHeaders(),
        )

        # Should increment
        assert result.name == "test (1).md"
        assert filepath.exists()

    def test_save_overwrites_same_identity(self, tmp_path: Path) -> None:
        """Test that same title AND same ID results in overwrite."""
        # Save first version
        conv1 = create_conversation(
            "Test Conv",
            datetime(2024, 1, 5, 10, 0, tzinfo=UTC),
            "id1",
        )
        filepath = tmp_path / "test.md"
        save_conversation(conv1, filepath, ConversationConfig(), AuthorHeaders())

        assert "Hello" in filepath.read_text()

        # Update it (e.g. change content in mock)
        conv1_updated = create_conversation(
            "Test Conv",
            datetime(2024, 1, 5, 10, 0, tzinfo=UTC),
            "id1",
        )
        # Use a completely different content to check overwrite
        conv1_updated.mapping["user_node"].message.content.parts = ["Something Else"]

        result = save_conversation(
            conv1_updated,
            filepath,
            ConversationConfig(),
            AuthorHeaders(),
        )

        # Should OVERWRITE (same path, no counter)
        assert result == filepath
        assert "Something Else" in filepath.read_text()
        assert "Hello" not in filepath.read_text()
