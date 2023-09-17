# message_processing.py


def determine_heading(author_role):
    """Determine the heading based on the author's role."""
    return author_role.capitalize() if author_role else "(other)"


def get_content_from_parts(content_data):
    """Extract content from the 'parts' of content data if available."""
    return content_data.get("parts", [None])[0]


def format_python_script(content_data):
    """Format content data containing Python code as markdown."""
    text = content_data.get("text")
    return f"```python\n{text}\n```" if text else None


def extract_content_from_message(message):
    """Extract content from a message."""
    content_data = message.get("content", {})

    content = get_content_from_parts(content_data)
    if content is None:
        content = format_python_script(content_data)

    return content


def format_message_as_md(message):
    """Format a message as markdown."""
    if not message or not message.get("author"):
        return ""

    author_role = message["author"].get("role")
    if author_role == "system":
        return ""

    heading = determine_heading(author_role)
    content = extract_content_from_message(message)

    if "text" in message.get("content", {}):
        heading += "\n### Code Interpreter..."

    return f"# {heading}\n{content}\n\n"
