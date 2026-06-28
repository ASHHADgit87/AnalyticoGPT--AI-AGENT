import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def _clean_markdown(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"^#{1,3}\s*", "", text, flags=re.MULTILINE)
    return text.strip()


def _build_styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "DocTitle",
            parent=base["Normal"],
            fontSize=22,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#4f46e5"),
            spaceAfter=2,
            leading=28,
        ),
        "subtitle": ParagraphStyle(
            "SubTitle",
            parent=base["Normal"],
            fontSize=9,
            fontName="Helvetica",
            textColor=colors.HexColor("#6b7280"),
            spaceAfter=16,
        ),
        "section_header": ParagraphStyle(
            "SectionHeader",
            parent=base["Normal"],
            fontSize=12,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#4f46e5"),
            spaceBefore=14,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontSize=9,
            fontName="Helvetica",
            textColor=colors.HexColor("#1f2937"),
            leading=14,
            spaceAfter=4,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["Normal"],
            fontSize=9,
            fontName="Helvetica",
            textColor=colors.HexColor("#374151"),
            leading=13,
            leftIndent=14,
            spaceAfter=3,
        ),
        "quality_label": ParagraphStyle(
            "QualityLabel",
            parent=base["Normal"],
            fontSize=9,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#374151"),
            leading=13,
            spaceAfter=2,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=base["Normal"],
            fontSize=8,
            fontName="Helvetica-Bold",
            textColor=colors.white,
        ),
        "table_cell": ParagraphStyle(
            "TableCell",
            parent=base["Normal"],
            fontSize=7.5,
            fontName="Helvetica",
            textColor=colors.HexColor("#1f2937"),
        ),
        "quality_score_big": ParagraphStyle(
            "QualityScoreBig",
            parent=base["Normal"],
            fontSize=28,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#4f46e5"),
            leading=32,
            spaceAfter=0,
        ),
        "quality_badge": ParagraphStyle(
            "QualityBadge",
            parent=base["Normal"],
            fontSize=11,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#059669"),
            spaceAfter=4,
        ),
        "quality_stars": ParagraphStyle(
            "QualityStars",
            parent=base["Normal"],
            fontSize=14,
            fontName="Helvetica",
            textColor=colors.HexColor("#f59e0b"),
            spaceAfter=6,
        ),
        "quality_dim_label": ParagraphStyle(
            "QualityDimLabel",
            parent=base["Normal"],
            fontSize=8,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#6b7280"),
            spaceAfter=1,
        ),
        "quality_dim_value": ParagraphStyle(
            "QualityDimValue",
            parent=base["Normal"],
            fontSize=8,
            fontName="Helvetica",
            textColor=colors.HexColor("#111827"),
            spaceAfter=1,
        ),
    }


def _score_color(score: float) -> colors.Color:
    if score >= 90:
        return colors.HexColor("#059669")
    if score >= 75:
        return colors.HexColor("#10b981")
    if score >= 60:
        return colors.HexColor("#f59e0b")
    if score >= 40:
        return colors.HexColor("#ef4444")
    return colors.HexColor("#b91c1c")


def _bar_table(label: str, value: float, styles: dict) -> Table:
    filled = int(value / 10)
    filled = max(0, min(10, filled))
    empty = 10 - filled

    bar_cells = []
    for i in range(10):
        if i < filled:
            bar_cells.append("")
        else:
            bar_cells.append("")

    bar_color = _score_color(value)

    cell_styles = [
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#f3f4f6")]),
    ]
    for i in range(filled):
        cell_styles.append(("BACKGROUND", (i, 0), (i, 0), bar_color))
    for i in range(filled, 10):
        cell_styles.append(("BACKGROUND", (i, 0), (i, 0), colors.HexColor("#e5e7eb")))

    bar_t = Table([bar_cells], colWidths=[7] * 10, rowHeights=[8])
    bar_t.setStyle(TableStyle(cell_styles))

    row = Table(
        [
            [
                Paragraph(label, styles["quality_dim_label"]),
                bar_t,
                Paragraph(f"{value:.0f}", styles["quality_dim_value"]),
            ]
        ],
        colWidths=[90, 75, 30],
    )
    row.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return row


def _build_quality_section(quality_report: dict, styles: dict) -> list:
    flowables = []

    flowables.append(Spacer(1, 10))
    flowables.append(Paragraph("Data Quality Report", styles["section_header"]))
    flowables.append(
        HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.HexColor("#4f46e5"),
            spaceAfter=10,
        )
    )

    score = quality_report.get("score", 0)
    badge = quality_report.get("badge", "")
    stars = quality_report.get("star_str", "")
    missing = quality_report.get("missing_pct", 0)
    dupes = quality_report.get("duplicate_pct", 0)
    outliers = quality_report.get("outlier_pct", 0)
    skewness = quality_report.get("avg_skewness", 0)
    raw = quality_report.get("raw", {})
    bd = quality_report.get("breakdown", {})

    score_color = _score_color(score)

    score_para = Paragraph(
        f"{score:.0f}/100",
        ParagraphStyle(
            "ScoreBig",
            parent=styles["quality_score_big"],
            textColor=score_color,
        ),
    )

    badge_para = Paragraph(
        badge,
        ParagraphStyle(
            "BadgeDyn",
            parent=styles["quality_badge"],
            textColor=score_color,
        ),
    )

    stars_para = Paragraph(stars, styles["quality_stars"])

    meta_lines = [
        f"Total Rows: {raw.get('total_rows', 'N/A')}",
        f"Total Columns: {raw.get('total_cols', 'N/A')}",
        f"Missing Cells: {raw.get('missing_cells', 'N/A')}",
        f"Duplicate Rows: {raw.get('duplicate_rows', 'N/A')}",
        f"Missing: {missing}%",
        f"Duplicates: {dupes}%",
        f"Outlier Ratio: {outliers}%",
        f"Avg Skewness: {skewness}",
    ]
    meta_paras = [Paragraph(line, styles["quality_dim_value"]) for line in meta_lines]

    left_col = [
        score_para,
        Spacer(1, 4),
        badge_para,
        stars_para,
        Spacer(1, 6),
    ] + meta_paras

    right_col = [Spacer(1, 4)]
    dim_labels = {
        "completeness": "Completeness",
        "uniqueness": "Uniqueness",
        "outlier": "Outlier Score",
        "consistency": "Consistency",
        "skewness": "Skewness Score",
    }
    for key, label in dim_labels.items():
        val = bd.get(key, 0)
        right_col.append(_bar_table(label, val, styles))
        right_col.append(Spacer(1, 3))

    layout = Table(
        [[left_col, right_col]],
        colWidths=[180, 230],
    )
    layout.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#f9fafb")),
                ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#ffffff")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                ("LINEAFTER", (0, 0), (0, 0), 0.5, colors.HexColor("#e5e7eb")),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("ROUNDEDCORNERS", [6]),
            ]
        )
    )

    flowables.append(layout)
    return flowables


def _build_summary_section(summary: str, styles: dict) -> list:
    flowables = []
    lines = summary.split("\n")

    in_quality_block = False

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            flowables.append(Spacer(1, 4))
            continue

        if "Data Quality Report" in line_stripped:
            in_quality_block = True
            continue

        if in_quality_block:
            if line_stripped.startswith("### ") or (
                line_stripped.startswith("*") and "Processed numeric" in line_stripped
            ):
                in_quality_block = False
            else:
                continue

        if line_stripped.startswith("### "):
            content = _clean_markdown(line_stripped)
            flowables.append(Spacer(1, 8))
            flowables.append(Paragraph(content, styles["section_header"]))
            flowables.append(
                HRFlowable(
                    width="100%",
                    thickness=0.5,
                    color=colors.HexColor("#4f46e5"),
                    spaceAfter=6,
                )
            )
            continue

        if line_stripped.startswith("## "):
            content = _clean_markdown(line_stripped)
            flowables.append(Spacer(1, 6))
            flowables.append(Paragraph(content, styles["section_header"]))
            continue

        if line_stripped.startswith("* ") or line_stripped.startswith("- "):
            content = _clean_markdown(line_stripped[2:])
            flowables.append(Paragraph(f"• {content}", styles["bullet"]))
            continue

        content = _clean_markdown(line_stripped)
        if content:
            flowables.append(Paragraph(content, styles["body"]))

    return flowables


def _clean_cell_value(val) -> str:
    s = str(val)
    if s.lower() in ("nan", "none", "nat", ""):
        return "-"
    try:
        f = float(s)
        if f == int(f):
            return str(int(f))
        return f"{f:.2f}"
    except Exception:
        pass
    return s[:28] if len(s) > 28 else s


def _build_performers_section(records: list, styles: dict) -> list:
    if not records:
        return []

    clean_records = []
    for rec in records:
        clean_rec = {}
        for k, v in rec.items():
            cleaned_val = _clean_cell_value(v)
            if cleaned_val == "-" and str(v).lower() in ("nan", "none", "nat"):
                continue
            clean_rec[k] = cleaned_val
        if clean_rec:
            clean_records.append(clean_rec)

    if not clean_records:
        return []

    all_keys = list(clean_records[0].keys())
    valid_keys = [
        k
        for k in all_keys
        if not all(_clean_cell_value(rec.get(k, "")) == "-" for rec in clean_records)
    ]

    if not valid_keys:
        return []

    flowables = []
    flowables.append(Spacer(1, 14))
    flowables.append(Paragraph("Top Performers", styles["section_header"]))
    flowables.append(
        HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.HexColor("#4f46e5"),
            spaceAfter=8,
        )
    )

    display_headers = [k.replace("_", " ").title()[:18] for k in valid_keys]
    table_data = [[Paragraph(h, styles["table_header"]) for h in display_headers]]

    for rec in clean_records:
        row = []
        for k in valid_keys:
            val = _clean_cell_value(rec.get(k, "-"))
            row.append(Paragraph(val, styles["table_cell"]))
        table_data.append(row)

    col_count = len(valid_keys)
    available_width = letter[0] - 1.5 * inch
    col_width = available_width / col_count

    t = Table(table_data, colWidths=[col_width] * col_count, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e1b4b")),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.HexColor("#f9fafb"), colors.HexColor("#f3f4f6")],
                ),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d1d5db")),
                ("LINEBELOW", (0, 0), (-1, 0), 1.2, colors.HexColor("#4f46e5")),
                ("ROUNDEDCORNERS", [4]),
            ]
        )
    )

    flowables.append(KeepTogether(t))
    return flowables


def compile_structural_pdf(
    target_path: str,
    title: str,
    summary: str,
    records: list,
    quality_report: dict = None,
) -> str:
    os.makedirs(os.path.dirname(target_path), exist_ok=True)

    doc = SimpleDocTemplate(
        target_path,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = _build_styles()
    story = []

    story.append(Paragraph(title, styles["title"]))
    story.append(
        Paragraph(
            "Generated by AnalyticoGPT   Data Analysis Pipeline",
            styles["subtitle"],
        )
    )
    story.append(
        HRFlowable(
            width="100%",
            thickness=1.5,
            color=colors.HexColor("#4f46e5"),
            spaceAfter=14,
        )
    )

    story.extend(_build_summary_section(summary, styles))

    if quality_report:
        story.extend(_build_quality_section(quality_report, styles))

    story.extend(_build_performers_section(records, styles))

    doc.build(story)
    return target_path
