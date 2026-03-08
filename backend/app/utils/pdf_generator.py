import os
from typing import Dict, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from app.config import settings


class PDFGenerator:
    @staticmethod
    def generate_from_template(
        template_name: str,
        fields: Dict[str, str],
        filename: str,
    ) -> str:
        pdf_dir = os.path.join(settings.UPLOAD_DIR, "pdfs")
        os.makedirs(pdf_dir, exist_ok=True)
        filepath = os.path.join(pdf_dir, filename)

        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4

        # Header
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2, height - 2 * cm, template_name)

        # Body fields
        c.setFont("Helvetica", 11)
        y_pos = height - 4 * cm
        for key, value in fields.items():
            label = key.replace("_", " ").title()
            c.drawString(2 * cm, y_pos, f"{label}: {value}")
            y_pos -= 0.8 * cm

        c.save()
        return filepath

    @staticmethod
    def attach_signature(
        pdf_path: str,
        signature_image_path: str,
        output_path: str,
        x: float = 2,
        y: float = 5,
        width: float = 4,
        height: float = 2,
    ) -> str:
        c = canvas.Canvas(output_path, pagesize=A4)
        page_width, page_height = A4

        # Copy placeholder – in a production system you'd merge with existing PDF
        c.setFont("Helvetica", 10)
        c.drawString(2 * cm, page_height - 2 * cm, "[Signed Document]")

        if os.path.exists(signature_image_path):
            c.drawImage(
                signature_image_path,
                x * cm,
                y * cm,
                width=width * cm,
                height=height * cm,
                preserveAspectRatio=True,
                mask="auto",
            )

        c.save()
        return output_path

    @staticmethod
    def generate_final_pdf(
        pdf_path: str,
        qr_path: Optional[str],
        output_filename: str,
    ) -> str:
        pdf_dir = os.path.join(settings.UPLOAD_DIR, "pdfs", "final")
        os.makedirs(pdf_dir, exist_ok=True)
        output_path = os.path.join(pdf_dir, output_filename)

        c = canvas.Canvas(output_path, pagesize=A4)
        page_width, page_height = A4

        c.setFont("Helvetica", 10)
        c.drawString(2 * cm, page_height - 2 * cm, "[Final Approved Document]")

        # Attach QR code at bottom-right
        if qr_path and os.path.exists(qr_path):
            c.drawImage(
                qr_path,
                page_width - 6 * cm,
                2 * cm,
                width=4 * cm,
                height=4 * cm,
                preserveAspectRatio=True,
                mask="auto",
            )

        c.save()
        return output_path
