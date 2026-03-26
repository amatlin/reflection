# Funhouse

## The idea

Reflection expands from a single website mirror into a funhouse of technological mirrors. Each mirror shows visitors how their behavior is tracked and analyzed in a different modality. The visitor walks through them sequentially and by the end has a composite picture of how much of their behavior is legible to machines.

## Why

The website mirror alone is clever but familiar — people vaguely know sites track clicks. A single video mirror would be more striking but it's still one trick, and camera-based surveillance installations have been done before. What hasn't been done is showing visitors the **analytics infrastructure** behind the surveillance — not just "we recorded you" but "here's the data warehouse, here's the pipeline, here's the SQL query, here's the daily aggregate you became part of." The funhouse extends that approach across modalities, making a statement about the universality of surveillance rather than demonstrating a single instance of it.

## The mirrors

Each mirror isolates a modality and shows visitors what's being extracted from that specific signal — especially the things they didn't know they were transmitting.

### 1. Web (actions)
Tracks clicks, navigation, behavioral events. The current Reflection website. People know sites track what they click; the mirror shows them the infrastructure behind it — the event stream, the warehouse, the pipeline, the analytics.

Already built.

### 2. Video (body)
Webcam-based. Tracks facial expressions, gestures, attention. People encounter cameras constantly but have no idea what's being extracted — not just "you were recorded" but "you smiled at 0:14, looked away at 0:22, your engagement dropped here." The gap between what people think cameras see and what they actually see.

### 3. Voice (speech)
Microphone-based. A single input (your voice) splits into two streams of analysis: the **content** (what you said, transcribed) and the **signal** (how you said it — pitch, pace, volume, emotion, hesitation). You say "I'm fine" and the mirror shows you the words *and* that your pitch dropped, your pace slowed, and the system tagged it as low-confidence negative sentiment.

## The arc

The mirrors escalate in intimacy:
1. **Actions** — the most external. Things you chose to do.
2. **Body** — less conscious. Expressions and attention you didn't deliberately perform.
3. **Voice** — the most personal. Literally coming from inside you, with emotional signatures you didn't intend to communicate.

The separation is pedagogical. If you hit someone with all three at once, they don't learn what each mirror is extracting — it blurs into a general feeling of unease. Isolating them gives each modality its own moment of recognition.

## The finale

After experiencing each mirror individually, the visitor sees a composite view where all three run simultaneously. This is the punchline: you've seen each one in isolation, and now you see what it looks like when they're all on at the same time — which is your actual life. Your phone is simultaneously tracking what you tap, seeing your face, and listening to your voice. The sequential reveal is what makes the coming-together meaningful.

## The architectural punchline

The mirrors look different on the surface but the apparatus behind them is identical. Events in, pipeline transforms, warehouse, dashboards out. The modality changes; the infrastructure doesn't. All three feed into the same BigQuery warehouse, the same dbt pipeline, the same analytics layer. This is the thing that makes the funhouse novel — not just "you're being watched in many ways" but "it's all the same machine."

## Grant angle

The website is mirror one — it's working and deployed at reflection.sh. The funhouse is the vision. The grant funds mirrors two and three. The project is modular: each mirror is a self-contained piece that adds to the whole without depending on the others being finished.

## Open questions

- Physical installation vs. browser-based vs. hybrid?
- Does this reframe the whole project identity or sit alongside the current site?
- What's the visitor journey in a physical space? Rooms? Stations?
- How does the composite finale actually work — split screen? Single screen with layers?
- Are there other mirrors worth considering? (Gaze tracking, keystroke dynamics, Wi-Fi presence)
- Voice-as-control was considered (speak to navigate the website, enabling a purely physical installation) but rejected — using voice as a command channel isn't a mirror, it doesn't reveal what voice surveillance extracts.
