import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from models.report_model import ReportModel


class ReportService:
    def __init__(self, output_dir: str = "outputs/reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_pdf_report(
        self, report_data: ReportModel, chart_paths: List[str]
    ) -> str:
        pdf_path = os.path.join(self.output_dir, f"report_{report_data.report_id}.pdf")
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()

        custom_title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontSize=24,
            leading=28,
            spaceAfter=12,
        )

        story = []
        story.append(Paragraph(report_data.title, custom_title_style))
        story.append(
            Paragraph(
                f"Author: {report_data.author} | Date: {report_data.generated_at}",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 12))

        story.append(Paragraph("Executive Summary", styles["Heading2"]))
        story.append(Paragraph(report_data.executive_summary, styles["Normal"]))
        story.append(Spacer(1, 12))

        for section in report_data.sections:
            story.append(Paragraph(section.title, styles["Heading3"]))
            story.append(Paragraph(section.content, styles["Normal"]))
            story.append(Spacer(1, 12))

        for path in chart_paths:
            if os.path.exists(path):
                story.append(Image(path, width=400, height=250))
                story.append(Spacer(1, 12))

        story.append(Paragraph("Strategic Recommendations", styles["Heading2"]))
        for rec in report_data.recommendations:
            story.append(Paragraph(f"• {rec}", styles["Normal"]))

        doc.build(story)
        report_data.output_pdf_path = pdf_path
        return pdf_path
