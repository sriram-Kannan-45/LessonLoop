import json

from app.content import SOURCE_PACK


def markdown_lesson(lesson, status, run_id, sources=None):
    label = "Approved lesson" if status == "APPROVED" else "Review draft — NOT APPROVED"
    lines = [f"# {lesson.get('title', 'Lesson review draft')}", "", f"> {label}. Run `{run_id}`.", ""]
    if status != "APPROVED":
        lines += ["This draft has not met every mandatory check. Do not treat it as a released lesson.", ""]
    sections = [("What you will learn", "learning_objectives"), ("Before you start", "prerequisites"), ("What it is", "what_it_is"), ("Why it matters", "why_it_matters"), ("How it works", "how_it_works")]
    for title, key in sections:
        value = lesson.get(key, "Section missing from this review draft.")
        lines += ["## " + title, ""]
        lines += [f"{index + 1}. {item}" for index, item in enumerate(value)] if isinstance(value, list) else [str(value)]
        lines.append("")
    lines += ["## Worked example", ""]
    example = lesson.get("worked_example", {})
    for key, title in [("context", "Illustrative context"), ("learner_question", "Question"), ("source_passage", "Source passage"), ("retrieved_information", "What the system retrieves and adds"), ("supported_answer", "Supported answer"), ("missing_information_question", "When information is missing"), ("missing_information_answer", "Honest response")]:
        lines += [f"**{title}:** {example.get(key, 'Missing from this draft.')}", ""]
    for title, key in [("Limitations", "limitations"), ("Recap", "recap")]:
        lines += ["## " + title, ""]
        value = lesson.get(key, "Section missing.")
        lines += ["- " + str(item) for item in value] if isinstance(value, list) else [str(value)]
        lines.append("")
    lines += ["## Practice questions and answers", ""]
    for index, item in enumerate(lesson.get("practice_questions", []), 1):
        lines += [f"### {index}. {item.get('question', 'Missing question')}", "", str(item.get("answer", "Missing answer")), ""]
    lines += ["## References", ""]
    sources = {source["id"]: source for source in (sources or SOURCE_PACK["sources"])}
    for reference in lesson.get("source_references", []):
        source = sources.get(reference.get("source_id"))
        if source:
            lines.append(f"- [{source['title']}]({source['url']}) — accessed {source['accessed_at']}.")
    return "\n".join(lines) + "\n"


def audit_report(repository, run_id):
    run = repository.get_run(run_id)
    return {"audit_version": "lessonloop-audit-v1", "provider_note": "Gemini generates and evaluates in separate calls; this is not cross-provider independence.",
            "run": run, "events": repository.events(run_id, 0, 1000)}
