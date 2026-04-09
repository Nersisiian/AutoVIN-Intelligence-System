import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from app.ml.dataset import load_training_data

def train_and_save():
    X, y_trim, y_engine, y_trans, y_class = load_training_data()
    # One-hot encode categorical features
    X_encoded = pd.get_dummies(X, columns=['wmi', 'vds', 'vis', 'manufacturer'])
    
    encoders = {}
    models = {}
    for target_name, y in zip(['trim', 'engine', 'transmission', 'vehicle_class'],
                              [y_trim, y_engine, y_trans, y_class]):
        le = LabelEncoder()
        y_enc = le.fit_transform(y)
        encoders[target_name] = le
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_encoded, y_enc)
        models[target_name] = model
    
    # Save model, encoders, and feature columns
    joblib.dump({
        'models': models,
        'encoders': encoders,
        'feature_columns': X_encoded.columns.tolist()
    }, 'app/ml/vin_model.pkl')
    print("Model saved to app/ml/vin_model.pkl")

if __name__ == "__main__":
    train_and_save()