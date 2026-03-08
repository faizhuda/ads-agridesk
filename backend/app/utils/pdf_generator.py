import os
from io import BytesIO
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
        signature_path: Optional[str] = None,
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

        # Optional applicant signature block
        if signature_path and os.path.exists(signature_path):
            c.setFont("Helvetica", 10)
            c.drawString(2 * cm, 4.3 * cm, "Tanda Tangan Mahasiswa")
            c.drawImage(
                signature_path,
                2 * cm,
                2 * cm,
                width=4 * cm,
                height=2 * cm,
                preserveAspectRatio=True,
                mask="auto",
            )

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
        signature_paths: Optional[list[str]] = None,
    ) -> str:
        pdf_dir = os.path.join(settings.UPLOAD_DIR, "pdfs", "final")
        os.makedirs(pdf_dir, exist_ok=True)
        output_path = os.path.join(pdf_dir, output_filename)

        if not pdf_path or not os.path.exists(pdf_path):
            # Fallback for legacy cases where source PDF is missing.
            c = canvas.Canvas(output_path, pagesize=A4)
            page_width, page_height = A4
            c.setFont("Helvetica", 10)
            c.drawString(2 * cm, page_height - 2 * cm, "[Final Approved Document]")
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

        from pypdf import PdfReader, PdfWriter

        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        last_page = writer.pages[-1]
        page_width = float(last_page.mediabox.width)
        page_height = float(last_page.mediabox.height)

        overlay_bytes = BytesIO()
        overlay = canvas.Canvas(overlay_bytes, pagesize=(page_width, page_height))

        # Attach QR code at bottom-right of final page.
        if qr_path and os.path.exists(qr_path):
            overlay.drawImage(
                qr_path,
                page_width - 6 * cm,
                2 * cm,
                width=4 * cm,
                height=4 * cm,
                preserveAspectRatio=True,
                mask="auto",
            )

        # Render each signed image on final page.
        valid_signature_paths = [p for p in (signature_paths or []) if p and os.path.exists(p)]
        sig_x = 2 * cm
        sig_y = 2 * cm
        for idx, sig_path in enumerate(valid_signature_paths):
            if idx > 0:
                sig_x += 4.8 * cm
            if sig_x + (4 * cm) > page_width - 7 * cm:
                break
            overlay.drawImage(
                sig_path,
                sig_x,
                sig_y,
                width=4 * cm,
                height=2 * cm,
                preserveAspectRatio=True,
                mask="auto",
            )

        overlay.save()
        overlay_bytes.seek(0)

        overlay_pdf = PdfReader(overlay_bytes)
        last_page.merge_page(overlay_pdf.pages[0])

        with open(output_path, "wb") as f:
            writer.write(f)

        return output_path
