from dataclasses import dataclass
import requests
import json


class ResponseException(Exception):
    def __init__(self, response: requests.Response):
        self.code = response.status_code
        try:
            self.message = response.json().get('message')
        except ValueError:
            self.message = None


@dataclass
class Config:
    x_api_key: str
    url: str


class Api:
    def __init__(self, user_id: str, is_initiated: bool, config: Config, metadata: dict=None):
        self.user_id: str = user_id
        self.is_initiated: bool = is_initiated
        self.config:Config = config
        self.metadata: dict = metadata if metadata is not None else {}

    def get_common_headers(self):
        return {
            'accept': 'application/json',
            'X-API-Key': self.config.x_api_key,
        }

    def new_session_id(self) -> str:
        data = {
            'is_initiated': self.is_initiated,
            'metadata': self.metadata,
            'user_id': self.user_id,
        }
        response = requests.post(
            f'{self.config.url}/initiate',
            headers=self.get_common_headers(),
            data=json.dumps(data)
        )
        if response.status_code != 201:
            raise ResponseException(response)

        return response.json()['session_id']

    def prediction(self):
        return PredictionHandler(self)

    def feedback(self):
        return FeedbackHandler(self)


class PredictionHandler:

    def __init__(self, api: Api):
        self.api = api

    def predict(self, audio_file) -> str:
        response = requests.post(
            f'{self.api.config.url}/prediction/',
            headers=self.api.get_common_headers(),
            files={'file': audio_file},
            data={
                'session_id': self.api.new_session_id(),
            },
        )

        if response.status_code != 202:
            raise ResponseException(response)

        return response.json()['session_id']

    def get_prediction_by_session(self, session_id: str):
        response = requests.get(
            f'{self.api.config.url}/predict/sessions/{session_id}',
            headers=self.api.get_common_headers()
        )

        if response.status_code != 200:
            raise ResponseException(response)

        return response.json()

    def get_prediction_by_user(self, user_id: str):
        response = requests.get(
            f'{self.api.config.url}/predict/users/{user_id}',
            headers=self.api.get_common_headers()
        )

        if response.status_code != 200:
            raise ResponseException(response)

        return response.json()


class FeedbackHandler:
    def __init__(self, api: Api):
        self.api = api

    def _phq(self, session_id, answers) -> None:
        count = len(answers)

        if count not in (2, 9):
            raise ValueError(f'Answers count not in (2, 9): {count}.')

        data = {
            'data': answers,
            'session_id': session_id,
        }
        response = requests.patch(
            f'{self.api.config.url}/feedback/phq/{count}',
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
            f'{self.api.config.url}/feedback/depression/binary',
            headers=self.api.get_common_headers(),
            data=json.dumps(data)
        )

        if response.status_code != 200:
            raise ResponseException(response)

    def phq_2(self, session_id: str, answers: list) -> None:
        return self._phq(session_id, answers)

    def phq_9(self, session_id: str, answers: list) -> None:
        return self._phq(session_id, answers)