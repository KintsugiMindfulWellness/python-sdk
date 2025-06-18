from kintsugi.model import Prediction, FeedbackScore


class FeedbackScoreParser:
     def parse(self, data: dict) -> FeedbackScore:
         feedback = FeedbackScore()

         category_label = [
             (key, value) for key, value in data.items()
             if key not in ['phq_2', 'phq_9']
         ]
         if category_label:
             feedback.category = category_label[0][0]
             feedback.label = category_label[0][1]

         feedback.phq_2 = data.get('phq_2', [])
         feedback.phq_9 = data.get('phq_9', [])

         return feedback


class PredictionParser:
    def parse(self, data: dict) -> Prediction:
        output = Prediction(
            session_id=data['session_id'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            is_calibrated=data['is_calibrated'],
            status=data['status'],
        )


        if output.status != 'processing':
            categories = data['model_category'].split(',')

            for category in categories:
                if 'predicted_score_' + category in data:
                    output.predicted_score[category] = data['predicted_score_' + category]

        if 'actual_score' in data:
            output.feedback_score = FeedbackScoreParser().parse(data['actual_score'])

        return output
