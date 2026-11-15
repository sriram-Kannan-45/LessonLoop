"""Supported teaching languages and versioned language-specific instructions."""
import copy
from app.content import canonical_hash

LANGUAGES = {"en": "English", "ta": "Tamil", "hi": "Hindi", "te": "Telugu", "kn": "Kannada",
             "ml": "Malayalam", "mr": "Marathi", "bn": "Bengali", "gu": "Gujarati", "pa": "Punjabi"}


def language_instruction(code):
    if code == "en":
        return ""
    return (f" For this run the teaching language is {LANGUAGES[code]}, overriding any default English-language instruction. "
            "Use its native script and simple everyday language for the title, explanations, examples, recap and all practice questions/answers. "
            "Explain technical English terms in the selected language at first use; do not merely transliterate unexplained jargon. "
            "Keep JSON property names, source IDs, claim IDs, URLs and evidence paths unchanged. "
            "The original source_passage quotation may stay in its source language; explain its meaning in the selected language. "
            "Evaluator reasons and corrections may be English, but judge beginner comprehension in the selected teaching language. "
            "Do not change facts while translating.")


def language_rubric(rubric, code):
    if code == "en":
        return rubric
    result = copy.deepcopy(rubric)
    result["language"] = code
    result["version"] += "-" + code + "-v1"
    result["checks"].append({"id": "LANGUAGE", "name": "Selected teaching language", "group": "language", "evaluator": "model", "mandatory": True,
                            "pass": f"Teach in simple {LANGUAGES[code]} using its native script throughout title, explanations, examples, recap and practice. Explain necessary English technical terms locally. Original source quotations, source titles, IDs and URLs may remain unchanged.",
                            "fail": "Substantial learner-facing text uses another language, unexplained transliteration, or loses factual meaning in translation.",
                            "evidence": "Select an actual lesson field or identify missing target-language content."})
    result["content_sha256"] = canonical_hash({k: v for k, v in result.items() if k != "content_sha256"})
    return result
