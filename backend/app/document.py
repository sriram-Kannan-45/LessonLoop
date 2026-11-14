"""Create a clean, escaped HTML document from an actually approved run."""
import html
from pathlib import Path

from app.exports import markdown_lesson


def clean_document(run, sources):
    if run["status"] != "APPROVED" or not run["final_lesson"]:
        raise ValueError("Only an actually approved run can create the submission document.")
    lesson = run["final_lesson"]
    escape = html.escape
    blocks = ["<h1>" + escape(lesson["title"]) + "</h1>", "<p class='subtitle'>A beginner lesson in simple English</p>"]
    def section(title, value):
        blocks.append("<section><h2>" + escape(title) + "</h2>")
        if isinstance(value, list):
            blocks.append("<ol>" + "".join("<li>" + escape(item) + "</li>" for item in value) + "</ol>")
        else:
            blocks.append("<p>" + escape(value).replace("\n", "<br>") + "</p>")
        blocks.append("</section>")
    for title, key in [("What you will learn", "learning_objectives"), ("Before you start", "prerequisites"), ("What it is", "what_it_is"), ("Why it matters", "why_it_matters"), ("How it works", "how_it_works")]:
        section(title, lesson[key])
    blocks.append("<section class='example'><h2>Worked example</h2>")
    for key, title in [("context", "Illustrative example"), ("learner_question", "Your question"), ("source_passage", "The source passage"), ("retrieved_information", "What is retrieved and added"), ("supported_answer", "A supported answer"), ("missing_information_question", "A question without enough information"), ("missing_information_answer", "The honest response")]:
        blocks.append("<h3>" + title + "</h3><p>" + escape(lesson["worked_example"][key]) + "</p>")
    blocks.append("</section>")
    section("What to be careful about", lesson["limitations"])
    section("A quick recap", lesson["recap"])
    blocks.append("<section><h2>Practice questions and answers</h2>")
    for index, item in enumerate(lesson["practice_questions"], 1):
        blocks.append(f"<h3>{index}. {escape(item['question'])}</h3><p>{escape(item['answer'])}</p>")
    blocks.append("</section><section><h2>References</h2><ul>")
    for ref in lesson["source_references"]:
        source = next(source for source in sources if source["id"] == ref["source_id"])
        blocks.append(f"<li><a href='{escape(source['url'], quote=True)}'>{escape(source['title'])}</a></li>")
    blocks.append("</ul></section>")
    return """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Introduction to RAG lesson</title><style>
body{font-family:Arial,sans-serif;color:#282c3a;background:#fff;margin:0;line-height:1.8;font-size:16px}main{max-width:750px;margin:55px auto;padding:0 28px 60px}h1{font-size:32px;line-height:1.25;color:#171a24;margin:0 0 12px}h2{font-size:23px;line-height:1.4;color:#252536;margin:35px 0 14px}h3{font-size:17px;margin:23px 0 8px}p{margin:8px 0 15px}.subtitle{color:#6b6b7a;margin-bottom:35px}li{padding-left:5px;margin-bottom:12px}a{color:#5145a8;overflow-wrap:anywhere}.example{padding:0 22px 18px;background:#f5f6fa;border:1px solid #e5e7ef;border-radius:6px}section{break-inside:auto}h1,h2,h3{break-after:avoid}p,li{orphans:3;widows:3}@media print{body{font-size:11pt}main{max-width:none;margin:0;padding:0}.example{background:white}a{color:inherit}@page{size:A4;margin:22mm}}@media(max-width:500px){main{margin-top:30px;padding:0 20px 35px}h1{font-size:28px}h2{font-size:21px}}
</style></head><body><main>""" + "\n".join(blocks) + "</main></body></html>"
