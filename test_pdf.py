from src.agents.security_analyzer.cli import save_as_pdf
from reportlab.lib import colors
import os
import json

# Create a simple test result with explicit color values
test_result = {
    "success": True,
    "file_path": "data/test_config.json",
    "risk_level": "critical",
    "poisoning_detected": True,
    "findings": [
        {"type": "excessive_permissions", "matched_text": "admin-access", "context": "admin-access permission granted"},
        {"type": "credential_exposure", "matched_text": "password", "context": "hardcoded password found"},
        {"type": "encryption_weaknesses", "matched_text": "disabled", "context": "encryption disabled in config"}
    ],
    "suggested_remediations": [
        "Remove excessive permissions",
        "Use a secrets manager instead of hardcoding credentials",
        "Enable encryption for sensitive data"
    ],
    "explanation": "Multiple security issues were detected that could lead to a system compromise."
}

# Fix the color issue in save_as_pdf function
def fixed_save_pdf(results):
    # Define risk level hex color mapping instead of ReportLab colors
    risk_color_map = {
        "critical": "#FF0000",  # Red
        "high": "#FF4500",      # OrangeRed
        "medium": "#FFA500",    # Orange
        "low": "#008000",       # Green
        "unknown": "#0000FF"    # Blue
    }
    
    # Get the risk level and corresponding color
    risk_level = results.get("risk_level", "unknown").lower()
    risk_color = risk_color_map.get(risk_level, "#0000FF")
    
    # Create reports directory if it doesn't exist
    reports_dir = os.path.join(os.getcwd(), "reports")
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # Generate a filename with timestamp
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(results["file_path"])
    output_path = os.path.join(reports_dir, f"{filename}_{timestamp}_fixed.pdf")
    
    # Import necessary libraries
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    
    # Create the PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Add a title
    title_text = f"Security Analysis Report: {risk_level.upper()} Risk"
    elements.append(Paragraph(title_text, styles["Title"]))
    
    # Add findings
    elements.append(Paragraph("Findings:", styles["Heading2"]))
    for finding in results["findings"]:
        elements.append(Paragraph(f"- {finding['type']}: {finding['matched_text']}", styles["Normal"]))
    
    # Build the PDF
    doc.build(elements)
    return output_path

# Save as PDF using the fixed function
print("Creating PDF...")
pdf_path = fixed_save_pdf(test_result)
print(f"PDF saved to: {pdf_path}")
print(f"PDF exists: {os.path.exists(pdf_path)}")
print(f"PDF size: {os.path.getsize(pdf_path)} bytes")
