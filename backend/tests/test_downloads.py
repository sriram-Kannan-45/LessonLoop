import io

import pytest
from docx import Document
from fastapi.testclient import TestClient
from pypdf import PdfReader

from app.db import Repository
from app.lesson_schemas import RunRequest
from app.main import create_app
from test_workflow import FakeAI, start


@pytest.mark.parametrize('status', ['APPROVED', 'NEEDS_REVIEW', 'CANCELLED'])
@pytest.mark.parametrize('format', ['txt', 'pdf', 'docx'])
def test_download_formats_preserve_content_status_and_source_attribution(settings, status, format):
    repo = Repository(settings.database_path)
    run = start(repo, FakeAI(failures=3 if status != 'APPROVED' else 0))
    if status == 'CANCELLED': repo.finish(run['id'], status)
    with TestClient(create_app(settings=settings, repository=repo)) as client:
        response = client.get(f"/api/runs/{run['id']}/export?format={format}")
    assert response.status_code == 200
    assert response.headers['content-disposition'].endswith(f'.{format}"')
    assert ('review-not-approved' if status != 'APPROVED' else 'approved') in response.headers['content-disposition']
    if format == 'pdf':
        assert response.headers['content-type'] == 'application/pdf'
        reader = PdfReader(io.BytesIO(response.content))
        content = '\n'.join(page.extract_text() for page in reader.pages)
    elif format == 'docx':
        assert response.content.startswith(b'PK')
        assert 'wordprocessingml' in response.headers['content-type']
        document = Document(io.BytesIO(response.content))
        content = '\n'.join(p.text for p in document.paragraphs)
        assert document.paragraphs[0].style.name == 'Title'
        assert not document.styles['Title'].element.xpath('.//w:pBdr')
    else:
        content = response.text
        assert 'text/plain' in response.headers['content-type']
        assert not content.startswith('# ')
    title = (run['final_lesson'] or run['review_draft'])['title']
    assert ' '.join(title.split()) in ' '.join(content.split())
    assert status in content and run['id'] in content
    assert 'References' in content and 'https://' in content
    assert ('NOT APPROVED' in content) == (status != 'APPROVED')
    assert 'Practice questions and answers' in content


@pytest.mark.parametrize('format', ['txt', 'pdf', 'docx'])
def test_no_saved_lesson_does_not_produce_an_empty_document(settings, format):
    repo = Repository(settings.database_path)
    ident = repo.create_run(RunRequest(reference_pack_id='rag-primary-v1'), 'mocked', 'mocked')
    repo.finish(ident, 'ERROR')
    with TestClient(create_app(settings=settings, repository=repo)) as client:
        response = client.get(f'/api/runs/{ident}/export?format={format}')
    assert response.status_code == 409 and response.json()['error_code'] == 'NO_DRAFT'
