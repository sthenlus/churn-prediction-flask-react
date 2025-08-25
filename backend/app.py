from flask import Flask, request, jsonify
from flask_cors import CORS
from celery.result import AsyncResult
from tasks import run_batch_prediction
from celery_config import celery_app

app = Flask(__name__)
CORS(app)


@app.route('/predict', methods=['POST'])
def start_prediction_task():
    """Dosyayı al, tahmin görevini başlat ve görev ID'sini döndür."""
    if 'file' not in request.files:
        return jsonify({"error": "İstekte dosya bulunamadı."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Dosya seçilmedi."}), 400

    try:
        json_data_string = file.read().decode('utf-8')
        task = run_batch_prediction.delay(json_data_string)
        return jsonify({"task_id": task.id}), 202
    except Exception as e:
        return jsonify({"error": f"Görev başlatılırken hata: {str(e)}"}), 500


@app.route('/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Verilen görev ID'sinin durumunu ve sonucunu kontrol et."""
    task_result = AsyncResult(task_id, app=celery_app)

    if task_result.successful():
        response = {"state": task_result.state, "result": task_result.result}
    elif task_result.state == 'FAILURE':
        response = {"state": task_result.state, "error": str(task_result.info)}
    else:
        response = {"state": task_result.state}
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)