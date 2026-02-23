import io
import re
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)

def extract_revised(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""

    # Try common heading variants first (case-insensitive).
    m = re.search(
        r"^\s*##\s*Revised\s+Report\s*:?\s*$([\s\S]*)",
        text,
        flags=re.I | re.M,
    )
    if m:
        candidate = _strip_outer_code_fence(m.group(1).strip())
        if candidate:
            return candidate

    # Fallback: if the model emitted only the revised report without headings.
    return _strip_outer_code_fence(text)


def _strip_outer_code_fence(text: str) -> str:
    if not text.startswith("```"):
        return text
    lines = text.splitlines()
    if len(lines) >= 2 and lines[-1].strip() == "```":
        return "\n".join(lines[1:-1]).strip()
    return text


def normalize_markdown_report(markdown_text: str, title: str = "ARA Research Report") -> str:
    text = _strip_outer_code_fence((markdown_text or "").replace("\r", "").strip())
    if not text:
        return f"# {title}\n\n_No content generated._"

    # Remove common agent wrappers if they leak through.
    text = re.sub(r"^\s*##\s*Critique\s*$.*?(?=^\s*##\s*Revised Report\s*$)", "", text, flags=re.S | re.M).strip()
    text = re.sub(r"^\s*##\s*Revised Report\s*$", "", text, flags=re.M).strip()

    # Ensure a top-level heading exists for clean Markdown/PDF output.
    first_nonempty = next((ln for ln in text.splitlines() if ln.strip()), "")
    if not first_nonempty.startswith("#"):
        text = f"# {title}\n\n{text}"

    # Normalize spacing around headings and collapse excessive blank lines.
    lines = text.splitlines()
    out: list[str] = []
    for i, line in enumerate(lines):
        if re.match(r"^\s*#{1,6}\s+", line):
            if out and out[-1].strip():
                out.append("")
            out.append(line.strip())
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            if next_line.strip():
                out.append("")
        else:
            out.append(line.rstrip())

    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    return text


def is_placeholder_report(markdown_text: str) -> bool:
    return "_No content generated._" in (markdown_text or "")


def _inline_markup(text: str) -> str:
    s = escape(text)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"<u>\1</u> (\2)", s)
    s = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", s)
    return s


def _build_styles():
    styles = getSampleStyleSheet()
    code_parent = styles["Code"] if "Code" in styles.byName else styles["BodyText"]
    return {
        "title": ParagraphStyle(
            "AraTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            spaceAfter=12,
        ),
        "h1": ParagraphStyle(
            "AraH1",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            spaceBefore=8,
            spaceAfter=6,
        ),
        "h2": ParagraphStyle(
            "AraH2",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            spaceBefore=6,
            spaceAfter=4,
        ),
        "h3": ParagraphStyle(
            "AraH3",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            spaceBefore=4,
            spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "AraBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            spaceAfter=5,
        ),
        "code": ParagraphStyle(
            "AraCode",
            parent=code_parent,
            fontName="Courier",
            fontSize=9,
            leading=12,
            leftIndent=8,
            rightIndent=8,
            spaceBefore=2,
            spaceAfter=6,
        ),
    }


def _markdown_to_story(markdown_text: str, title: str):
    styles = _build_styles()
    story = [Paragraph(_inline_markup(title), styles["title"]), Spacer(1, 0.08 * inch)]
    normalized_title = re.sub(r"\s+", " ", title).strip().lower()

    lines = markdown_text.replace("\r", "").splitlines()
    paragraph_buf: list[str] = []
    code_buf: list[str] = []
    table_buf: list[str] = []
    list_buf: list[str] = []
    list_kind: str | None = None  # "bullet" or "ordered"
    in_code = False

    def flush_paragraph():
        nonlocal paragraph_buf
        if paragraph_buf:
            text = " ".join(s.strip() for s in paragraph_buf if s.strip())
            if text:
                story.append(Paragraph(_inline_markup(text), styles["body"]))
            paragraph_buf = []

    def flush_code():
        nonlocal code_buf
        if code_buf:
            story.append(Preformatted("\n".join(code_buf), styles["code"]))
            code_buf = []

    def flush_table():
        nonlocal table_buf
        if table_buf:
            story.append(Preformatted("\n".join(table_buf), styles["code"]))
            table_buf = []

    def flush_list():
        nonlocal list_buf, list_kind
        if not list_buf:
            return
        items = [ListItem(Paragraph(_inline_markup(item), styles["body"])) for item in list_buf]
        story.append(
            ListFlowable(
                items,
                bulletType="1" if list_kind == "ordered" else "bullet",
                leftIndent=16,
                bulletFontName="Helvetica",
            )
        )
        story.append(Spacer(1, 0.03 * inch))
        list_buf = []
        list_kind = None

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_paragraph()
            flush_list()
            flush_table()
            in_code = not in_code
            if not in_code:
                flush_code()
            continue

        if in_code:
            code_buf.append(line)
            continue

        if not stripped:
            flush_paragraph()
            flush_list()
            flush_table()
            story.append(Spacer(1, 0.04 * inch))
            continue

        if "|" in stripped and stripped.count("|") >= 2:
            flush_paragraph()
            flush_list()
            table_buf.append(line)
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            flush_list()
            flush_table()
            heading_text = heading.group(2).strip()
            if (
                len(story) <= 2
                and len(heading.group(1)) == 1
                and re.sub(r"\s+", " ", heading_text).strip().lower() == normalized_title
            ):
                continue
            level = min(len(heading.group(1)), 3)
            story.append(Paragraph(_inline_markup(heading_text), styles[f"h{level}"]))
            continue

        bullet = re.match(r"^[-*+]\s+(.+)$", stripped)
        if bullet:
            flush_paragraph()
            flush_table()
            item = bullet.group(1).strip()
            if list_kind not in (None, "bullet"):
                flush_list()
            list_kind = "bullet"
            list_buf.append(item)
            continue

        ordered = re.match(r"^\d+[\.\)]\s+(.+)$", stripped)
        if ordered:
            flush_paragraph()
            flush_table()
            item = ordered.group(1).strip()
            if list_kind not in (None, "ordered"):
                flush_list()
            list_kind = "ordered"
            list_buf.append(item)
            continue

        if re.match(r"^[-*_]{3,}$", stripped):
            flush_paragraph()
            flush_list()
            flush_table()
            story.append(Spacer(1, 0.08 * inch))
            continue

        flush_table()
        flush_list()
        paragraph_buf.append(stripped)

    flush_paragraph()
    flush_list()
    flush_table()
    flush_code()
    return story

def export_pdf_bytes(title: str, markdown_text: str) -> bytes:
    markdown_text = normalize_markdown_report(markdown_text, title=title)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.6 * inch,
        title=title,
    )
    doc.build(_markdown_to_story(markdown_text, title=title))
    return buf.getvalue()
