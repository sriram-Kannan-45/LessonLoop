"""Build the project explanation and saved lesson as editable Word documents.

Run with the bundled document-authoring Python runtime (python-docx required).
Final Word deliverables are tracked under docs/submission at the user's request.
Render evidence and other generated artifacts remain under ignored artifacts/.
"""

from pathlib import Path
import re

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "submission"


def inline(paragraph, text):
    """Preserve emphasis and genuine source hyperlinks from the Markdown."""
    pattern = r"(\[[^\]]+\]\(https?://[^)]+\)|\*\*[^*]+\*\*|`[^`]+`)"
    for part in re.split(pattern, text):
        link = re.fullmatch(r"\[([^\]]+)\]\((https?://[^)]+)\)", part)
        if link:
            relation = paragraph.part.relate_to(
                link[2],
                "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                is_external=True,
            )
            hyperlink = OxmlElement("w:hyperlink")
            hyperlink.set(qn("r:id"), relation)
            run = OxmlElement("w:r")
            properties = OxmlElement("w:rPr")
            color = OxmlElement("w:color")
            color.set(qn("w:val"), "1F4E79")
            properties.append(color)
            run.append(properties)
            value = OxmlElement("w:t")
            value.text = link[1]
            run.append(value)
            hyperlink.append(run)
            paragraph._p.append(hyperlink)
        elif part.startswith("**") and part.endswith("**"):
            paragraph.add_run(part[2:-2]).bold = True
        elif part.startswith("`") and part.endswith("`"):
            paragraph.add_run(part[1:-1]).font.name = "Consolas"
        else:
            paragraph.add_run(part)


def build(source, destination, lesson=False):
    document = Document()
    section = document.sections[0]
    section.page_width, section.page_height = Inches(8.27), Inches(11.69)
    section.top_margin = section.bottom_margin = Inches(0.72 if lesson else 0.6)
    section.left_margin = section.right_margin = Inches(0.8)
    for name in ("Normal", "Title", "Subtitle", "Heading 1", "Heading 2", "Heading 3"):
        style = document.styles[name]
        style.font.name = "Calibri"
        style.font.color.rgb = RGBColor(0, 0, 0)
        properties = style.element.find(qn("w:pPr"))
        if properties is not None:
            for border in list(properties.findall(qn("w:pBdr"))):
                properties.remove(border)
    normal = document.styles["Normal"]
    normal.font.size = Pt(11 if lesson else 10.5)
    normal.paragraph_format.space_after = Pt(7 if lesson else 5)
    normal.paragraph_format.line_spacing = 1.12 if lesson else 1.06
    document.styles["Title"].font.size = Pt(25)
    document.styles["Title"].paragraph_format.space_after = Pt(14)
    for name, size in (("Heading 1", 15), ("Heading 2", 12), ("Heading 3", 11)):
        style = document.styles[name]
        style.font.size = Pt(size)
        style.paragraph_format.space_before = Pt(13)
        style.paragraph_format.space_after = Pt(6)
        style.paragraph_format.keep_with_next = True
    document.core_properties.title = (
        "Introduction to RAG Finding Facts for AI" if lesson else "LessonLoop Project Documentation"
    )
    document.core_properties.author = "LessonLoop"
    document.core_properties.subject = "Final lesson content" if lesson else "Project explanation and recording guide"
    code = False
    for line in source.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            if code and document.paragraphs:
                document.paragraphs[-1].paragraph_format.space_after = Pt(7)
            code = not code
            continue
        if not line.strip():
            continue
        if code:
            paragraph = document.add_paragraph()
            paragraph.paragraph_format.space_after = Pt(1)
            paragraph.paragraph_format.line_spacing = 1
            run = paragraph.add_run(line)
            run.font.name = "Consolas"
            run.font.size = Pt(8)
            continue
        heading = re.match(r"^(#{1,4}) (.+)$", line)
        if heading:
            level = len(heading[1])
            title = heading[2]
            if level == 1 and lesson:
                title = "Introduction to RAG Finding Facts for AI"
            # Preserve the saved lesson text; only headings receive punctuation cleanup.
            title = re.sub(r"[^\w\s]", "", title).strip()
            paragraph = document.add_paragraph(title, "Title" if level == 1 else f"Heading {level - 1}")
            if lesson and heading[2] == "Practice questions and answers":
                paragraph.paragraph_format.page_break_before = True
            continue
        if line.startswith("> "):
            line = line[2:]
        bullet = re.match(r"^- (.+)$", line)
        numbered = re.match(r"^\d+\. (.+)$", line)
        if bullet:
            inline(document.add_paragraph(style="List Bullet"), bullet[1])
        elif numbered:
            paragraph = document.add_paragraph()
            paragraph.paragraph_format.left_indent = Inches(0.25)
            paragraph.paragraph_format.first_line_indent = Inches(-0.25)
            inline(paragraph, line)
        else:
            inline(document.add_paragraph(), line)
    if lesson:
        # Keep the historical approved lesson body and audit untouched.
        # Append current project links as a separately labelled section.
        document.add_paragraph("Project links", "Heading 1")
        links = (ROOT / "docs" / "SUBMISSION_LINKS.md").read_text(encoding="utf-8")
        for line in links.split("## Assignment deliverables\n", 1)[1].split("\n## Word copies", 1)[0].splitlines():
            if line.startswith("- "):
                inline(document.add_paragraph(style="List Bullet"), line[2:])
    destination.parent.mkdir(parents=True, exist_ok=True)
    document.save(destination)
    print(destination)


if __name__ == "__main__":
    build(ROOT / "docs" / "PROJECT_DOCUMENTATION.md", OUTPUT / "LessonLoop_Project_Documentation.docx")
    build(ROOT / "submission" / "final-lesson" / "lesson-approved.md", OUTPUT / "LessonLoop_Final_Lesson.docx", lesson=True)
