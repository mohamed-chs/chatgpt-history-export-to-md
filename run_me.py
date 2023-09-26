import typer

from src.message_processing import format_message_as_md
from src.metadata_extraction import extract_metadata, save_conversation_to_md
from src.utils import extract_zip, format_title, get_most_recent_zip, sanitize_title

app = typer.Typer()


@app.command()
def convert(source: str, destination: str):
    # Conversion code here.
    pass


@app.command()
def visualize(type: str, source: str):
    # Visualization code here.
    pass


@app.command()
def export(source: str, format: str):
    # Exporting code here.
    pass


if __name__ == "__main__":
    app()
