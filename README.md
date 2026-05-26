# Voice Translate

Turn spoken audio into another language while keeping the speaker’s voice. Upload a recording, choose a target language, and receive translated speech that sounds like the original speaker.

This service runs locally (or on your own server) and uses [ElevenLabs](https://elevenlabs.io) for voice cloning, dubbing, and speech synthesis. You need an ElevenLabs API key with access to voice cloning and dubbing.

## What you need

- **Python 3.10+** (or a compatible version your environment already uses)
- **An ElevenLabs API key** — set as `ELEVENV3_API_KEY` (see [Configuration](#configuration))
- **Network access** to `api.elevenlabs.io` while translating

## Quick start

### 1. Install dependencies

From the project directory:

```bash
pip install -r requirements.txt
```

Or, if you use the project Makefile (creates `.venv` and installs dependencies):

```bash
make deps
```

### 2. Configure your API key

Create a `.env` file in the project root:

```bash
ELEVENV3_API_KEY=your_api_key_here
```

The server loads this file on startup. Values already set in your shell environment are not overwritten.

### 3. Start the server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or:

```bash
make run
```

The API is available at `http://localhost:8000`. Open `http://localhost:8000/docs` in a browser for an interactive form to try translations without writing code.

### 4. Translate audio

Send a **POST** request to `/translate` with:

| Field | Description |
|-------|-------------|
| `source_audio` | Audio file (multipart upload) |
| `target_language` | One of: `en`, `es`, `fr`, `de` |

**Example with curl:**

```bash
curl -X POST "http://localhost:8000/translate" \
  -F "target_language=es" \
  -F "source_audio=@/path/to/your/recording.wav" \
  --output translated.mp3
```

A successful response is raw audio (typically MP3). Save it with `--output` as shown, or play it from your HTTP client if it supports binary responses.

## Supported inputs and outputs

**Target languages:** English (`en`), Spanish (`es`), French (`fr`), German (`de`).

**Input formats:** `.wav`, `.mp3`, `.m4a`, `.ogg`, `.webm`

**Response:** Translated audio as MP3 or WAV, depending on what the pipeline returns. The `Content-Type` header reflects the format.

**Source language:** Detected automatically; you only specify the target language.

## API overview

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Service info and links |
| `/health` | GET | Liveness check (`{"status":"ok"}`) |
| `/ready` | GET | Readiness check (API key configured) |
| `/translate` | POST | Upload audio and receive translation |
| `/docs` | GET | Interactive API documentation (Swagger UI) |

### Common errors

| Status | Meaning |
|--------|---------|
| 400 | Missing file, empty file, or invalid upload |
| 401 | Missing or invalid `X-API-Key` when `SERVICE_API_KEY` is set |
| 413 | Upload exceeds `MAX_UPLOAD_BYTES` |
| 415 | Unsupported audio format |
| 422 | Invalid `target_language` |
| 502 | Translation output failed quality validation |
| 503 | ElevenLabs timeout or configuration/auth problem |
| 500 | Unexpected failure during translation |

Error bodies include a `detail` message you can show to users or logs.

## How long does it take?

Translation is not instant. The service clones a voice profile from your upload, runs dubbing, applies the cloned voice to the dubbed audio, and may normalize output length. ElevenLabs dubbing is polled until complete (up to about 90 seconds). Plan for **roughly 30–90 seconds** per request for typical clips; longer source audio can take more time and consume more API quota.

## Privacy and data handling

- Uploaded audio is written to a temporary file on the server for processing, then deleted.
- A short-lived voice profile is created on ElevenLabs for your clip and **deleted after each request** when possible.
- Audio and API traffic go to ElevenLabs under your account; review their terms and data policies before production use.

## Configuration reference

| Variable | Required | Description |
|----------|----------|-------------|
| `ELEVENV3_API_KEY` | Yes | ElevenLabs API key used for voice clone, dubbing, and speech-to-speech |
| `SERVICE_API_KEY` | No | When set, clients must send matching `X-API-Key` on `/translate` |
| `MAX_UPLOAD_BYTES` | No | Maximum upload size in bytes (default: 26214400, 25 MiB) |

If the key is missing or invalid, `/translate` returns **503** with an authentication-related message.

## Verifying the installation

Check that the server is up:

```bash
curl http://localhost:8000/health
```

Expect: `{"status":"ok"}`.

For a full end-to-end test against the real ElevenLabs API (slow, uses quota):

```bash
ELEVENV3_API_KEY=your_key make test-integration
```

Unit tests and typecheck (no ElevenLabs calls):

```bash
make check
```

Or separately:

```bash
make test
make typecheck
```

## Troubleshooting

**“Eleven API key invalid or expired” or “Voice Clone API key invalid or expired”**  
Confirm `ELEVENV3_API_KEY` in `.env` or your environment, and that the key has the needed ElevenLabs product access.

**503 / timeout**  
The upstream service may be slow or overloaded. Retry with a shorter clip or wait and try again.

**415 Unsupported audio format**  
Use one of the supported extensions listed above.

**422 Unsupported target language**  
Use exactly `en`, `es`, `fr`, or `de`.

## License and third-party services

Translation quality, availability, and billing depend on ElevenLabs. This application is a thin wrapper around their voice clone, dubbing, and speech-to-speech APIs; usage counts against your ElevenLabs account.
