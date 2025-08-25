import pandas as pd
import joblib
import io
from celery_config import celery_app

# Modelin eğitildiği sütunların listesi
MODEL_FEATURES = [
    'cart_abandon_rate', 'ReturnRate', 'RepeatPurchaseRate', 'AvgBasketValue',
    'Last7DaysLogins', 'SupportInteractions', 'MonthlyPurchaseFreq',
    'BrandLoyaltyScore', 'total_purchase_count', 'avg_discount_percentage_used'
]

# Modeli ve ölçekleyiciyi bir kere yükle
try:
    model = joblib.load("./models/LogReg_Heavy_modell.pkl")
    scaler = joblib.load("./models/LogReg_Heavy_scalerr.pkl")
    print("Celery Worker: Model ve ölçekleyici yüklendi.")
except Exception as e:
    model = None
    scaler = None
    print(f"Celery Worker: Model yüklenirken hata oluştu: {e}")


@celery_app.task(bind=True)
def run_batch_prediction(self, json_data_string):
    """Arka planda çalışacak olan asenkron tahmin görevi."""
    if not model or not scaler:
        raise Exception("Model veya ölçekleyici yüklenemedi.")

    try:
        input_df = pd.read_json(io.StringIO(json_data_string))
        original_data = input_df.copy()

        for col in MODEL_FEATURES:
            if col not in input_df.columns:
                raise ValueError(f"JSON dosyasında eksik özellik: '{col}'")

        input_df_features = input_df[MODEL_FEATURES]
        input_scaled = scaler.transform(input_df_features)

        predictions = model.predict(input_scaled)
        probabilities = model.predict_proba(input_scaled)

        original_data['churn_prediction'] = predictions
        original_data['churn_probability'] = [f"{p[1] * 100:.2f}%" for p in probabilities]

        return original_data.to_dict(orient='records')

    except Exception as e:
        self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        raise