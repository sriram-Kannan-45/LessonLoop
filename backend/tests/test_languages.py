import asyncio
import pytest
from fastapi.testclient import TestClient
from app.db import Repository
from app.languages import LANGUAGES
from app.lesson_schemas import RunRequest
from app.main import create_app
from app.services.lesson_ai import LessonAI, evaluation_groups
from test_topics import TopicAI, wiki_transport, pack, lesson_for, verdicts

REAL_GENERATE = LessonAI.generate
REAL_EVALUATE = LessonAI.evaluate


@pytest.mark.parametrize('code', list(LANGUAGES))
def test_language_is_frozen_with_appropriate_prompt_and_rubric(settings, code):
    repo = Repository(settings.database_path)
    ident = repo.create_run(RunRequest(language=code, reference_pack_id='rag-primary-v1'), 'mocked', 'mocked')
    run = repo.get_run(ident)
    assert run['language'] == code
    assert run['selected_memory'] == []
    assert len(run['rubric_snapshot']['checks']) == (14 if code == 'en' else 15)
    if code != 'en':
        assert LANGUAGES[code] in repo.prompt(run['generator_prompt_version'])['instructions']
        assert 'LANGUAGE' in [key for group in evaluation_groups(run['rubric_snapshot']) for key in group]
    assert Repository(settings.database_path).get_run(ident)['language'] == code


def test_english_lesson_cannot_pass_tamil_language_check(settings, monkeypatch):
    settings.gemini_api_key = 'fake-language-key'
    wiki_transport(monkeypatch, 'Photosynthesis')
    class WrongLanguage(TopicAI):
        async def evaluate(self, lesson, sources, rubric, *args, **kwargs):
            raw, usage = await super().evaluate(lesson, sources, rubric)
            for check in raw['checks']:
                if check['check_id'] == 'LANGUAGE':
                    check.update(passed=False, reason='Mocked language judgment: this lesson is English rather than Tamil.', required_change='Write the learner-facing lesson in Tamil.')
            return raw, usage
    with TestClient(create_app(settings=settings, ai=WrongLanguage())) as client:
        ident = client.post('/api/runs', json={'topic':'Photosynthesis','language':'ta'}).json()['id']
        for _ in range(200):
            run = client.get('/api/runs/'+ident).json()
            if run['status'] != 'RUNNING': break
        assert run['status'] == 'NEEDS_REVIEW' and run['attempt_count'] == 3
        assert len(run['attempts'][-1]['evaluation']) == 15
        assert run['final_lesson'] is None and run['language'] == 'ta'
        assert client.post('/api/runs',json={'language':'unsupported'}).status_code == 422


def test_generation_and_evaluation_receive_tamil_context(settings, monkeypatch):
    from app.languages import language_rubric, language_instruction
    from app.topics import topic_rubric
    source = pack('RAG')
    lesson = lesson_for('RAG', source)
    ai = LessonAI(settings)
    calls = []
    async def call(model, instructions, data, schema, *args, **kwargs):
        calls.append(data)
        assert 'Tamil' in instructions
        return (verdicts(lesson,data['expected_check_ids']) if 'expected_check_ids' in data else lesson), {}
    ai.call = call
    rubric = language_rubric(topic_rubric('RAG'), 'ta')
    asyncio.run(REAL_GENERATE(ai, {'language':'ta','topic':'RAG','source_pack':source,'instructions':language_instruction('ta')}))
    raw, _ = asyncio.run(REAL_EVALUATE(ai,lesson,source,rubric))
    assert calls[0]['language'] == 'Tamil'
    assert all(data['teaching_language'] == 'Tamil' for data in calls[1:])
    assert len(raw['checks']) == 13


def test_tamil_exports_preserve_native_text_and_report_missing_pdf_font(settings, monkeypatch):
    from app.download_documents import docx_lesson,text_lesson,pdf_lesson,DocumentExportUnavailable
    from app.dataset import BASE
    from app.content import SOURCE_PACK
    from docx import Document
    import copy,io
    lesson=copy.deepcopy(BASE);lesson['title']='தமிழ் பாடம் சோதனை'
    args=(lesson,'NEEDS_REVIEW','test-native',SOURCE_PACK['sources'])
    assert lesson['title'] in text_lesson(*args)
    assert Document(io.BytesIO(docx_lesson(*args))).paragraphs[0].text == lesson['title']
    monkeypatch.setenv('LESSONLOOP_PDF_FONT', str(settings.database_path.parent/'missing.ttf'))
    with pytest.raises(DocumentExportUnavailable): pdf_lesson(*args)


def test_existing_english_history_survives_language_column_migration(settings):
    repo=Repository(settings.database_path)
    ident=repo.create_run(RunRequest(reference_pack_id='rag-primary-v1'),'mocked','mocked')
    repo.finish(ident,'ERROR')
    before=repo.get_run(ident)
    with repo.connection() as con: con.execute('ALTER TABLE runs DROP COLUMN language')
    assert Repository(settings.database_path).get_run(ident)==before


def test_english_learned_instruction_is_not_injected_into_tamil(settings):
    repo=Repository(settings.database_path)
    ident=repo.create_run(RunRequest(reference_pack_id='rag-primary-v1'),'mocked','mocked');repo.finish(ident,'ERROR')
    exp=repo.create_experiment('TERMS_EXPLAINED','Mocked English-only learned instruction.',[ident],'mocked-language-scope')
    repo.finish_experiment(exp,'ACTIVATED',[{'mocked':True}])
    native=repo.create_run(RunRequest(language='ta',reference_pack_id='rag-primary-v1'),'mocked','mocked')
    r=repo.get_run(native)
    assert r['selected_memory']==[]
    assert 'Mocked English-only learned instruction.' not in repo.prompt(r['generator_prompt_version'])['instructions']
    repo.finish(native,'ERROR')
    assert native not in repo.supporting_runs('TERMS_EXPLAINED')
