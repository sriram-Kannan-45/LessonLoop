"""Readable lesson downloads with explicit approval status and source attribution."""
import io
import os
import re
from pathlib import Path
from xml.sax.saxutils import escape


class DocumentExportUnavailable(Exception):
    pass


def text(value):
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ufffe\uffff]", "", str(value))


def lesson_blocks(lesson, status, run_id, sources):
    label = "Approved lesson" if status == "APPROVED" else "Review draft — NOT APPROVED"
    blocks = [("title", text(lesson.get("title", "Lesson review draft"))),
              ("status", f"{label} | Status: {status}"), ("body", "Run: " + run_id)]
    if status != "APPROVED":
        blocks.append(("body", "This draft has not met every mandatory check. Do not treat it as a released lesson."))
    def section(title, value):
        blocks.append(("heading", title))
        if isinstance(value, list):
            blocks.extend(("body", f"{i}. {text(item)}") for i, item in enumerate(value, 1))
        else:
            blocks.append(("body", text(value)))
    for title, key in [("What you will learn", "learning_objectives"), ("Before you start", "prerequisites"),
                       ("What it is", "what_it_is"), ("Why it matters", "why_it_matters"), ("Step by step explanation", "how_it_works")]:
        section(title, lesson.get(key, "Section missing from this review draft."))
    blocks.append(("heading", "Worked example"))
    example = lesson.get("worked_example", {})
    if not isinstance(example, dict):
        example = {}
    for title, key in [("Illustrative context", "context"), ("Question", "learner_question"), ("Source passage", "source_passage"),
                       ("Reference information used", "retrieved_information"), ("Supported answer", "supported_answer"),
                       ("When information is missing", "missing_information_question"), ("Honest response", "missing_information_answer")]:
        blocks.extend([("subheading", title), ("body", text(example.get(key, "Missing from this draft.")))])
    section("Limitations", lesson.get("limitations", "Section missing."))
    section("Recap", lesson.get("recap", "Section missing."))
    blocks.append(("heading", "Practice questions and answers"))
    for index, item in enumerate(lesson.get("practice_questions", []), 1):
        if isinstance(item, dict):
            blocks.extend([("subheading", f"{index}. {text(item.get('question', 'Missing question'))}"), ("body", text(item.get("answer", "Missing answer")))])
    blocks.append(("heading", "References"))
    by_id = {source["id"]: source for source in sources}
    for ref in lesson.get("source_references", []):
        if not isinstance(ref, dict):
            continue
        source = by_id.get(ref.get("source_id"))
        if source:
            blocks.append(("body", text(f"{source['title']}\n{source['url']}\nAccessed: {source['accessed_at']}")))
            if source.get("license"):
                blocks.append(("body", text(f"Source excerpts: Wikipedia contributors, {source['license']}\n{source['license_url']}")))
    return blocks


def text_lesson(lesson, status, run_id, sources):
    return "\n\n".join(value for _, value in lesson_blocks(lesson, status, run_id, sources)) + "\n"


def docx_lesson(lesson, status, run_id, sources):
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.oxml.ns import qn
    document = Document()
    section = document.sections[0]
    section.page_width, section.page_height = Inches(8.5), Inches(11)
    section.top_margin = section.bottom_margin = Inches(.75)
    section.left_margin = section.right_margin = Inches(.8)
    normal = document.styles["Normal"]
    native = any("\u0900" <= ch <= "\u0dff" for ch in str(lesson))
    normal.font.name, normal.font.size = "Nirmala UI" if native else "Arial", Pt(11)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.12
    for name, size in [("Title", 23), ("Heading 1", 15), ("Heading 2", 12)]:
        style = document.styles[name]
        style.font.name, style.font.size, style.font.color.rgb = normal.font.name, Pt(size), RGBColor(0, 0, 0)
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.space_before = Pt(12)
        style.paragraph_format.space_after = Pt(6)
    for style in document.styles:
        for border in style.element.xpath(".//w:pBdr"):
            border.getparent().remove(border)
    for kind, value in lesson_blocks(lesson, status, run_id, sources):
        paragraph = document.add_paragraph(value, {"title": "Title", "heading": "Heading 1", "subheading": "Heading 2"}.get(kind, "Normal"))
        if native:
            for run in paragraph.runs:
                run.font.name = "Nirmala UI"
                fonts = run._element.get_or_add_rPr().get_or_add_rFonts()
                fonts.set(qn("w:cs"), "Nirmala UI")
                fonts.set(qn("w:eastAsia"), "Nirmala UI")
                run.font.color.rgb = RGBColor(0, 0, 0)
                if kind == "title":
                    run.font.size = Pt(23)
                    run.font.bold = True
        if kind == "status":
            for run in paragraph.runs:
                run.bold = True
    section.footer.paragraphs[0].text = "LessonLoop | " + ("Approved lesson" if status == "APPROVED" else "Review draft - NOT APPROVED")
    output = io.BytesIO()
    document.save(output)
    return output.getvalue()


def pdf_lesson(lesson, status, run_id, sources):
    import reportlab
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    font_dir = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    fallback = Path(reportlab.__file__).parent / "fonts"
    for name, file, bundled in [("LessonBody", "arial.ttf", "Vera.ttf"), ("LessonBold", "arialbd.ttf", "VeraBd.ttf")]:
        if name not in pdfmetrics.getRegisteredFontNames():
            path = font_dir / file
            pdfmetrics.registerFont(TTFont(name, str(path if path.exists() else fallback / bundled)))
    native = any("\u0900" <= ch <= "\u0dff" for ch in str(lesson))
    body_font, bold_font = "LessonBody", "LessonBold"
    if native:
        path = Path(os.environ.get("LESSONLOOP_PDF_FONT", str(font_dir / "Nirmala.ttc")))
        if not path.exists():
            raise DocumentExportUnavailable("A native-script PDF font is required. Install Nirmala UI or configure LESSONLOOP_PDF_FONT; TXT and Word downloads remain available.")
        body_font, bold_font = "LessonIndicBody", "LessonIndicBold"
        for name, index in [(body_font, 0), (bold_font, 1 if path.suffix.lower() == ".ttc" else 0)]:
            if name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(name, str(path), subfontIndex=index, shapable=True))
    body = ParagraphStyle("LessonBody", fontName=body_font, fontSize=11, leading=16, spaceAfter=9, shaping=int(native))
    title = ParagraphStyle("LessonTitle", parent=body, fontName=bold_font, fontSize=22, leading=27, spaceAfter=16, keepWithNext=True)
    heading = ParagraphStyle("LessonHeading", parent=body, fontName=bold_font, fontSize=15, leading=20, spaceBefore=14, keepWithNext=True)
    subheading = ParagraphStyle("LessonSubheading", parent=body, fontName=bold_font, fontSize=11, leading=16, spaceBefore=7, keepWithNext=True)
    status_style = ParagraphStyle("LessonStatus", parent=body, fontName=bold_font)
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=letter, leftMargin=57.6, rightMargin=57.6, topMargin=54, bottomMargin=54,
                            title=text(lesson.get("title", "Lesson review draft")), author="LessonLoop")
    story = []
    for kind, value in lesson_blocks(lesson, status, run_id, sources):
        style = {"title": title, "heading": heading, "subheading": subheading, "status": status_style}.get(kind, body)
        story.append(Paragraph(escape(value).replace("\n", "<br/>"), style))
    def footer(canvas, document):
        canvas.saveState()
        canvas.setFont("LessonBody", 8)
        canvas.drawString(57.6, 30, "LessonLoop | " + ("Approved lesson" if status == "APPROVED" else "Review draft - NOT APPROVED"))
        canvas.drawRightString(letter[0] - 57.6, 30, str(document.page))
        canvas.restoreState()
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return output.getvalue()
