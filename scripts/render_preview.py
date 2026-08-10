"""Regenerate the deterministic README preview image.

Development-only dependencies: reportlab and PyMuPDF.
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import fitz
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas


WIDTH = 1440
HEIGHT = 960

INK = "#17231f"
GREEN = "#126b4b"
RED = "#aa3838"
GOLD = "#c69213"
MUTED = "#60716a"
BORDER = "#cad5d1"
PAPER = "#ffffff"
BACKGROUND = "#f7f9f8"


def set_color(pdf: canvas.Canvas, value: str, *, fill: bool = True) -> None:
    red, green, blue = (
        int(value[index : index + 2], 16) / 255 for index in (1, 3, 5)
    )
    if fill:
        pdf.setFillColorRGB(red, green, blue)
    else:
        pdf.setStrokeColorRGB(red, green, blue)


def draw_text(
    pdf: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    *,
    size: float = 14,
    font: str = "Helvetica",
    color: str = INK,
) -> None:
    set_color(pdf, color)
    pdf.setFont(font, size)
    pdf.drawString(x, y, text)


def draw_wrapped(
    pdf: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    width: float,
    *,
    size: float = 13,
    leading: float = 18,
    font: str = "Helvetica",
    color: str = INK,
) -> float:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and pdfmetrics.stringWidth(candidate, font, size) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    for line in lines:
        draw_text(pdf, line, x, y, size=size, font=font, color=color)
        y -= leading
    return y


def draw_panel(
    pdf: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    label: str,
    title: str,
) -> None:
    set_color(pdf, PAPER)
    set_color(pdf, BORDER, fill=False)
    pdf.roundRect(x, y, width, height, 6, fill=1, stroke=1)
    pdf.line(x, y + height - 68, x + width, y + height - 68)
    draw_text(
        pdf,
        label.upper(),
        x + 20,
        y + height - 27,
        size=10,
        font="Helvetica-Bold",
        color=MUTED,
    )
    draw_text(
        pdf,
        title,
        x + 20,
        y + height - 51,
        size=20,
        font="Helvetica-Bold",
    )


def draw_source(
    pdf: canvas.Canvas,
    x: float,
    y: float,
    filename: str,
    lines: list[tuple[str, bool]],
    *,
    accent: str = "#a9b8b2",
) -> float:
    height = 31 + len(lines) * 20
    set_color(pdf, accent)
    pdf.rect(x, y - height + 8, 3, height, fill=1, stroke=0)
    draw_text(
        pdf,
        filename,
        x + 14,
        y,
        size=12,
        font="Courier-Bold",
        color=GREEN,
    )
    line_y = y - 23
    for line, bold in lines:
        draw_text(
            pdf,
            line,
            x + 14,
            line_y,
            size=13,
            font="Helvetica-Bold" if bold else "Helvetica",
            color="#35453f",
        )
        line_y -= 20
    return y - height - 12


def render_preview(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        pdf_path = Path(temp_file.name)

    pdf = canvas.Canvas(str(pdf_path), pagesize=(WIDTH, HEIGHT))
    set_color(pdf, BACKGROUND)
    pdf.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
    set_color(pdf, GREEN)
    pdf.rect(0, HEIGHT - 18, WIDTH, 18, fill=1, stroke=0)

    draw_text(
        pdf,
        "LAB MEETING REPORT",
        48,
        902,
        size=12,
        font="Helvetica-Bold",
        color=GREEN,
    )
    draw_text(
        pdf,
        "From scattered notes to an evidence-grounded decision",
        48,
        861,
        size=32,
        font="Helvetica-Bold",
    )
    draw_text(
        pdf,
        "Synthetic example. Every value remains traceable to a bundled source.",
        48,
        834,
        size=15,
        color="#52615c",
    )
    set_color(pdf, BORDER)
    set_color(pdf, BORDER, fill=False)
    pdf.roundRect(1334, 865, 58, 30, 4, fill=0, stroke=1)
    draw_text(pdf, "v1.2.2", 1343, 875, size=11, font="Helvetica-Bold")

    panel_y = 125
    panel_height = 675
    left_x = 48
    left_width = 405
    right_x = 525
    right_width = 867
    draw_panel(pdf, left_x, panel_y, left_width, panel_height, "Inputs / four files", "Raw research evidence")
    draw_panel(pdf, right_x, panel_y, right_width, panel_height, "Generated Markdown report", "Decision-ready, with evidence boundaries")

    set_color(pdf, GREEN, fill=False)
    pdf.setLineWidth(3)
    pdf.line(472, 469, 502, 469)
    pdf.line(493, 477, 502, 469)
    pdf.line(493, 461, 502, 469)
    pdf.setLineWidth(1)

    source_y = 696
    source_y = draw_source(
        pdf,
        68,
        source_y,
        "results/baseline.csv",
        [("Macro-F1: 0.712", True), ("Median latency: 18.2 ms", False)],
    )
    source_y = draw_source(
        pdf,
        68,
        source_y,
        "results/retrieval_reranker.csv",
        [
            ("Seeds 11, 22, 33: 0.758 / 0.764 / 0.749", False),
            ("Mean: 0.757 | latency: 19.4 ms", True),
        ],
    )
    source_y = draw_source(
        pdf,
        68,
        source_y,
        "results/paraphrase_all_classes.csv",
        [
            ("Macro-F1: 0.691", True),
            ("Rare-class precision dropped most.", False),
            ("Expected outcome: not supplied", True),
        ],
        accent=RED,
    )
    source_y = draw_source(
        pdf,
        68,
        source_y,
        "input-notes.md",
        [
            ("Manual review: 45 / 120", True),
            ("No supported retrieval failure taxonomy yet.", False),
        ],
        accent=GOLD,
    )
    set_color(pdf, "#f1f4f3")
    pdf.roundRect(66, 164, 369, 86, 4, fill=1, stroke=0)
    draw_wrapped(
        pdf,
        "Mixed CSV rows, experiment notes, a failed run, and an unresolved decision enter as separate evidence sources.",
        80,
        224,
        338,
        size=12,
        leading=17,
        color="#55645f",
    )

    summary_x = right_x + 18
    summary_y = 612
    summary_width = right_width - 36
    summary_height = 92
    set_color(pdf, BORDER, fill=False)
    pdf.rect(summary_x, summary_y, summary_width, summary_height, fill=0, stroke=1)
    column_width = summary_width / 3
    for index in (1, 2):
        pdf.line(
            summary_x + column_width * index,
            summary_y,
            summary_x + column_width * index,
            summary_y + summary_height,
        )
    summaries = [
        ("VALIDATED PROGRESS", "Macro-F1 0.712 -> 0.757", GREEN),
        ("OPERATIONAL COST", "Latency 18.2 -> 19.4 ms", INK),
        ("NEGATIVE RESULT", "Paraphrase run fell to 0.691", RED),
    ]
    for index, (label, value, color) in enumerate(summaries):
        x = summary_x + column_width * index + 13
        draw_text(pdf, label, x, 678, size=9, font="Helvetica-Bold", color=MUTED)
        draw_wrapped(
            pdf,
            value,
            x,
            646,
            column_width - 26,
            size=14,
            leading=18,
            font="Helvetica-Bold",
            color=color,
        )

    draw_text(pdf, "Results and evidence", summary_x, 578, size=16, font="Helvetica-Bold")
    table_x = summary_x
    table_top = 558
    row_height = 36
    columns = [315, 116, 116, 284]
    headers = ["Experiment", "Macro-F1", "Latency", "Evidence"]
    rows = [
        ["Frozen encoder baseline", "0.712", "18.2 ms", "baseline.csv"],
        ["Retrieval + reranker", "0.757 mean", "19.4 ms", "retrieval_reranker.csv"],
        ["Paraphrase all classes", "0.691", "Not supplied", "paraphrase_all_classes.csv"],
    ]
    set_color(pdf, "#eaf0ee")
    pdf.rect(table_x, table_top - row_height, sum(columns), row_height, fill=1, stroke=0)
    set_color(pdf, BORDER, fill=False)
    pdf.rect(table_x, table_top - row_height * 4, sum(columns), row_height * 4, fill=0, stroke=1)
    for row_index in range(1, 4):
        y = table_top - row_height * row_index
        pdf.line(table_x, y, table_x + sum(columns), y)
    running_x = table_x
    for width in columns[:-1]:
        running_x += width
        pdf.line(running_x, table_top, running_x, table_top - row_height * 4)
    running_x = table_x
    for index, header in enumerate(headers):
        draw_text(pdf, header, running_x + 9, table_top - 24, size=10, font="Helvetica-Bold")
        running_x += columns[index]
    for row_index, row in enumerate(rows):
        running_x = table_x
        y = table_top - row_height * (row_index + 1) - 23
        for column_index, value in enumerate(row):
            color = RED if value == "0.691" else GREEN if value == "0.757 mean" else INK
            font = "Courier" if column_index == 3 else "Helvetica"
            if value in {"0.691", "0.757 mean"}:
                font = "Helvetica-Bold"
            draw_text(pdf, value, running_x + 9, y, size=10, font=font, color=color)
            running_x += columns[column_index]

    callout_y = 315
    callout_width = (summary_width - 16) / 2
    set_color(pdf, RED)
    pdf.rect(summary_x, callout_y + 78, callout_width, 3, fill=1, stroke=0)
    draw_text(pdf, "Failed experiment retained", summary_x, callout_y + 56, size=13, font="Helvetica-Bold")
    draw_wrapped(
        pdf,
        "Observed: class-wide paraphrasing reduced macro-F1. Boundary: no expected outcome or additional cause was supplied.",
        summary_x,
        callout_y + 34,
        callout_width - 8,
        size=11,
        leading=15,
        color="#3f4e49",
    )
    second_x = summary_x + callout_width + 16
    set_color(pdf, "#263b34")
    pdf.rect(second_x, callout_y + 78, callout_width, 3, fill=1, stroke=0)
    draw_text(pdf, "Attribution remains unresolved", second_x, callout_y + 56, size=13, font="Helvetica-Bold")
    draw_wrapped(
        pdf,
        "The comparison changes retrieval and the reranker together, so the gain cannot be assigned to either component.",
        second_x,
        callout_y + 34,
        callout_width - 8,
        size=11,
        leading=15,
        color="#3f4e49",
    )

    set_color(pdf, "#fff8e5")
    pdf.roundRect(summary_x, 178, summary_width, 102, 4, fill=1, stroke=0)
    set_color(pdf, GOLD)
    pdf.rect(summary_x, 178, 4, 102, fill=1, stroke=0)
    draw_text(pdf, "Next decision", summary_x + 17, 248, size=13, font="Helvetica-Bold")
    draw_wrapped(
        pdf,
        "Choose between the retrieval-only ablation and completion of manual review. The sources do not provide a priority rule.",
        summary_x + 17,
        225,
        summary_width - 34,
        size=11,
        leading=15,
        color="#4b473a",
    )

    draw_text(
        pdf,
        "Facts, interpretations, hypotheses, failures, and missing evidence stay distinct.",
        48,
        82,
        size=11,
        color="#5f6e69",
    )
    draw_text(
        pdf,
        "Audit the full example in examples/research-progress/",
        1094,
        82,
        size=10,
        font="Courier",
        color=GREEN,
    )
    pdf.showPage()
    pdf.save()

    document = fitz.open(pdf_path)
    try:
        pixmap = document[0].get_pixmap(alpha=False)
        pixmap.save(output)
    finally:
        document.close()
        pdf_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the README preview PNG")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("assets/lab-meeting-report-preview.png"),
    )
    args = parser.parse_args()
    render_preview(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
