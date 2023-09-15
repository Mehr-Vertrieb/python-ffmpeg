from flask import Flask, request, jsonify
import os
import subprocess

app = Flask(__name__)

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

# Endpunkt zum Hochladen und Aufteilen der MP3-Datei
@app.route('/upload', methods=['POST'])
def upload_and_split():
    try:
        # Überprüfen, ob eine Datei im Anfrageformular enthalten ist
        if 'file' not in request.files:
            return jsonify({"error": "No file part"})

        file = request.files['file']

        # Überprüfen, ob die Datei ein MP3-Audioformat ist
        if file.filename == '' or not file.filename.endswith('.mp3'):
            return jsonify({"error": "Invalid file format"})

        # Speichern Sie die hochgeladene Datei vorübergehend
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        input_file = os.path.join(upload_dir, file.filename)
        file.save(input_file)

        # Aufteilen der MP3-Datei
        max_size = 15 * 1024 * 1024  # Maximale Dateigröße in Byte (15 MB)
        output_files = split_mp3(input_file, "output", max_size)

        # Rückgabe der aufgeteilten Dateien
        return jsonify({"message": "File split successfully", "parts": output_files})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
