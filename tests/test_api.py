import pytest
from requests.models import Response
from unittest.mock import patch, MagicMock
from src.kintsugi.api import Api, Config, PredictionHandler, ResponseException


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