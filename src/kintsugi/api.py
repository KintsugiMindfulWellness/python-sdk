import requests
import json
from kintsugi.parsers import PredictionParser


DEFAULT_URL = 'https://api.kintsugihealth.com/v2'


class ResponseException(Exception):
    def __init__(self, response: requests.Response):
        self.code = response.status_code
        try:
            self.message = response.json().get('message')
        except ValueError:
            self.message = None


class Api:
    def __init__(self, x_api_key: str, url: str = DEFAULT_URL):
        self.x_api_key = x_api_key
        self.url: str = url

    def get_common_headers(self):
        return {
            'accept': 'application/json',
            'X-API-Key': self.x_api_key,
        }

    def new_session_id(self, user_id: str, metadata: dict = None) -> str:
        data = {
            'is_initiated': True,
            'user_id': user_id,
        }

        if metadata:
            data['metadata'] = metadata

        response = requests.post(
            f'{self.url}/initiate',
            headers=self.get_common_headers(),
            data=json.dumps(data)
        )
        if response.status_code != 201:
            raise ResponseException(response)

        return response.json()['session_id']

    def prediction(self) -> 'PredictionHandler':
        return PredictionHandler(self)

    def feedback(self) -> 'FeedbackHandler':
        return FeedbackHandler(self)


class PredictionHandler:

    def __init__(self, api: Api):
        self.api = api

    def predict(self, user_id: str, audio_file, metadata:dict = None, allowed_sample_rate: int = None) -> str:
        data = {
            'session_id': self.api.new_session_id(user_id, metadata),
        }

        if allowed_sample_rate:
            data['allowed_sample_rate'] = allowed_sample_rate

        response = requests.post(
            f'{self.api.url}/prediction/',
            headers=self.api.get_common_headers(),
            files={'file': audio_file},
            data=data,
        )

        if response.status_code != 202:
            raise ResponseException(response)

        return response.json()['session_id']

    def get_prediction_by_session(self, session_id: str):
        response = requests.get(
            f'{self.api.url}/predict/sessions/{session_id}',
            headers=self.api.get_common_headers()
        )

        if response.status_code != 200:
            raise ResponseException(response)

        data = response.json()
        data['session_id'] = session_id
        return PredictionParser().parse(data)

    def get_prediction_by_user(self, user_id: str):
        response = requests.get(
            f'{self.api.url}/predict/users/{user_id}',
            headers=self.api.get_common_headers()
        )

        if response.status_code != 200:
            raise ResponseException(response)

        parser = PredictionParser()
        list_data = response.json()
        return [parser.parse(data) for data in list_data]


class FeedbackHandler:
    def __init__(self, api: Api):
        self.api = api

    def _send_answers(self, path, session_id, answers, expected_count) -> None:
        count = len(answers)

        if count != expected_count:
            raise ValueError(f'Answers count is not what is expected: {expected_count}.')

        data = {
            'data': answers,
            'session_id': session_id,
        }
        response = requests.patch(
            f'{self.api.url}/feedback/{path}/{count}',
            headers=self.api.get_common_headers(),
            data=json.dumps(data)
        )

        if response.status_code != 200:
            raise ResponseException(response)

    def depression(self, session_id: str, data: str):
        if data not in ('false', 'true', 'additional_consideration_required'):
            raise ValueError(f'Param data not in ("false", "true", "additional_consideration_required"): {data}.')

        data = {
            'data': data,
            'session_id': session_id,
        }
        response = requests.patch(
            f'{self.api.url}/feedback/depression/binary',
            headers=self.api.get_common_headers(),
            data=json.dumps(data)
        )

        if response.status_code != 200:
            raise ResponseException(response)

    def phq_2(self, session_id: str, answers: list) -> None:
        return self._send_answers('phq', session_id, answers, 2)

    def phq_9(self, session_id: str, answers: list) -> None:
        return self._send_answers('phq', session_id, answers, 9)

    def gad_7(self, session_id: str, answers: list) -> None:
        return self._send_answers('gad', session_id, answers, 7)