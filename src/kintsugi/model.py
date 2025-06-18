from __future__ import annotations
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional

class FeedbackScore:
    category: str
    label: str
    phq_2: str
    phq_9: str


@dataclass
class Prediction:
    session_id: str
    created_at: datetime
    updated_at: datetime
    is_calibrated: bool
    status: str
    feedback_score: Optional[FeedbackScore] = None
    predicted_score: dict = field(default_factory=dict)

    def get_score(self, category: str) -> str | None:
        return self.predicted_score.get(category, None)

