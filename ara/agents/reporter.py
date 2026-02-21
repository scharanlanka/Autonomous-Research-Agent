import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def extract_revised(text: str) -> str:
    # If critic returns "## Revised Report", take that section
    marker = "## Revised Report"
    if marker in text:
        return text.split(marker, 1)[1].strip()
    return text.strip()

def export_pdf_bytes(title: str, markdown_text: str) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    x = 40
    y = height - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, title)
    y -= 25

    c.setFont("Helvetica", 10)

    # naive markdown-to-text lines
    lines = markdown_text.replace("\r", "").split("\n")
    for line in lines:
        if y < 60:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 50
        # keep lines short-ish
        line = line[:160]
        c.drawString(x, y, line)
        y -= 14

    c.save()
    return buf.getvalue()