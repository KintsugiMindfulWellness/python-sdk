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
        output = Prediction()

        output.session_id = data['session_id']
        output.created_at = data['created_at']
        output.updated_at = data['updated_at']
        output.is_calibrated = data['is_calibrated']
        output.status = data['status']

        if 'predicted_score' in data:
            predicted_data_raw = data['predicted_score']
            predicted_data = predicted_data_raw

            if isinstance(predicted_data_raw, str):
                predicted_data = {data['model_category']: predicted_data_raw}

            output.predicted_score = predicted_data

        if 'actual_score' in data:
            output.feedback_score = FeedbackScoreParser().parse(data['actual_score'])

        return output
