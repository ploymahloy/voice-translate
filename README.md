# voice-translate

Upload a source audio file and receive translated speech in a voice cloned from that recording.

Supported target languages: `en`, `es`, `fr`, `de`.

Supported input formats: `.wav`, `.mp3`.

## Prerequisites

- Python 3.11+
- An [ElevenLabs](https://elevenlabs.io/) API key with voice cloning, dubbing, and speech-to-speech access

## Setup

```bash
make deps
cp .env.example .env
# Edit .env and set ELEVENV3_API_KEY to your real key
```

## Run

```bash
make run
```

Or:

```bash
export ELEVENV3_API_KEY=your-elevenlabs-api-key-here
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive API.

## Translate audio

```bash
curl -X POST http://localhost:8000/translate \
  -F target_language=es \
  -F source_audio=@path/to/recording.wav \
  --output translated.mp3
```

## Tests

```bash
make test
```

Integration tests call the live ElevenLabs API and require a valid key:

```bash
export ELEVENV3_API_KEY=your-elevenlabs-api-key-here
make test-integration
```
