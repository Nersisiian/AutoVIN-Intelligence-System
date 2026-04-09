import joblib
import pandas as pd
from app.ml.dataset import extract_features


class VINSpecPredictor:
    def __init__(self, model_path: str = "app/ml/vin_model.pkl"):
        self.artifacts = joblib.load(model_path)
        self.models = self.artifacts['models']
        self.encoders = self.artifacts['encoders']
        self.feature_columns = self.artifacts['feature_columns']

    def predict(self, vin: str) -> dict:
        try:
            feat = extract_features(vin)
            feat_df = pd.DataFrame([feat])
            feat_encoded = pd.get_dummies(feat_df, columns=['wmi', 'vds', 'vis', 'manufacturer'])
            # Align with training columns
            feat_encoded = feat_encoded.reindex(columns=self.feature_columns, fill_value=0)
        except Exception as e:
            return {"error": f"Feature extraction failed: {str(e)}"}

        results = {}
        for target, model in self.models.items():
            pred_enc = model.predict(feat_encoded)[0]
            try:
                label = self.encoders[target].inverse_transform([pred_enc])[0]
            except ValueError:
                label = "Unknown"  # unseen label
            results[target] = label
        return results