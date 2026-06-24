import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def compile_structural_pdf(
    target_path: str, title: str, summary: str, records: list
) -> str:
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    doc = SimpleDocTemplate(target_path, pagesize=letter)
    styles = getSampleStyleSheet()

    custom_header = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=22,
        textColor=colors.HexColor("#6366f1"),
        spaceAfter=15,
    )
    story = [Paragraph(title, custom_header), Spacer(1, 10)]
    story.append(Paragraph(summary, styles["Normal"]))
    story.append(Spacer(1, 15))

    if records and len(records) > 0:
        if isinstance(records, dict):
            headers = list(records.keys())
            table_data = [headers]
            table_data.append([str(records[h]) for h in headers])
        elif isinstance(records, list) and isinstance(records[0], dict):
            headers = list(records[0].keys())
            table_data = [headers]
            for item in records:
                table_data.append([str(item.get(h, "")) for h in headers])
        else:
            headers = []
            table_data = []

        if table_data:
            t = Table(table_data)
            t.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f293d")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#374151")),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ]
                )
            )
            story.append(t)

    doc.build(story)
    return target_path
