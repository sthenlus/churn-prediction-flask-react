# Python'un hafif bir versiyonunu temel al
FROM python:3.9-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Önce gereksinimleri kopyala ve yükle (bu, katman önbelleklemesini optimize eder)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projenin geri kalanını kopyala
COPY . .

# Flask uygulamasının çalışacağı portu belirt
EXPOSE 5000

# Konteyner çalıştığında uygulamayı başlatacak komut
CMD ["python", "app.py"]