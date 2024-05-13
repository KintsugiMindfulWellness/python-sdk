from dataclasses import dataclass
import requests
import json


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

    def new_session_id(self) -> str:
        headers = {
            'accept': 'application/json',
            'X-API-Key': self.config.x_api_key,
            'Content-Type': 'application/json',
        }
        data = {
            'is_initiated': self.is_initiated,
            'metadata': self.metadata,
            'user_id': self.user_id,
        }
        response = requests.post(
            f'{self.config.url}/initiate',
            headers=headers,
            data=json.dumps(data)
        )
        if response.status_code == 201:
            return response.json()['session_id']
        else:
            return response.json()['message']

    def predictions(self):
        return PredictionsHandler(self)

    def feedback(self):
        return FeedbackHandler(self)


class PredictionsHandler:

    def __init__(self, api: Api):
        self.api = api

    def predict_depression_severity(self) -> str:
        session_id = self.api.new_session_id()
        # Invoke endpoint
        return session_id

    def get_prediction_by_session(self, session_id: str):
        # Invoke endpoint
        pass

    def get_prediction_by_user(self, user_id: str):
        # Invoke endpoint
        pass


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