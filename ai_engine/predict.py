import os
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "encoders.pkl")

model = joblib.load(MODEL_PATH)
label_encoders = joblib.load(ENCODER_PATH)


def predict_maintenance(input_data: dict):
    df = pd.DataFrame([input_data])

    for column, encoder in label_encoders.items():
        if column in df.columns:
            value = str(df.at[0, column])
            known = set(encoder.classes_)

            if value not in known:
                value = encoder.classes_[0]

            df[column] = encoder.transform([value])

    prediction = model.predict(df)[0]

    if hasattr(model, "predict_proba"):
        probability = model.predict_proba(df)[0][1]
    else:
        probability = 0.0

    return {
        "prediction": int(prediction),
        "risk_score": round(float(probability) * 100, 2)
    }