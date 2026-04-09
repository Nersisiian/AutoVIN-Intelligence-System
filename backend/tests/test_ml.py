from app.ml.predict import VINSpecPredictor

def test_ml_prediction():
    pred = VINSpecPredictor()
    result = pred.predict("1HGCM82633A123456")
    assert 'trim' in result
    assert 'engine' in result
    assert 'transmission' in result