from __future__ import annotations
from datetime import datetime


class FeedbackScore:
    category: str
    label: str
    phq_2: str
    phq_9: str


class Prediction:
    session_id: str
    predicted_score: dict = {}
    feedback_score: FeedbackScore
    created_at: datetime
    updated_at: datetime
    is_calibrated: bool
    status: str

    def get_score(self, category: str) -> str | None:
        return self.predicted_score.get(category, None)

