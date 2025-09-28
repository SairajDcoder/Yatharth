from flask import send_file
from flask_restx import Namespace, Resource
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import io

from src.yatharth.database import db
from src.yatharth.database.login_model import Login
from src.yatharth.database.verifyHistory_model import VerificationHistory

# Create namespace
REPORTS_API = Namespace('api', description='PDF Report operations')


@REPORTS_API.route('/download/user/<string:user_email>')
class UserReport(Resource):
    def get(self, user_email):
        """Download user-specific PDF report"""
        try:
            # Fetch user data from database
            user = Login.query.filter_by(email=user_email).first()
            if not user:
                return {'message': 'User not found'}, 404

            user_data = {
                "email": user.email,
                "username": user.username,
                "phone_no": user.phone_no,
                "created_at": user.created_at.strftime('%Y-%m-%d') if user.created_at else 'N/A'
            }

            # Generate PDF
            pdf_content = generate_user_report_pdf(user_data, "verification")

            # Create response
            filename = f"yatharth_report_{user.username}_{datetime.now().strftime('%Y%m%d')}.pdf"

            return send_file(
                BytesIO(pdf_content),
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )

        except Exception as e:
            return {'message': f'Error generating report: {str(e)}'}, 500


def generate_user_report_pdf(user_data: dict, report_type: str) -> bytes:
    """Generate PDF report with user data and verification history"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Create styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.darkblue,
        alignment=1  # Center aligned
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkblue
    )

    normal_style = styles['Normal']
    small_style = ParagraphStyle(
        'Small',
        parent=normal_style,
        fontSize=8
    )

    # Build story (content)
    story = []

    # Title
    story.append(Paragraph("YATHARTH VERIFICATION REPORT", title_style))
    story.append(Spacer(1, 0.2*inch))

    # Report metadata
    story.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    story.append(
        Paragraph(f"Report Type: {report_type.upper()} Report", normal_style))
    story.append(Paragraph(
        f"Report ID: REP-{datetime.now().strftime('%Y%m%d-%H%M%S')}", normal_style))
    story.append(Spacer(1, 0.3*inch))

    # User Information
    story.append(Paragraph("User Information", heading_style))
    user_info = [
        ["Username:", user_data.get('username', 'N/A')],
        ["Email:", user_data.get('email', 'N/A')],
        ["Phone:", user_data.get('phone_no', 'N/A')],
        ["Member Since:", user_data.get('created_at', 'N/A')]
    ]

    user_table = Table(user_info, colWidths=[1.5*inch, 4*inch])
    user_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(user_table)
    story.append(Spacer(1, 0.3*inch))

    # Footer
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("This is an auto-generated report from YATHARTH Verification System.",
                           ParagraphStyle('Footer', parent=small_style, textColor=colors.gray)))

    # Build PDF
    doc.build(story)

    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
