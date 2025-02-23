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

def generate_pdf_report(results, output_path="reports"):
    """Generate PDF report from test results"""
    try:
        # Create PDF instance
        pdf = TestResultsPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Summary Section
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r["status"] == "success")
        success_rate = round((passed_tests/total_tests * 100) if total_tests > 0 else 0)

        # Add summary
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Test Cases Summary', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(60, 10, f'Total Tests: {total_tests}', 0, 1)
        pdf.cell(60, 10, f'Passed Tests: {passed_tests}', 0, 1)
        pdf.cell(60, 10, f'Success Rate: {success_rate}%', 0, 1)
        pdf.ln(10)

        # Detailed Results
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Detailed Test Results', 0, 1)
        pdf.ln(5)

        # Process each test case
        for idx, result in enumerate(results, 1):
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, f'Test Case {idx}:', 0, 1)
            
            pdf.set_font('Arial', '', 12)
            pdf.cell(30, 10, 'Query:', 0)
            pdf.multi_cell(0, 10, result["query"])
            
            pdf.cell(30, 10, 'Status:', 0)
            pdf.cell(0, 10, result["status"].upper(), 0, 1)

            # Add code sections
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Generated Code:', 0, 1)
            pdf.set_font('Courier', '', 10)
            pdf.multi_cell(0, 5, result["generated_code"])
            
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Expected Code:', 0, 1)
            pdf.set_font('Courier', '', 10)
            pdf.multi_cell(0, 5, result["expected_code"])

            # Add module results if present
            if "analysis_results" in result:
                pdf.ln(5)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, 'Analysis Results:', 0, 1)
                
                for module_id, analysis in result["analysis_results"].items():
                    pdf.set_font('Arial', 'B', 11)
                    pdf.cell(0, 10, f'{analysis["name"]}:', 0, 1)
                    
                    if "error" in analysis:
                        pdf.set_font('Arial', '', 10)
                        pdf.multi_cell(0, 10, f"Error: {analysis['error']}")
                    else:
                        pdf.set_font('Arial', '', 10)
                        result_text = str(analysis['result'])
                        pdf.multi_cell(0, 5, result_text[:500])

            pdf.add_page()

        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)

        # Generate unique filename with timestamp
        filename = f"code_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(output_path, filename)

        # Save PDF
        pdf.output(filepath)
        
        print(f"PDF generated successfully at: {filepath}")  # Debug print
        return filepath

    except Exception as e:
        print(f"Error generating PDF: {str(e)}")  # Debug print
        return None