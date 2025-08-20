from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib

# Flask uygulamasını başlat
app = Flask(__name__)
# React'tan gelen isteklere izin vermek için CORS'u etkinleştir
CORS(app)

# Modeli ve ölçekleyiciyi yükle
try:
    model = joblib.load("./models/LogReg_Heavy_modell.pkl")
    scaler = joblib.load("./models/LogReg_Heavy_scalerr.pkl")
    print("Model ve ölçekleyici başarıyla yüklendi.")
except Exception as e:
    print(f"Model yüklenirken hata oluştu: {e}")
    model = None
    scaler = None

# Modelin eğitildiği sütunların listesi (scaler'dan alınıyor)
# Bu sıralama, modelin doğru tahmin yapması için hayati önem taşır.
MODEL_FEATURES = [
    'cart_abandon_rate', 'ReturnRate', 'RepeatPurchaseRate', 'AvgBasketValue',
    'Last7DaysLogins', 'SupportInteractions', 'MonthlyPurchaseFreq',
    'BrandLoyaltyScore', 'total_purchase_count', 'avg_discount_percentage_used'
]

@app.route('/predict', methods=['POST'])
def predict():
    if not model or not scaler:
        return jsonify({"error": "Model veya ölçekleyici yüklenemedi, sunucu loglarını kontrol edin."}), 500

    try:
        # Gelen JSON verisini al
        data = request.get_json()
        
        # Gelen veriyi bir Pandas DataFrame'e çevir
        input_df = pd.DataFrame([data])
        
        # Modelin beklediği özelliklerin veri içinde olduğundan emin ol
        for col in MODEL_FEATURES:
            if col not in input_df.columns:
                return jsonify({"error": f"Eksik özellik: '{col}'"}), 400

        # Veriyi modelin eğitildiği sıraya göre düzenle
        input_df = input_df[MODEL_FEATURES]

        # Sayısal verileri ölçeklendir
        input_scaled = scaler.transform(input_df)

        # Tahmin yap
        prediction = model.predict(input_scaled)
        probability = model.predict_proba(input_scaled)

        # Churn olma olasılığını al (% olarak)
        churn_probability = probability[0][1] * 100

        # Sonucu JSON formatında geri döndür
        return jsonify({
            'churn_prediction': int(prediction[0]), # 0: Kalır, 1: Gider
            'churn_probability': f"{churn_probability:.2f}%"
        })

    except Exception as e:
        return jsonify({"error": f"Tahmin sırasında bir hata oluştu: {str(e)}"}), 500

if __name__ == '__main__':
    # Sunucuyu başlat (debug=True geliştirme aşaması için)
    app.run(port=5000, debug=True)