from __future__ import annotations

from markdown import Markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension


def render_markdown(text: str) -> str:
    """Renderiza texto Markdown seguro con un conjunto de extensiones útiles."""
    md = Markdown(
        extensions=[
            FencedCodeExtension(),
            CodeHiliteExtension(guess_lang=False, noclasses=True),
            TableExtension(),
        ],
        output_format="html5",
    )
    return md.convert(text)
