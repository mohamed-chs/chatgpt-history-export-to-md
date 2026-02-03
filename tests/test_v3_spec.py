from datetime import datetime

from convoviz.config import YAMLConfig
from convoviz.models import Conversation
from convoviz.models.message import Message, MessageAuthor, MessageContent, MessageMetadata
from convoviz.renderers.markdown import replace_citations
from convoviz.renderers.yaml import render_yaml_header


class TestContentFiltering:
    def test_sonic_webpage_hidden(self):
        msg = Message(
            id="1",
            author=MessageAuthor(role="tool", name="web.search"),
            content=MessageContent(content_type="sonic_webpage", text="Scraped text"),
            status="finished_successfully",
            weight=1.0,
            metadata=MessageMetadata(),
        )
        assert msg.is_hidden

    def test_bio_tool_hidden(self):
        msg = Message(
            id="2",
            author=MessageAuthor(role="tool", name="bio"),
            content=MessageContent(content_type="text", text="Memory update"),
            status="finished_successfully",
            weight=1.0,
            metadata=MessageMetadata(),
        )
        assert msg.is_hidden

    def test_web_run_tool_hidden(self):
        msg = Message(
            id="3",
            author=MessageAuthor(role="tool", name="web.run"),
            content=MessageContent(content_type="text", text="Orchestration"),
            status="finished_successfully",
            weight=1.0,
            metadata=MessageMetadata(),
        )
        assert msg.is_hidden

    def test_browser_tool_tether_quote_visible(self):
        msg = Message(
            id="4",
            author=MessageAuthor(role="tool", name="browser"),
            content=MessageContent(content_type="tether_quote", text="Citation quote"),
            status="finished_successfully",
            weight=1.0,
            metadata=MessageMetadata(),
        )
        assert not msg.is_hidden

    def test_browser_tool_other_hidden(self):
        msg = Message(
            id="5",
            author=MessageAuthor(role="tool", name="browser"),
            content=MessageContent(content_type="execution_output", text="Searching..."),
            status="finished_successfully",
            weight=1.0,
            metadata=MessageMetadata(),
        )
        assert msg.is_hidden

    def test_dalle_status_hidden(self):
        msg = Message(
            id="6",
            author=MessageAuthor(role="tool", name="dalle.text2im"),
            content=MessageContent(content_type="text", text="DALL·E displayed 1 images..."),
            status="finished_successfully",
            weight=1.0,
            metadata=MessageMetadata(),
        )
        assert msg.is_hidden


class TestCitationParsing:
    def test_replace_citations(self):
        text = "This is a claim 【172†source】 and another 【173†source】."
        citations = [
            {
                "start_ix": 16,
                "end_ix": 28,
                "metadata": {"title": "Source 1", "url": "http://example.com/1"},
            },
            {
                "start_ix": 41,
                "end_ix": 53,
                "metadata": {"url": "http://example.com/2"},  # No title
            },
        ]

        result = replace_citations(text, citations)
        # Expected: "This is a claim [[Source 1](http://example.com/1)] and another [[Source](http://example.com/2)]."
        assert "[[Source 1](http://example.com/1)]" in result
        assert "[[Source](http://example.com/2)]" in result
        assert "【172†source】" not in result

    def test_replace_embedded_citations(self):
        # \uE200cite\uE202turn0search18\uE201
        text = "Check this source: \ue200cite\ue202turn0search18\ue201."
        citation_map = {
            "turn0search18": {"title": "My Source", "url": "http://example.com/embedded"}
        }

        result = replace_citations(text, citation_map=citation_map)
        assert "[[My Source](http://example.com/embedded)]" in result
        assert "\ue200" not in result

    def test_replace_embedded_citations_multiple(self):
        # \uE200cite\uE202key1\uE202key2\uE201
        text = "Sources: \ue200cite\ue202key1\ue202key2\ue201"
        citation_map = {
            "key1": {"title": "S1", "url": "http://s1.com"},
            "key2": {"title": "S2", "url": "http://s2.com"},
        }
        result = replace_citations(text, citation_map=citation_map)
        assert "[[S1](http://s1.com)]" in result
        assert "[[S2](http://s2.com)]" in result
        # Check adjacent spacing/concatenation
        # Expected: "Sources:  [[S1](http://s1.com)] [[S2](http://s2.com)]"
        assert "[[S1](http://s1.com)][[S2](http://s2.com)]" in result.replace(" ", "")


class TestMetadataEnrichment:
    def test_render_yaml_header_new_fields(self):
        conv = Conversation(
            title="Test",
            create_time=datetime(2026, 2, 3),
            update_time=datetime(2026, 2, 3),
            mapping={},
            current_node="node1",
            conversation_id="conv1",
            is_starred=True,
            voice={"mode": "advanced"},
        )

        config = YAMLConfig(is_starred=True, voice=True)
        yaml = render_yaml_header(conv, config)

        assert "is_starred: true" in yaml
        assert "voice:" in yaml
        assert 'mode: "advanced"' in yaml

    def test_voice_as_string(self):
        conv = Conversation(
            title="Voice Test",
            create_time=datetime(2026, 2, 3),
            update_time=datetime(2026, 2, 3),
            mapping={},
            current_node="node1",
            conversation_id="conv_voice",
            voice="cove",
        )
        config = YAMLConfig(voice=True)
        yaml = render_yaml_header(conv, config)
        assert 'voice: "cove"' in yaml
