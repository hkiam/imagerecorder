FROM python:3.11-alpine
WORKDIR /app

# Abhängigkeiten für Pillow installieren
RUN pip install --upgrade pip
RUN pip install --no-cache-dir pillow

# Abhängigkeiten für Flask installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY . .

# Flask-Umgebung variablen setzen
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Exponieren des Flask Ports
EXPOSE 5000

# Befehl zum Starten der Anwendung
CMD ["flask", "run", "--host=0.0.0.0"]