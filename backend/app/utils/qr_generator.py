import os

import qrcode
from PIL import Image

from app.config import settings


class QRCodeGenerator:
    @staticmethod
    def generate_qr_code(data: str, filename: str) -> str:
        qr_dir = os.path.join(settings.UPLOAD_DIR, "qr_codes")
        os.makedirs(qr_dir, exist_ok=True)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img: Image.Image = qr.make_image(fill_color="black", back_color="white")
        filepath = os.path.join(qr_dir, filename)
        img.save(filepath)
        return filepath
