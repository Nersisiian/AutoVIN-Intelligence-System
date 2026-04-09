from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


@dataclass(frozen=True)
class AiEstimatedSpecs:
    make: str | None
    model: str | None
    trim: str | None
    engine: str | None
    transmission: str | None
    safety_features: list[str]
    confidence: float


class AiSpecEstimator:
    """
    Lightweight, self-contained estimator trained on a small embedded dataset.
    It is meant as a fallback when the VIN can't be decoded reliably.
    """

    def __init__(self) -> None:
        # Tiny dataset: (wmi_prefix2, year_bucket, make, model, engine, transmission)
        data = [
            ("1H", "2015+", "Honda", "Civic", "2.0L I4", "CVT"),
            ("1H", "2010-2014", "Honda", "Accord", "2.4L I4", "Automatic"),
            ("JT", "2015+", "Toyota", "Corolla", "1.8L I4", "CVT"),
            ("JT", "2010-2014", "Toyota", "Camry", "2.5L I4", "Automatic"),
            ("1F", "2015+", "Ford", "F-150", "3.5L V6", "Automatic"),
            ("1F", "2010-2014", "Ford", "Fusion", "2.5L I4", "Automatic"),
            ("WBA", "2015+", "BMW", "3 Series", "2.0L Turbo I4", "Automatic"),
            ("WDB", "2015+", "Mercedes-Benz", "C-Class", "2.0L Turbo I4", "Automatic"),
            ("KM", "2015+", "Hyundai", "Elantra", "2.0L I4", "Automatic"),
            ("KN", "2015+", "Kia", "Sportage", "2.4L I4", "Automatic"),
            ("JN", "2015+", "Nissan", "Altima", "2.5L I4", "CVT"),
        ]

        X = [{"wmi": wmi, "year_bucket": yb} for (wmi, yb, *_rest) in data]
        y_make = [make for (_wmi, _yb, make, _model, _engine, _tx) in data]
        y_model = [model for (_wmi, _yb, _make, model, _engine, _tx) in data]
        y_engine = [engine for (_wmi, _yb, _make, _model, engine, _tx) in data]
        y_tx = [tx for (_wmi, _yb, _make, _model, _engine, tx) in data]

        pre = DictVectorizer(sparse=True)

        def clf() -> LogisticRegression:
            return LogisticRegression(max_iter=500, n_jobs=1)

        self._make_model: Pipeline = Pipeline([("pre", pre), ("clf", clf())]).fit(X, y_make)
        self._model_model: Pipeline = Pipeline([("pre", pre), ("clf", clf())]).fit(X, y_model)
        self._engine_model: Pipeline = Pipeline([("pre", pre), ("clf", clf())]).fit(X, y_engine)
        self._tx_model: Pipeline = Pipeline([("pre", pre), ("clf", clf())]).fit(X, y_tx)

    @staticmethod
    def _bucket_year(year: int | None) -> str:
        if year is None:
            return "unknown"
        if year >= 2015:
            return "2015+"
        if 2010 <= year <= 2014:
            return "2010-2014"
        return "pre-2010"

    def estimate(self, wmi: str, year: int | None) -> AiEstimatedSpecs:
        x = [{"wmi": wmi[:3] if len(wmi) >= 3 else wmi[:2], "year_bucket": self._bucket_year(year)}]

        make = str(self._make_model.predict(x)[0])
        model = str(self._model_model.predict(x)[0])
        engine = str(self._engine_model.predict(x)[0])
        tx = str(self._tx_model.predict(x)[0])

        # crude confidence from max class probability across models
        probs = []
        for m in (self._make_model, self._model_model, self._engine_model, self._tx_model):
            if hasattr(m, "predict_proba"):
                p = m.predict_proba(x)[0]
                probs.append(float(np.max(p)))
        confidence = float(np.mean(probs)) if probs else 0.55

        safety_features = ["ABS", "ESC", "Airbags (Front)"]
        return AiEstimatedSpecs(
            make=make,
            model=model,
            trim="Estimated",
            engine=engine,
            transmission=tx,
            safety_features=safety_features,
            confidence=max(0.4, min(0.85, confidence)),
        )


ai_estimator = AiSpecEstimator()
