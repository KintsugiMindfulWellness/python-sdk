import pytest
from unittest.mock import patch, MagicMock
from src.kintsugi.api import Api, Config, ResponseException

mock_config = Config(
    x_api_key='x-api-key-for-tests',
    url='https://tests.kintsugihealth.com'
)


def test_api_initialization():
    api = Api('test_user', True, mock_config)
    assert api.user_id == 'test_user'
    assert api.is_initiated is True
    assert api.config == mock_config
    assert api.metadata == {}


def test_get_common_headers():
    api = Api('test_user', True, mock_config)
    expected_headers = {
        'accept': 'application/json',
        'X-API-Key': mock_config.x_api_key,
    }
    assert api.get_common_headers() == expected_headers


@patch('requests.post')
def test_new_session_id(mock_post):
    api = Api('test_user', True, mock_config)
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"session_id": "test_session_id"}
    mock_post.return_value = mock_response

    assert api.new_session_id() == "test_session_id"


@patch('requests.post')
def test_new_session_id_failure(mock_post):
    api = Api('test_user', True, mock_config)
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_post.return_value = mock_response

    with pytest.raises(ResponseException):
        api.new_session_id()