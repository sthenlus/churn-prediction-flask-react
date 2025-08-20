import React, { useState } from 'react';
import './App.css';

function App() {
  // Form verilerini tutmak için state
  const [formData, setFormData] = useState({
    cart_abandon_rate: 0.5,
    ReturnRate: 0.1,
    RepeatPurchaseRate: 0.3,
    AvgBasketValue: 150,
    Last7DaysLogins: 5,
    SupportInteractions: 2,
    MonthlyPurchaseFreq: 1.5,
    BrandLoyaltyScore: 0.7,
    total_purchase_count: 10,
    avg_discount_percentage_used: 5,
  });

  // Tahmin sonucunu ve yüklenme durumunu tutmak için state
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Formdaki her değişiklikte state'i güncelle
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: parseFloat(value), // Gelen tüm değerleri sayıya çevir
    });
  };

  // Form gönderildiğinde backend'e istek at
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setPrediction(null);

    try {
      const response = await fetch('http://127.0.0.1:5000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('API isteği başarısız oldu veya model hatası.');
      }

      const result = await response.json();
      setPrediction(result);
    } catch (err) {
      setError('Tahmin alınırken bir hata oluştu. Backend sunucusunun çalıştığından emin olun.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Müşteri Churn Tahmin Prototipi</h1>
        <p>Müşteri verilerini girerek churn riskini tahmin edin.</p>
      </header>
      <main className="container">
        <form onSubmit={handleSubmit} className="churn-form">
          <div className="form-grid">
            {Object.keys(formData).map((key) => (
              <div className="form-group" key={key}>
                <label htmlFor={key}>{key.replace(/_/g, ' ')}</label>
                <input
                  type="number"
                  step="any"
                  id={key}
                  name={key}
                  value={formData[key]}
                  onChange={handleChange}
                  required
                />
              </div>
            ))}
          </div>
          <button type="submit" disabled={loading}>
            {loading ? 'Tahmin Ediliyor...' : 'Churn Riskini Tahmin Et'}
          </button>
        </form>

        {error && <div className="result-container error">{error}</div>}

        {prediction && (
          <div className={`result-container ${prediction.churn_prediction === 1 ? 'churn' : 'no-churn'}`}>
            <h2>Tahmin Sonucu</h2>
            <p className="prediction-text">
              Bu Müşterinin Churn Etme Olasılığı: <strong>{prediction.churn_probability}</strong>
            </p>
            <p className="prediction-label">
              {prediction.churn_prediction === 1 ? 'Riskli Müşteri (Churn)' : 'Sadık Müşteri (Churn Değil)'}
            </p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;