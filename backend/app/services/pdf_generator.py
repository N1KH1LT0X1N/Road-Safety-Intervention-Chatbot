"""PDF report generator for interventions."""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io
import base64
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Generate comprehensive PDF reports for road safety interventions."""

    def __init__(self):
        """Initialize PDF generator."""
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        logger.info("PDF generator initialized")

    def _create_custom_styles(self):
        """Create custom paragraph styles."""
        # Title style
        self.styles.add(
            ParagraphStyle(
                name="CustomTitle",
                parent=self.styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#1f77b4"),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
            )
        )

        # Heading style
        self.styles.add(
            ParagraphStyle(
                name="CustomHeading",
                parent=self.styles["Heading2"],
                fontSize=16,
                textColor=colors.HexColor("#2ca02c"),
                spaceBefore=12,
                spaceAfter=6,
                fontName="Helvetica-Bold",
            )
        )

        # Confidence badge style
        self.styles.add(
            ParagraphStyle(
                name="ConfidenceBadge",
                parent=self.styles["Normal"],
                fontSize=14,
                textColor=colors.white,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
            )
        )

    def generate_intervention_report(
        self, query: str, interventions: List[Dict[str, Any]], synthesis: str, metadata: Dict[str, Any]
    ) -> bytes:
        """Generate comprehensive intervention report."""
        try:
            # Create PDF buffer
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5 * inch, bottomMargin=0.5 * inch)

            # Build story (content)
            story = []

            # Cover page
            story.extend(self._create_cover_page(query, metadata))
            story.append(PageBreak())

            # Executive summary
            story.extend(self._create_executive_summary(query, len(interventions), metadata))
            story.append(Spacer(1, 0.3 * inch))

            # Interventions
            for idx, intervention in enumerate(interventions, 1):
                story.extend(self._create_intervention_section(intervention, idx))

                if idx < len(interventions):
                    story.append(Spacer(1, 0.2 * inch))
                    story.append(self._create_separator())
                    story.append(Spacer(1, 0.2 * inch))

            # Add page break before synthesis
            story.append(PageBreak())

            # AI Analysis
            story.extend(self._create_synthesis_section(synthesis))

            # Footer with metadata
            story.append(PageBreak())
            story.extend(self._create_metadata_section(metadata))

            # Build PDF
            doc.build(story)

            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()

            logger.info("PDF report generated successfully")
            return pdf_bytes

        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            raise

    def _create_cover_page(self, query: str, metadata: Dict[str, Any]) -> List:
        """Create cover page."""
        story = []

        # Title
        story.append(Spacer(1, 2 * inch))
        title = Paragraph("🚦 Road Safety Intervention Report", self.styles["CustomTitle"])
        story.append(title)

        story.append(Spacer(1, 0.5 * inch))

        # Query box
        query_style = ParagraphStyle(
            "QueryStyle",
            parent=self.styles["Normal"],
            fontSize=14,
            textColor=colors.HexColor("#333333"),
            alignment=TA_CENTER,
            fontName="Helvetica-Oblique",
        )

        query_text = f'<font color="#666666">Query:</font> "<b>{query}</b>"'
        story.append(Paragraph(query_text, query_style))

        story.append(Spacer(1, 1 * inch))

        # Report info table
        report_data = [
            ["Report Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Total Results:", str(metadata.get("total_results", 0))],
            ["Search Strategy:", metadata.get("search_strategy", "N/A").upper()],
            ["Query Time:", f"{metadata.get('query_time_ms', 0)}ms"],
        ]

        report_table = Table(report_data, colWidths=[2.5 * inch, 3 * inch])
        report_table.setStyle(
            TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), "Helvetica", 11),
                    ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 11),
                    ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#666666")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f5f5f5")),
                ]
            )
        )

        story.append(report_table)

        story.append(Spacer(1, 1.5 * inch))

        # Powered by
        powered_by = Paragraph(
            '<font size="10" color="#999999">Powered by Google Gemini AI</font>', self.styles["Normal"]
        )
        story.append(powered_by)

        return story

    def _create_executive_summary(self, query: str, num_results: int, metadata: Dict[str, Any]) -> List:
        """Create executive summary section."""
        story = []

        # Title
        story.append(Paragraph("Executive Summary", self.styles["CustomHeading"]))
        story.append(Spacer(1, 0.1 * inch))

        # Summary text
        summary_text = f"""
        This report presents {num_results} road safety intervention(s) identified for the query:
        "<b>{query}</b>". The interventions have been ranked by relevance and confidence using a
        hybrid search approach combining semantic similarity and structured queries.
        <br/><br/>
        Each intervention includes detailed specifications from IRC (Indian Roads Congress) standards,
        implementation guidelines, cost estimates, and maintenance requirements.
        """

        summary_para = Paragraph(summary_text, self.styles["Normal"])
        story.append(summary_para)

        return story

    def _create_intervention_section(self, intervention: Dict[str, Any], idx: int) -> List:
        """Create intervention detail section."""
        story = []

        # Intervention title with confidence
        confidence = intervention.get("confidence", 0)
        stars = "⭐" * min(5, int(confidence * 5))

        title_text = f'<font size="14"><b>{idx}. {intervention.get("title", "Unknown")}</b></font>'
        story.append(Paragraph(title_text, self.styles["Normal"]))

        # Confidence badge
        confidence_text = f'<font color="green">{stars} {confidence * 100:.0f}% Confidence</font>'
        story.append(Paragraph(confidence_text, self.styles["Normal"]))

        story.append(Spacer(1, 0.1 * inch))

        # Details table
        details_data = [
            ["Category:", intervention.get("category", "N/A")],
            ["Problem:", intervention.get("problem", "N/A")],
            ["Type:", intervention.get("type", "N/A")],
            ["IRC Reference:", f"{intervention.get('irc_reference', {}).get('code', 'N/A')} {intervention.get('irc_reference', {}).get('clause', '')}"],
            ["Cost Estimate:", intervention.get("cost_estimate", "N/A")],
            ["Installation Time:", intervention.get("installation_time", "N/A")],
        ]

        details_table = Table(details_data, colWidths=[2 * inch, 4 * inch])
        details_table.setStyle(
            TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), "Helvetica", 10),
                    ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 10),
                    ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#555555")),
                    ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                    ("ALIGN", (1, 0), (1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f9f9f9")),
                ]
            )
        )

        story.append(details_table)
        story.append(Spacer(1, 0.15 * inch))

        # Specifications
        specs = intervention.get("specifications", {})
        if specs:
            story.append(Paragraph("<b>Specifications:</b>", self.styles["Normal"]))

            specs_text = []
            if specs.get("dimensions"):
                specs_text.append(f"• Dimensions: {specs['dimensions']}")
            if specs.get("colors"):
                specs_text.append(f"• Colors: {', '.join(specs['colors'])}")
            if specs.get("placement"):
                specs_text.append(f"• Placement: {specs['placement']}")

            if specs_text:
                story.append(Paragraph("<br/>".join(specs_text), self.styles["Normal"]))
                story.append(Spacer(1, 0.1 * inch))

        # Explanation
        explanation = intervention.get("explanation", "No explanation available")
        story.append(Paragraph("<b>Explanation:</b>", self.styles["Normal"]))
        story.append(Paragraph(explanation, self.styles["Normal"]))

        story.append(Spacer(1, 0.1 * inch))

        # Maintenance
        maintenance = intervention.get("maintenance", "Standard maintenance required")
        story.append(Paragraph("<b>Maintenance:</b>", self.styles["Normal"]))
        story.append(Paragraph(maintenance, self.styles["Normal"]))

        return story

    def _create_synthesis_section(self, synthesis: str) -> List:
        """Create AI synthesis section."""
        story = []

        story.append(Paragraph("AI Analysis & Recommendations", self.styles["CustomHeading"]))
        story.append(Spacer(1, 0.1 * inch))

        # Convert markdown-like syntax to paragraph-friendly format
        synthesis_clean = synthesis.replace("**", "<b>").replace("##", "<br/><br/><b>").replace("*", "")

        story.append(Paragraph(synthesis_clean[:2000], self.styles["Normal"]))  # Limit length

        return story

    def _create_metadata_section(self, metadata: Dict[str, Any]) -> List:
        """Create metadata section."""
        story = []

        story.append(Paragraph("Technical Metadata", self.styles["CustomHeading"]))
        story.append(Spacer(1, 0.1 * inch))

        # Metadata table
        gemini_tokens = metadata.get("gemini_tokens", {})

        meta_data = [
            ["Search Strategy:", metadata.get("search_strategy", "N/A").upper()],
            ["Total Results:", str(metadata.get("total_results", 0))],
            ["Query Time:", f"{metadata.get('query_time_ms', 0)}ms"],
            ["Gemini Input Tokens:", str(gemini_tokens.get("input", 0))],
            ["Gemini Output Tokens:", str(gemini_tokens.get("output", 0))],
        ]

        meta_table = Table(meta_data, colWidths=[2.5 * inch, 3 * inch])
        meta_table.setStyle(
            TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
                    ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 9),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#666666")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#fafafa")),
                ]
            )
        )

        story.append(meta_table)

        # Footer
        story.append(Spacer(1, 0.5 * inch))
        footer_text = f"""
        <font size="8" color="#999999">
        Report generated on {datetime.now().strftime("%Y-%m-%d at %H:%M:%S")} |
        Road Safety Intervention AI v1.0 |
        Powered by Google Gemini
        </font>
        """
        story.append(Paragraph(footer_text, self.styles["Normal"]))

        return story

    def _create_separator(self):
        """Create visual separator."""
        return Table(
            [[""]],
            colWidths=[6 * inch],
            style=TableStyle([("LINEABOVE", (0, 0), (-1, -1), 2, colors.HexColor("#dddddd"))]),
        )
