export type TrackName = "kick" | "snare" | "hihat";

const API_BASE = "http://127.0.0.1:5000";

export async function hitTrack(track: TrackName): Promise<void> {
  await fetch(`${API_BASE}/hit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ track }),
  });
}


export async function stopAll(): Promise<void> {
  await fetch(`${API_BASE}/stop_all`, {
    method: "POST",
  });
}