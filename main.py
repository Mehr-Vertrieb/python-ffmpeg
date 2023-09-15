import os
import subprocess
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Ordner, in dem die hochgeladenen MP3-Dateien und die gesplitteten Dateien gespeichert werden
UPLOAD_FOLDER = '/var/lib/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Funktion zum Überprüfen der Dateierweiterung
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'mp3'

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Überprüfen, ob die POST-Anfrage eine Datei enthält
        if 'file' not in request.files:
            return jsonify({'error': 'Keine Datei hochgeladen'}), 400

        file = request.files['file']

        # Überprüfen, ob die Datei eine MP3-Datei ist
        if file.filename == '':
            return jsonify({'error': 'Keine ausgewählte Datei'}), 400

        if file and allowed_file(file.filename):
            # Speichern der hochgeladenen Datei
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Hier Split-Code einfügen (Verwendung von ffmpeg oder ähnlichem)
            # ...

            # Nach dem erfolgreichen Split löschen Sie die ursprüngliche Datei
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return jsonify({'success': 'Datei erfolgreich hochgeladen und gesplittet'}), 200
        else:
            return jsonify({'error': 'Ungültige Dateiendung'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
