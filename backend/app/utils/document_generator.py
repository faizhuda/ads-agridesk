from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.core.settings import settings

if TYPE_CHECKING:
    from app.domain.signature import Signature
    from app.domain.surat import Surat

_PAGE_W, _PAGE_H = A4
_MARGIN = 25 * mm


class LocalDocumentGenerator:
    """Generate PDF documents and QR verification images."""

    def __init__(self, base_dir: str | None = None):
        root_dir = Path(base_dir or settings.documents_dir)
        self.base_dir = root_dir
        self.qr_dir = self.base_dir / "qr"
        self.pdf_dir = self.base_dir / "pdf"
        self.qr_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # QR
    # ------------------------------------------------------------------

    def generate_verification_qr(self, document_hash: str, surat_id: int) -> str:
        file_name = f"verify_{surat_id}_{document_hash[:10]}.png"
        file_path = self.qr_dir / file_name

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(document_hash)
        qr.make(fit=True)

        image = qr.make_image(fill_color="black", back_color="white")
        image.save(file_path)

        return str(file_path)

    # ------------------------------------------------------------------
    # PDF
    # ------------------------------------------------------------------

    def generate_surat_pdf(
        self,
        surat: Surat,
        signatures: list[Signature] | None = None,
    ) -> str:
        """Generate / regenerate the surat PDF.

        The PDF is re-created on every state-changing event so it always
        reflects the latest status and signatures.
        """
        file_name = f"surat_{surat.surat_id}.pdf"
        file_path = self.pdf_dir / file_name

        pdf = canvas.Canvas(str(file_path), pagesize=A4)
        pdf.setTitle(f"Surat {surat.surat_id}")
        y = _PAGE_H - _MARGIN

        # --- Header ---
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawCentredString(_PAGE_W / 2, y, "INSTITUT PERTANIAN BOGOR")
        y -= 18
        pdf.setFont("Helvetica", 11)
        pdf.drawCentredString(_PAGE_W / 2, y, "Sistem Administrasi Surat Akademik – Agridesk")
        y -= 24

        # Horizontal rule
        pdf.setLineWidth(1)
        pdf.line(_MARGIN, y, _PAGE_W - _MARGIN, y)
        y -= 24

        # --- Title ---
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawCentredString(_PAGE_W / 2, y, surat.jenis.upper())
        y -= 30

        # --- Body ---
        pdf.setFont("Helvetica", 11)
        fields = [
            ("No. Surat", str(surat.surat_id or "-")),
            ("Jenis", surat.jenis),
            ("Status", surat.status.value),
            ("Mahasiswa ID", str(surat.mahasiswa_id)),
        ]
        if surat.keperluan:
            fields.append(("Keperluan", surat.keperluan))

        for label, value in fields:
            pdf.drawString(_MARGIN, y, f"{label}: {value}")
            y -= 18

        # --- Signatures ---
        if signatures:
            y -= 12
            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(_MARGIN, y, "Tanda Tangan Dosen:")
            y -= 18
            pdf.setFont("Helvetica", 10)
            for sig in signatures:
                status_text = "✓ Ditandatangani" if sig.is_signed() else "⏳ Menunggu"
                line = f"  Dosen ID {sig.owner_id} — {status_text}"
                if sig.signed_at:
                    line += f"  ({sig.signed_at:%Y-%m-%d %H:%M})"
                pdf.drawString(_MARGIN, y, line)
                y -= 16

        # --- Document hash / QR ---
        if surat.document_hash:
            y -= 12
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(_MARGIN, y, "Verifikasi Dokumen:")
            y -= 16
            pdf.setFont("Courier", 9)
            pdf.drawString(_MARGIN, y, surat.document_hash)
            y -= 18

        if surat.qr_path and os.path.exists(surat.qr_path):
            qr_size = 30 * mm
            y -= qr_size + 4
            pdf.drawImage(surat.qr_path, _MARGIN, y, qr_size, qr_size)
            y -= 8

        # --- Footer ---
        pdf.setFont("Helvetica-Oblique", 8)
        pdf.drawCentredString(
            _PAGE_W / 2,
            _MARGIN - 8,
            "Dokumen ini dihasilkan oleh sistem Agridesk dan dapat diverifikasi secara online.",
        )

        pdf.showPage()
        pdf.save()

        return str(file_path)
