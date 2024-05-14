import json

import pytest
from requests.models import Response
from unittest.mock import patch, MagicMock
from src.kintsugi.api import Api, Config, PredictionHandler, FeedbackHandler, ResponseException


@pytest.fixture
def config():
    return Config(
        x_api_key='x-api-key-for-tests',
        url='https://tests.kintsugihealth.com'
    )


@pytest.fixture
def api(config):
    api = Api('user_id', True, config)
    api.new_session_id = MagicMock()
    return api


def test_api_initialization(config):
    api = Api('test_user', True, config)
    assert api.user_id == 'test_user'
    assert api.is_initiated is True
    assert api.config == config
    assert api.metadata == {}


def test_get_common_headers(config):
    api = Api('test_user', True, config)
    expected_headers = {
        'accept': 'application/json',
        'X-API-Key': config.x_api_key,
    }
    assert api.get_common_headers() == expected_headers


@patch('requests.post')
def test_new_session_id(mock_post, config):
    api = Api('test_user', True, config)
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"session_id": "test_session_id"}
    mock_post.return_value = mock_response

    assert api.new_session_id() == "test_session_id"


@patch('requests.post')
def test_new_session_id_failure(mock_post, config):
    api = Api('test_user', True, config)
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_post.return_value = mock_response

    with pytest.raises(ResponseException):
        api.new_session_id()


@patch("requests.post")
def test_predict(mock_post, api):
    mock_response = Response()
    mock_response.status_code = 202
    mock_response._content = b'{"session_id":"1234"}'
    mock_post.return_value = mock_response

    handler = PredictionHandler(api)
    session_id = handler.predict('test_audio.wav')

    assert session_id == '1234'


@patch("requests.get")
def test_get_prediction_by_session(mock_get, api):
    mock_response = Response()
    mock_response.status_code = 200
    mock_response._content = b'{"prediction":"prediction"}'
    mock_get.return_value = mock_response

    handler = PredictionHandler(api)
    result = handler.get_prediction_by_session('1234')

    assert result['prediction'] == 'prediction'


@patch("requests.get")
def test_get_prediction_by_user(mock_get, api):
    mock_response = Response()
    mock_response.status_code = 200
    mock_response._content = b'{"prediction":"prediction"}'
    mock_get.return_value = mock_response

    handler = PredictionHandler(api)
    result = handler.get_prediction_by_user('user_id')

    assert result['prediction'] == 'prediction'


@patch("requests.patch")
def test_depression(mock_patch, api):
    handler = FeedbackHandler(api)
    mock_patch.return_value.status_code = 200
    handler.depression('1', 'true')
    mock_patch.assert_called_once()

    with pytest.raises(ResponseException):
        mock_patch.return_value.status_code = 400
        handler.depression('1', 'true')


def test_depression_failure(api):
    handler = FeedbackHandler(api)
    with pytest.raises(ValueError):
        handler.depression('1', 'wrong_data')


@pytest.mark.parametrize('answers', [
    [1, 2],
    [1, 2, 1, 1, 2, 1, 1, 2, 1],
])
@patch("requests.patch")
def test_phq(mock_patch, answers, api):
    handler = FeedbackHandler(api)
    mock_patch.return_value.status_code = 200
    session_id = 'session-123'
    count = len(answers)

    if count == 2:
        handler.phq_2(session_id, answers)
    else:
        handler.phq_9(session_id, answers)

    mock_patch.assert_called_once_with(
        f'{api.config.url}/feedback/phq/{count}',
        headers=api.get_common_headers(),
        data=json.dumps({
            'data': answers,
            'session_id': session_id
        })
    )


@pytest.mark.parametrize('answers', [
    [1],
    [1, 2, 3],
    [],
])
def test_phq_2_failure(answers, api):
    handler = FeedbackHandler(api)

    with pytest.raises(ValueError):
        handler.phq_2('session-123', answers)


@pytest.mark.parametrize('answers', [
    [1, 2, 3, 1, 2, 3, 1, 2],
    [1, 2, 3, 1, 2, 3, 1, 2, 3, 1],
    [],
])
def test_phq_9_failure(answers, api):
    handler = FeedbackHandler(api)

    with pytest.raises(ValueError):
        handler.phq_2('session-123', answers)