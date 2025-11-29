import { useEffect, useState } from "react";
import "./App.css";
import { stopAll, hitTrack, type TrackName } from "./api";

const tracks: TrackName[] = ["kick", "snare", "hihat"];
const STEPS = 16;
const TEMPO = 120; // BPM

type Pattern = Record<TrackName, boolean[]>;

function createEmptyPattern(): Pattern {
  return {
    kick: Array(STEPS).fill(false),
    snare: Array(STEPS).fill(false),
    hihat: Array(STEPS).fill(false),
  };
}

function App() {
  const [pattern, setPattern] = useState<Pattern>(createEmptyPattern);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  const toggleStep = (track: TrackName, index: number) => {
    setPattern((prev) => ({
      ...prev,
      [track]: prev[track].map((v, i) => (i === index ? !v : v)),
    }));
  };

  // Sequencer loop: browser timing → calls backend /hit
  useEffect(() => {
    if (!isPlaying) return;

    const stepDurationMs = (60 / TEMPO / 4) * 1000; // 16th notes

    const intervalId = window.setInterval(() => {
      setCurrentStep((prev) => {
        const stepToTrigger = prev;

        // Trigger all active tracks at this step
        tracks.forEach((track) => {
          if (pattern[track][stepToTrigger]) {
            hitTrack(track).catch((err) => console.error("Hit failed:", err));
          }
        });

        return (prev + 1) % STEPS;
      });
    }, stepDurationMs);

    return () => window.clearInterval(intervalId);
  }, [isPlaying, pattern]);

  return (
    <div className="App">
      <h1>pygame Drum Mixer</h1>

      <div className="controls">
        {!isPlaying ? (
          <button onClick={() => setIsPlaying(true)}>▶ Play</button>
        ) : (
          <button
            onClick={() => {
              setIsPlaying(false);
              setCurrentStep(0);
              stopAll(); // NEW: tell pygame to stop all sounds
            }}
          >
            ⏹ Stop
          </button>
        )}
      </div>

      <div className="tracks">
        {tracks.map((track) => (
          <div key={track} className="track">
            <h3>{track.toUpperCase()}</h3>
            <div className="grid">
              {pattern[track].map((active, i) => {
                const isCurrent = i === currentStep && isPlaying;
                return (
                  <div
                    key={i}
                    className={`step ${active ? "active" : ""} ${
                      isCurrent ? "current" : ""
                    }`}
                    onClick={() => toggleStep(track, i)}
                  >
                    {i + 1}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
