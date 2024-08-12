from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from PIL import Image
import os
from datetime import datetime, timedelta
import shutil

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'images'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

# Funktion, um den Ordnernamen basierend auf dem aktuellen Datum zu generieren
def get_image_folder(date=None):
    if date:
        return os.path.join(app.config['UPLOAD_FOLDER'], date)
    else:
        today = datetime.today().strftime('%Y-%m-%d')
        return os.path.join(app.config['UPLOAD_FOLDER'], today)

# Funktion, um die Bilder mit Datum und Uhrzeit in chronologischer Reihenfolge zu laden
def load_images(date=None):
    image_folder = get_image_folder(date)
    images = []

    if not os.path.exists(image_folder):
        return images, False  # Gibt eine leere Liste und einen False-Flag zurück
    
    for filename in os.listdir(image_folder):
        if filename.lower().endswith(".jpeg") or filename.lower().endswith(".jpg"):
            filepath = os.path.join(image_folder, filename)
            try:
                base_name = os.path.splitext(filename)[0]
                timestamp_str = base_name.split('_')[-2] +"_"+ base_name.split('_')[-1]
                timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S').timestamp()                
            except (IndexError, ValueError):
                print(f"Ungültiger Timestamp im Dateinamen: {filename}")
                timestamp = os.path.getmtime(filepath)
            
            images.append({
                'filename': filename,
                'datetime': datetime.fromtimestamp(timestamp),
                'highlight': 'Ding' in filename  # Überprüfen, ob "Ding" im Dateinamen ist
            })
    
    # Sortiere die Bilder nach dem Datum
    images.sort(key=lambda x: x['datetime'])
    return images, True  # Gibt die Bilderliste und einen True-Flag zurück

# Funktion zum Löschen alter Ordner
def delete_old_folders():
    cutoff_date = datetime.today() - timedelta(days=30)

    for folder_name in os.listdir(app.config['UPLOAD_FOLDER']):
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
        # Überprüfen, ob der Ordnername ein Datum ist und älter als 30 Tage ist
        try:
            folder_date = datetime.strptime(folder_name, '%Y-%m-%d')
            if folder_date < cutoff_date:
                shutil.rmtree(folder_path)
                print(f"Gelöschter Ordner: {folder_path}")
        except ValueError:
            # Wenn der Ordnername kein Datum ist, überspringen
            continue

# Funktion, um eine Liste aller verfügbaren Ordner (Tage) zu laden
def load_available_dates():
    dates = []
    for folder_name in os.listdir(app.config['UPLOAD_FOLDER']):
        try:
            # Überprüfen, ob der Ordnername ein gültiges Datum ist
            folder_date = datetime.strptime(folder_name, '%Y-%m-%d')
            dates.append(folder_name)
        except ValueError:
            continue
    dates.sort(reverse=True)  # Sortiere die Daten in absteigender Reihenfolge
    return dates

# Thumbnail-Größe definieren
THUMBNAIL_SIZE = (150, 150)

# Route für das Index
@app.route('/')
def index():
    date = request.args.get('date')  # Datum aus den Query-Parametern abrufen
    images, folder_exists = load_images(date)
    available_dates = load_available_dates()
    return render_template('index.html', images=images, folder_exists=folder_exists, available_dates=available_dates, selected_date=date)

# Route zum Abrufen der Thumbnails
@app.route('/thumbnail/<filename>')
def thumbnail(filename):
    date = request.args.get('date')
    image_folder = get_image_folder(date)
    img_path = os.path.join(image_folder, filename)
    img = Image.open(img_path)
    img.thumbnail(THUMBNAIL_SIZE)
    
    thumbnail_folder = os.path.join(image_folder, 'thumbnails')
    thumbnail_path = os.path.join(thumbnail_folder, filename)

    if not os.path.exists(thumbnail_folder):
        os.makedirs(thumbnail_folder)

    img.save(thumbnail_path)
    return send_from_directory(thumbnail_folder, filename)

# Route zum Abrufen des Bildes in voller Größe
@app.route('/image/<filename>')
def image(filename):
    date = request.args.get('date')
    image_folder = get_image_folder(date)
    return send_from_directory(image_folder, filename)

# Route zum Hochladen eines neuen Bildes
@app.route('/upload/<filename>', methods=['POST'])
def upload_image(filename):
    
    delete_old_folders()  # Überprüfen und löschen alter Ordner bei jedem Upload

    # Prüfen, ob die Datei im Request vorhanden ist
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Erstellen des Ordners für das aktuelle Datum, falls er nicht existiert
    image_folder = get_image_folder()
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)

    # Speichern der Datei mit Datum und Uhrzeit im Namen
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_extension = os.path.splitext(filename)[1]
    secure_filename = f"{os.path.splitext(filename)[0]}_{timestamp}{file_extension}"
    filepath = os.path.join(image_folder, secure_filename)

    file.save(filepath)

    return jsonify({"message": "File uploaded successfully", "filename": secure_filename}), 200

if __name__ == '__main__':
    app.run(debug=True)
