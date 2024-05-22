from flask import Flask, request, send_file, jsonify
from pydub import AudioSegment
import os

# install wrapper's package
from rnnoise_wrapper import RNNoise

app = Flask(__name__)
denoiser = RNNoise("./rnnoise_wrapper/libs/librnnoise_default.so.0.4.1")

def read_audio(file):
    # Parse the file format from the filename extension
    format = file.filename.rsplit('.', 1)[1].lower()

    # Use pydub to read various audio formats
    audio = AudioSegment.from_file(file, format=format)

    # Normalize the audio to the rnnoise's input format
    audio = audio.set_frame_rate(48000)
    audio = audio.set_sample_width(2)
    audio = audio.set_channels(1)

    return audio

@app.route('/denoise', methods=['POST'])
def denoise():
    global denoiser

    if 'file' not in request.files:
        return jsonify({"status": "File not found"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"status": "File name invalid"}), 404
    

    if file:
        try:
            audio = read_audio(file)
            denoised_audio = denoiser.filter(audio)
            denoiser.write_wav("denoised.wav", denoised_audio)
            return send_file("denoised.wav", as_attachment=True)
        except:
            return jsonify({"status": "An exception happend!"}), 500
    
    return jsonify({"status": "File invalid"}), 403

if __name__ == '__main__':
    port = int(os.getenv("APP_PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
