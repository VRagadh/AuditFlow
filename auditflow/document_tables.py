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
        column_styles: dict[int, str] | None = None
        ) -> str:
    rows = [row for row in rows if any(cell_text(value) for value in row)]
    if not rows:
        return f"<p><em>{html_text(empty_text)}</em></p>"
    headings = "".join(f'<th scope="col">{html_text(value)}</th>' for value in headers)

    # it allows to apply styles to the columns specified in the create_audit_program function (audit_program.py)
    # this is important because some columns must inherently contain a lot of text, which requires a wider column.
    def make_cell(value: Any, col_idx: int) -> str:
        html_val = html_text(value)
        style = column_styles.get(col_idx) if column_styles else None
        if style:
            return f'<td><div style="{style}">{html_val}</div></td>'
        return f"<td>{html_val}</td>"

    body = "\n".join(
        "<tr>" + "".join(make_cell(value, idx) for idx, value in enumerate(row)) + "</tr>"
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