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

    def predictions(self):
        return PredictionsHandler(self)

    def feedback(self):
        return FeedbackHandler(self)


class PredictionsHandler:

    def __init__(self, api: Api):
        self.api = api

    def predict(self, audio_file) -> str:
        response = requests.post(
            f'{self.api.config.url}/predict/depression/severity',
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

    def anxiety(self):
        pass

    def depression(self):
        pass

    def phq_2(self):
        pass

    def phq_9(self):
        pass