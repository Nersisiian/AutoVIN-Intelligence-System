# /app/ml/model.py
from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier

MODEL_PATH = Path(__file__).parent / "vin_model.pkl"

class VINModel:
    def __init__(self):
        self.model = None

    def train(self, X, y):
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            random_state=42
        )
        self.model.fit(X, y)
        joblib.dump(self.model, MODEL_PATH)

    def load(self):
        if MODEL_PATH.exists():
            self.model = joblib.load(MODEL_PATH)
        else:
            raise FileNotFoundError("Model not trained yet")

    def predict(self, X):
        if self.model is None:
            self.load()
        return self.model.predict(X)