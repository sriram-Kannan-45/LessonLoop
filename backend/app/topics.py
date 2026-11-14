"""On-demand topic references. Only the fixed public Wikipedia API is fetched."""
import re
from datetime import datetime, timezone
from urllib.parse import quote

import httpx

from app.content import canonical_hash
from app.services.lesson_ai import WorkflowError

WIKI_API = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "LessonLoop/1.0 (https://github.com/sriram-Kannan-45/LessonLoop)"


def topic_rubric(topic):
    definitions = [
        ("TOPIC_DEFINITION", "Accurate topic introduction", "Define the requested topic accurately, explain its scope and avoid substituting another subject."),
        ("TOPIC_RELEVANCE", "Relevant learning objectives", "The objectives and all sections address the requested topic and the beginner's needs."),
        ("CORE_EXPLANATION", "Clear explanation of the main ideas", "Explain the important process, method, relationships or sequence of ideas step by step, as appropriate to this subject."),
        ("KEY_CONCEPTS", "Essential concepts covered", "Cover the central concepts needed for an introductory understanding, consistent with the retrieved references."),
        ("CONCEPT_DISTINCTIONS", "Important distinctions are correct", "Distinguish related concepts where needed and avoid misleading simplifications or common misconceptions."),
        ("GROUNDED_CLAIMS", "Factual claims supported", "Material factual claims agree with the frozen reference excerpts. Clearly separate invented examples, assumptions and deductions from reported facts."),
        ("TERMS_EXPLAINED", "Technical terms explained on first use", "Explain every essential specialist term in ordinary language before or at first meaningful use, in every section and practice answer."),
        ("NO_PREREQUISITES", "No hidden background assumptions", "Teach without assuming prior specialist, coding or subject knowledge; familiar examples should respect the learner's age."),
        ("WORKED_EXAMPLE", "A complete relevant worked example", "Show a concrete question or task, a reference passage or explicitly invented example data, relevant information and a supported answer or solution."),
        ("HONEST_LIMITATIONS", "Scope and assumptions are honest", "State relevant assumptions, boundaries or limitations. Avoid universal guarantees that exceed the evidence or the subject's conditions."),
        ("MISSING_INFORMATION", "Missing information handled honestly", "Include an example question that cannot be answered from the supplied facts, identify what is missing and avoid inventing an answer."),
        ("FLOW_AND_PRACTICE", "Coherent lesson and correct practice", "Definitions, steps, example and recap agree, and all three practice answers are correct and supported by the lesson."),
    ]
    checks = [
        {"id": "STRUCTURE", "name": "Complete lesson structure", "group": "general", "pass": "All structured lesson sections, a complete example and three practice questions with answers are present.", "fail": "Required content is absent or malformed.", "evidence": "Local schema validation.", "evaluator": "code", "mandatory": True},
        {"id": "SOURCES", "name": "Reference identifiers and example labelling", "group": "general", "pass": "Source and claim pairs exist in this run's frozen references. The teaching example is labelled illustrative, fictional or invented.", "fail": "Unknown source/claim pairs or missing example label.", "evidence": "Local source mapping validation.", "evaluator": "code", "mandatory": True},
    ]
    for key, name, condition in definitions:
        checks.append({"id": key, "name": name, "group": "topic", "pass": condition,
                       "fail": "The passing condition is absent, contradicted or not supported by the actual lesson.",
                       "evidence": "An exact relevant lesson excerpt or an explicit missing-content explanation; use only this run's claim IDs.",
                       "evaluator": "model", "mandatory": True})
    rubric = {"kind": "general", "version": "beginner-topic-v1-" + canonical_hash(topic)[:12], "topic": topic,
              "release_rule": "Every mandatory check must pass. Never approve on retry exhaustion.", "checks": checks}
    rubric["content_sha256"] = canonical_hash(rubric)
    return rubric


def pending_pack(topic):
    return {"id": "auto", "version": "pending-" + canonical_hash(topic)[:16], "topic": topic,
            "status": "pending", "review_note": "Topic references have not been collected yet.", "sources": [], "claims": []}


async def _get(client, params):
    try:
        async with client.stream("GET", WIKI_API, params={"format": "json", "formatversion": 2, "utf8": 1, **params}) as response:
            response.raise_for_status()
            data = bytearray()
            async for chunk in response.aiter_bytes():
                data.extend(chunk)
                if len(data) > 1_000_000:
                    raise ValueError("Reference response too large")
        import json
        result = json.loads(data)
        if not isinstance(result, dict) or "error" in result or not isinstance(result.get("query"), dict):
            raise ValueError("Invalid reference response")
        return result
    except (httpx.HTTPError, ValueError, TypeError):
        raise WorkflowError("REFERENCES_UNAVAILABLE", "Topic references could not be retrieved. Check your connection and try again; no lesson was approved.") from None


async def collect_topic_references(topic):
    query = re.sub(r"^(?:introduction to|basics of|learn about|learn)\s+", "", topic, flags=re.IGNORECASE).strip() or topic
    async with httpx.AsyncClient(timeout=httpx.Timeout(15, connect=8), headers={"User-Agent": USER_AGENT}, follow_redirects=False) as client:
        found = await _get(client, {"action": "query", "list": "search", "srsearch": query, "srlimit": 3, "srnamespace": 0})
        hits = found.get("query", {}).get("search", [])
        if not isinstance(hits, list):
            raise WorkflowError("REFERENCES_UNAVAILABLE", "The reference search returned invalid data. Please try again.")
        ids = [str(hit["pageid"]) for hit in hits[:3] if isinstance(hit, dict) and isinstance(hit.get("pageid"), int) and hit["pageid"] > 0]
        if not ids:
            raise WorkflowError("REFERENCES_NOT_FOUND", "No usable public references were found for this topic. Try a more specific subject name; no lesson was approved.")
        fetched = await _get(client, {"action": "query", "pageids": "|".join(ids), "prop": "extracts|revisions|pageprops", "ppprop": "disambiguation", "explaintext": 1, "exintro": 1, "exlimit": 3, "exchars": 2600, "rvprop": "ids|timestamp", "redirects": 1})
    pages = fetched.get("query", {}).get("pages", [])
    if not isinstance(pages, list):
        raise WorkflowError("REFERENCES_UNAVAILABLE", "The reference service returned invalid page data. Please try again.")
    by_id = {str(page.get("pageid")): page for page in pages if isinstance(page, dict)}
    sources, claims = [], []
    accessed = datetime.now(timezone.utc).isoformat()
    for page_id in ids:
        page = by_id.get(page_id, {})
        extract, title = page.get("extract", ""), page.get("title", "")
        if not isinstance(extract, str) or not isinstance(title, str) or not title:
            continue
        if "(disambiguation)" in title.lower() or "disambiguation" in (page.get("pageprops") or {}):
            continue
        paragraphs = [part.strip() for part in extract.split("\n") if len(part.strip()) >= 100 and not part.strip().startswith("==")]
        if not paragraphs:
            continue
        sid, notes = "S" + str(len(sources) + 1), []
        for paragraph in paragraphs[:2]:
            text = paragraph[:800].rsplit(" ", 1)[0] if len(paragraph) > 800 else paragraph
            cid = "C" + str(len(claims) + 1).zfill(2)
            note_id = "N" + str(len(claims) + 1)
            notes.append({"id": note_id, "text": text, "claim_ids": [cid]})
            claims.append({"id": cid, "note_ids": [note_id], "source_ids": [sid]})
        revisions = page.get("revisions")
        revision = revisions[0] if isinstance(revisions, list) and revisions and isinstance(revisions[0], dict) else {}
        revision_id = revision.get("revid")
        url = "https://en.wikipedia.org/wiki/" + quote(title.replace(" ", "_"), safe="")
        revision_url = "https://en.wikipedia.org/w/index.php?oldid=" + str(revision_id) if isinstance(revision_id, int) else url
        sources.append({"id": sid, "title": title, "url": revision_url, "canonical_url": url, "accessed_at": accessed,
                        "version": str(revision_id or "current"), "revision_id": revision_id,
                        "revision_url": revision_url,
                        "license": "CC BY-SA 4.0", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
                        "notes": notes, "notes_sha256": canonical_hash(notes)})
    if not sources:
        raise WorkflowError("REFERENCES_NOT_FOUND", "The topic search returned no usable reference text. Try a more specific topic; no lesson was approved.")
    pack = {"id": "auto", "topic": topic, "status": "retrieved", "retrieved_at": accessed,
            "review_note": "Public Wikipedia excerpts retrieved for this topic and frozen for this run. These are automatically collected secondary references, not a human-reviewed reference pack. Inspect their relevance, revision and original pages.",
            "provenance": "Wikipedia search and text-extract APIs; no model-generated citations", "sources": sources, "claims": claims}
    pack["version"] = "topic-references-v1-" + canonical_hash(pack)[:16]
    pack["content_sha256"] = canonical_hash(pack)
    return pack
