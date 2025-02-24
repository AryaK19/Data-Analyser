from fpdf import FPDF
from datetime import datetime
import os
import json
from pathlib import Path

class TestResultsPDF(FPDF):
    def header(self):
        # Title
        self.set_font('Arial', 'B', 20)
        self.cell(0, 10, 'Code Analysis Report', 0, 1, 'C')
        # Date
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'R')
        # Line break
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(results):
    """Generate PDF report from analysis results"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        import os
        
        # Create results directory if it doesn't exist
        results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
        os.makedirs(results_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        pdf_path = os.path.join(results_dir, f"analysis_report_{timestamp}.pdf")
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Add content to the PDF
        story = []
        styles = getSampleStyleSheet()
        
        # Add title
        title = Paragraph("Code Analysis Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Add each test case result
        for idx, result in enumerate(results):
            # Add test case header
            story.append(Paragraph(f"Test Case {idx + 1}: {result['query']}", styles['Heading1']))
            story.append(Spacer(1, 12))
            
            # Add analysis results
            if "analysis_results" in result:
                for module_id, analysis in result["analysis_results"].items():
                    story.append(Paragraph(f"{analysis['name']}", styles['Heading2']))
                    if "result" in analysis:
                        # Format result details
                        result_text = str(analysis['result'])
                        story.append(Paragraph(result_text, styles['Normal']))
                    story.append(Spacer(1, 12))
            
            story.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(story)
        
        print(f"PDF generated at: {pdf_path}")  # Debug print
        return pdf_path
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")  # Debug print
        import traceback
        print(traceback.format_exc())  # Debug print
        return None