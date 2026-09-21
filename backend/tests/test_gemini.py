import json
from unittest.mock import Mock

import httpx
import pytest

from app.config import settings
from app.services.gemini_service import GeminiError, GeminiService


def response_for(payload):
    comments = json.loads(payload['contents'][0]['parts'][0]['text'])
    result = {
        'comments': [{'id': c['id'], 'sentiment': 'positive' if c['id'] % 2 == 0 else 'negative',
                      'emotion': 'joy' if c['id'] % 2 == 0 else 'anger',
                      'topics': ['team', 'team']} for c in comments],
        'keywords': ['ทีม', 'ทีม', 'invented-keyword'], 'summary': 'ความคิดเห็นมีทั้งคำชมและคำวิจารณ์',
    }
    return httpx.Response(200, json={'candidates': [{'finishReason': 'STOP', 'content': {
        'parts': [{'text': json.dumps(result)}]}}]})


@pytest.fixture
def configured(monkeypatch):
    monkeypatch.setattr(settings, 'GEMINI_API_KEY', 'secret-test-key')


def test_request_and_aggregation(configured):
    def handle(request):
        assert request.url.host == 'generativelanguage.googleapis.com'
        assert 'key=' not in str(request.url)
        assert request.headers['x-goog-api-key'] == 'secret-test-key'
        payload = json.loads(request.content)
        assert payload['generationConfig']['responseMimeType'] == 'application/json'
        schema = payload['generationConfig']['responseSchema']
        assert schema['properties']['comments']['items']['properties']['sentiment']['enum'] == ['positive', 'neutral', 'negative']
        assert '$ref' not in json.dumps(schema)
        assert 'additionalProperties' not in json.dumps(schema)
        return response_for(payload)
    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        result = GeminiService(client).analyze_comments(['ทีมนี้ดี', 'ทีมเล่นแย่'])
    assert result['sentiment'] == {'positive': 50, 'negative': 50, 'neutral': 0, 'sample_size': 2}
    assert result['categories']['categories'] == [{'category': 'team', 'percentage': 100}]
    assert result['keywords'] == [{'keyword': 'ทีม', 'count': 2, 'importance': 1, 'trend_percent': None}]


def test_missing_key_and_empty_comments(monkeypatch):
    monkeypatch.setattr(settings, 'GEMINI_API_KEY', '')
    client = Mock()
    assert GeminiService(client).analyze_comments([])['summary']['based_on_comments'] == 0
    with pytest.raises(GeminiError) as error:
        GeminiService(client).analyze_comments(['test'])
    assert error.value.status_code == 503
    client.post.assert_not_called()


@pytest.mark.parametrize('status, expected', [(400, 502), (401, 503), (403, 503), (404, 502), (429, 429), (500, 502)])
def test_api_errors_are_safe(configured, status, expected):
    client = Mock()
    client.post.return_value = httpx.Response(status, text='secret-test-key upstream diagnostic')
    with pytest.raises(GeminiError) as error:
        GeminiService(client).analyze_comments(['test'])
    assert error.value.status_code == expected
    assert 'secret-test-key' not in str(error.value)


@pytest.mark.parametrize('body', [
    {}, [], None, {'candidates': []}, {'candidates': [None]},
    {'candidates': [{'finishReason': 'MAX_TOKENS'}]},
    {'candidates': [{'finishReason': 'STOP', 'content': {'parts': [{'text': 'invalid json'}]}}]},
])
def test_invalid_output_rejected(configured, body):
    client = Mock()
    client.post.return_value = httpx.Response(200, json=body)
    with pytest.raises(GeminiError):
        GeminiService(client).analyze_comments(['test'])


@pytest.mark.parametrize('ids', [[0, 0], [0], [0, 2]])
def test_missing_or_duplicate_ids_rejected(configured, ids):
    result = {'comments': [{'id': i, 'sentiment': 'neutral', 'emotion': 'neutral', 'topics': ['other']} for i in ids],
              'keywords': [], 'summary': 'สรุป'}
    client = Mock()
    client.post.return_value = httpx.Response(200, json={'candidates': [{'finishReason': 'STOP', 'content': {
        'parts': [{'text': json.dumps(result)}]}}]})
    with pytest.raises(GeminiError):
        GeminiService(client).analyze_comments(['one', 'two'])


@pytest.mark.parametrize('error, status', [(httpx.ReadTimeout('secret-test-key'), 504),
                                         (httpx.ConnectError('secret-test-key'), 503)])
def test_connection_errors(configured, error, status):
    client = Mock()
    client.post.side_effect = error
    with pytest.raises(GeminiError) as exc:
        GeminiService(client).analyze_comments(['test'])
    assert exc.value.status_code == status
    assert 'secret-test-key' not in str(exc.value)
    assert client.post.call_count == 1


def test_incomplete_response_retried_once(configured):
    client = Mock()
    calls = []
    def post(*args, **kwargs):
        calls.append(kwargs['json'])
        if len(calls) == 1:
            return httpx.Response(200, json={'candidates': [{'finishReason': 'MAX_TOKENS'}]})
        return response_for(kwargs['json'])
    client.post.side_effect = post
    result = GeminiService(client).analyze_comments(['ทีมดี', 'ทีมแย่'])
    assert result['sentiment']['sample_size'] == 2
    assert len(calls) == 2
    assert 'exactly 2 comment results' in calls[0]['systemInstruction']['parts'][0]['text']


def test_invalid_response_retry_is_bounded(configured):
    client = Mock()
    client.post.return_value = httpx.Response(200, json={})
    with pytest.raises(GeminiError):
        GeminiService(client).analyze_comments(['test'])
    assert client.post.call_count == 2


def test_safety_response_not_retried(configured):
    client = Mock()
    client.post.return_value = httpx.Response(200, json={'candidates': [{'finishReason': 'SAFETY'}]})
    with pytest.raises(GeminiError):
        GeminiService(client).analyze_comments(['test'])
    assert client.post.call_count == 1
