from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

from auditflow.blocks import replace_auto_blocks


def mapping_rows(value: Any) -> list[dict[str, Any]]:
    return [row for row in value if isinstance(row, dict)] if isinstance(value, list) else []


def cell_text(value: Any) -> str:
    if isinstance(value, list):
        return "\n".join(f'- {cell_text(item)}' for item in value)
    return "" if value is None else str(value).strip()


def html_text(value: Any) -> str:
    return escape(cell_text(value)).replace("`", "&#96;").replace("\n", "<br>")


def html_table(
    headers: list[str], 
    rows: list[list[Any]], 
    empty_text: str,
    field_names: list[str] | None = None
) -> str:
    rows = [row for row in rows if any(cell_text(value) for value in row)]
    if not rows:
        return f"<p><em>{html_text(empty_text)}</em></p>"
        
    def get_class(idx: int) -> str:
        if field_names and idx < len(field_names):
            # Convert snake_case to kebab-case for CSS (test_script -> col-test-script)
            return f' class="col-{field_names[idx].replace("_", "-")}"'
        return ""

    headings = "".join(
        f'<th scope="col"{get_class(idx)}>{html_text(value)}</th>' 
        for idx, value in enumerate(headers)
    )
    
    body = "\n".join(
        "<tr>" + "".join(
            f"<td{get_class(idx)}>{html_text(value)}</td>" 
            for idx, value in enumerate(row)
        ) + "</tr>"
        for row in rows
    )
    return (
        '<div class="scroll-table-container">\n<table>\n'
        f"<thead><tr>{headings}</tr></thead>\n<tbody>\n{body}\n</tbody>\n</table>\n</div>"
    )


def refresh_table_document(path: Path, content: str, name: str, body: str) -> bool:
    """Update a named table block while preserving the document around it."""
    updated = replace_auto_blocks(
        content, {name: "```{=html}\n" + body + "\n```"}, keep_unknown=True,
    )
    data = updated.encode("utf-8")
    if path.exists() and data == path.read_bytes():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return True