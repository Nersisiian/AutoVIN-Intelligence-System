from app.ml.predict import VINSpecPredictor

_predictor = None

def get_predictor():
    global _predictor
    if _predictor is None:
        _predictor = VINSpecPredictor()
    return _predictor

def predict_vin_specs(vin: str):
    return get_predictor().predict(vin)