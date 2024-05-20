# Kintsugi Python SDK
Python SDK to access Kintsugi Voice API v2.

## Usage
```
import os
from src.kintsugi.api import Api


if __name__ == '__main__':
    # Configuration Parameters
    x_api_key = os.environ['X_API_KEY']
    user_id = os.environ['USER_ID']
    url = os.environ['URL']

    # Arguments
    audio_file_1 = open('/Users/jackson/Downloads/test_audio.wav', 'rb')
    audio_file_2 = open('/Users/jackson/Downloads/test_audio.wav', 'rb')
    allowed_sample_rate = 44100
    metadata = {
        'age': 39,
        'gender': 'male'
    }

    # API instantiation
    api = Api(x_api_key=x_api_key, url=url)

    # Prediction using all arguments
    api.prediction().predict(
        user_id,
        audio_file_1,
        metadata=metadata,
        allowed_sample_rate=allowed_sample_rate,
    )

    # Prediction using fewer arguments
    session_id = api.prediction().predict(user_id, audio_file_2)

    # Get prediction by session
    prediction_response = api.prediction().get_prediction_by_session(session_id)
    print(f'Score for depression: {prediction_response.get_score("depression")}')
    print(f'Score for anxiety: {prediction_response.get_score("anxiety")}')

    # Get predictions by user
    predictions_user = api.prediction().get_prediction_by_user(user_id)

    # Depression feedback
    api.feedback().depression(session_id, 'false')

    # PHQ2 feedback
    api.feedback().phq_2(session_id, [1, 2])

    # PHQ9 feedback
    api.feedback().phq_2(session_id, [1, 2, 1, 2, 1, 2, 3, 1, 2])
```