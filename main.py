from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import subprocess

app = Flask(__name__)

# Ordner, in dem die hochgeladenen MP3-Dateien und die gesplitteten Dateien gespeichert werden
UPLOAD_FOLDER = '/var/lib/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
            split_result = split_mp3(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'output', 15)

            # Nach dem erfolgreichen Split löschen Sie die ursprüngliche Datei
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            if isinstance(split_result, list):
                return jsonify({'success': 'Datei erfolgreich hochgeladen und gesplittet', 'output_files': split_result}), 200
            else:
                return jsonify({'error': 'Split fehlgeschlagen', 'details': split_result}), 500
        else:
            return jsonify({'error': 'Ungültige Dateiendung'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Funktion zum Aufteilen der MP3-Dateien
def split_mp3(input_file, output_directory, max_size):
    try:
        # Überprüfen, ob das Ausgabeverzeichnis existiert, andernfalls erstellen
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Berechnen Sie die Anzahl der Teile basierend auf der maximalen Größe
        part_number = 1
        output_files = []

        while True:
            # Definieren Sie den Ausgabedateinamen für das aktuelle Teil
            output_file = os.path.join(output_directory, f"part_{part_number}.mp3")

            # Teilen Sie die MP3-Datei mit FFmpeg
            command = [
                "ffmpeg",
                "-i", input_file,
                "-ss", str((part_number - 1) * max_size),
                "-t", str(max_size),
                "-c:a", "copy",
                output_file
            ]

            subprocess.run(command, check=True)

            # Überprüfen Sie, ob das aktuelle Teil erstellt wurde
            if os.path.exists(output_file):
                output_files.append(output_file)
                part_number += 1
            else:
                break

        return output_files
    except Exception as e:
        return str(e)

# Erlaubte Dateiendungen für den Upload
ALLOWED_EXTENSIONS = {'mp3'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
