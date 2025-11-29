from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pygame

app = Flask(__name__)
CORS(app)

# ---------- pygame.mixer INIT ----------
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Folder where your mp3 files live
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "static", "audio")

# Map logical track names -> actual file names
SOUNDS = {
    # main kick used by React's "kick"
    "kick": pygame.mixer.Sound(os.path.join(AUDIO_DIR, "kick-hardstyle.mp3")),

    # you can use these later if you add more tracks in React
    "kick2": pygame.mixer.Sound(os.path.join(AUDIO_DIR, "kick-hardstyle-2.mp3")),
    "kick3": pygame.mixer.Sound(os.path.join(AUDIO_DIR, "wiese-kick.mp3")),

    "snare": pygame.mixer.Sound(os.path.join(AUDIO_DIR, "snare.mp3")),

    # your file is called thihat.mp3, we map it to logical name "hihat"
    "hihat": pygame.mixer.Sound(os.path.join(AUDIO_DIR, "thihat.mp3")),
}


@app.route("/")
def home():
    return {"status": "Drum Mixer API running with pygame.mixer"}


@app.route("/hit", methods=["POST"])
def hit():
    """
    Body: { "track": "kick" | "snare" | "hihat" | "kick2" | "kick3" }
    Plays that sound using pygame.mixer on the server machine.
    """
    data = request.json or {}
    track = data.get("track")

    if track not in SOUNDS:
        return jsonify({"error": f"Unknown track '{track}'"}), 400

    SOUNDS[track].play()
    return jsonify({"status": "ok", "track": track})


@app.route("/stop_all", methods=["POST"])
def stop_all():
    pygame.mixer.stop()   # Stops ALL playing channels
    return jsonify({"status": "stopped"})


@app.route("/save_preset", methods=["POST"])
def save_preset():
    # stub for now
    data = request.json or {}
    print("Preset received:", data)
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)
