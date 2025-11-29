# Drum Mixer

A minimal drum sequencer built with a React frontend and a Flask backend. React handles the 16-step pattern UI and timing, while Flask uses `pygame.mixer` to play MP3/WAV drum samples locally.

## Features

- 16-step sequencer (kick, snare, hi-hat)
- React controls timing and step activation
- Flask receives hit events and triggers pygame audio playback
- Supports MP3 and WAV samples
- Stop button immediately stops all playing sounds

## Project Structure

- frontend/ — React + Vite + TypeScript
- backend/ — Flask API with pygame sound engine
- backend/static/audio/ — Drum sample files
