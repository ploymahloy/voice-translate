# Voice Translate

[![CI/CD](https://github.com/ploymahloy/voice-translate/actions/workflows/ci.yml/badge.svg)](https://github.com/ploymahloy/voice-translate/actions/workflows/ci.yml)

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
PYTHONPATH=. uvicorn server.main:app --host 0.0.0.0 --port 8000
```

Or:

```bash
make run
```

The API is available at `http://34.201.102.73`. Open `http://34.201.102.73/docs` in a browser for an interactive form to try translations without writing code.

### 4. Translate audio

Send a **POST** request to `/translate` with:


| Field             | Description                                                |
| ----------------- | ---------------------------------------------------------- |
| `source_audio`    | Audio file (multipart upload)                              |
| `target_language` | ISO 639-3 code (see [Target languages](#target-languages)) |


**Example with curl:**

```bash
curl -X POST "http://34.201.102.73/translate" \
  -F "target_language=spa" \
  -F "source_audio=@/path/to/your/recording.wav" \
  --output translated.mp3
```

A successful response is raw audio (typically MP3). Save it with `--output` as shown, or play it from your HTTP client if it supports binary responses.

## Supported inputs and outputs

### Target languages

`target_language` must be an **ISO 639-3** code. The canonical list lives in [`shared/languages.json`](shared/languages.json); the web UI shows the same languages sorted alphabetically by code.

**Accepted languages (74):**

| Code | Language | Code | Language | Code | Language |
| ---- | -------- | ---- | -------- | ---- | -------- |
| `afr` | Afrikaans | `ara` | Arabic | `asm` | Assamese |
| `aze` | Azerbaijani | `bel` | Belarusian | `ben` | Bengali |
| `bos` | Bosnian | `bul` | Bulgarian | `cat` | Catalan |
| `ceb` | Cebuano | `ces` | Czech | `cym` | Welsh |
| `dan` | Danish | `deu` | German | `ell` | Greek |
| `eng` | English | `est` | Estonian | `fil` | Filipino |
| `fin` | Finnish | `fra` | French | `gle` | Irish |
| `glg` | Galician | `guj` | Gujarati | `hau` | Hausa |
| `heb` | Hebrew | `hin` | Hindi | `hrv` | Croatian |
| `hye` | Armenian | `ind` | Indonesian | `isl` | Icelandic |
| `ita` | Italian | `jav` | Javanese | `kan` | Kannada |
| `kat` | Georgian | `kaz` | Kazakh | `kir` | Kyrgyz |
| `kor` | Korean | `lav` | Latvian | `lin` | Lingala |
| `lit` | Lithuanian | `ltz` | Luxembourgish | `mal` | Malayalam |
| `mar` | Marathi | `msa` | Malay | `nep` | Nepali |
| `nld` | Dutch | `nor` | Norwegian | `nya` | Chichewa |
| `ori` | Odia | `pan` | Punjabi | `pol` | Polish |
| `por` | Portuguese | `pus` | Pashto | `ron` | Romanian |
| `rus` | Russian | `slk` | Slovak | `slv` | Slovenian |
| `som` | Somali | `spa` | Spanish | `srp` | Serbian |
| `swe` | Swedish | `swa` | Swahili | `tam` | Tamil |
| `tel` | Telugu | `tgl` | Tagalog | `tha` | Thai |
| `tur` | Turkish | `ukr` | Ukrainian | `urd` | Urdu |
| `vie` | Vietnamese | `yor` | Yoruba | `yue` | Cantonese |
| `zho` | Chinese (Mandarin) | `zul` | Zulu | | |

**Breaking change:** older 2-letter codes are no longer accepted. Migrate as follows:

| Old (ISO 639-1) | New (ISO 639-3) |
| --------------- | --------------- |
| `en`            | `eng`           |
| `es`            | `spa`           |
| `fr`            | `fra`           |
| `de`            | `deu`           |

**Input formats:** `.wav`, `.mp3`

**Response:** Translated audio as MP3 or WAV, depending on what the pipeline returns. The `Content-Type` header reflects the format.

**Source language:** Detected automatically; you only specify the target language.

## API overview


| Endpoint     | Method | Purpose                                    |
| ------------ | ------ | ------------------------------------------ |
| `/`          | GET    | Service info and links                     |
| `/health`    | GET    | Liveness check (`{"status":"ok"}`)         |
| `/ready`     | GET    | Readiness check (API key configured)       |
| `/translate` | POST   | Upload audio and receive translation       |
| `/docs`      | GET    | Interactive API documentation (Swagger UI) |


### Common errors


| Status | Meaning                                                      |
| ------ | ------------------------------------------------------------ |
| 400    | Missing file, empty file, or invalid upload                  |
| 401    | Missing or invalid `X-API-Key` when `SERVICE_API_KEY` is set |
| 413    | Upload exceeds `MAX_UPLOAD_BYTES`                            |
| 415    | Unsupported audio format                                     |
| 422    | Invalid `target_language`                                    |
| 502    | Translation output failed quality validation                 |
| 503    | ElevenLabs timeout or configuration/auth problem             |
| 500    | Unexpected failure during translation                        |


Error bodies include a `detail` message you can show to users or logs.

## How long does it take?

Translation is not instant. The service clones a voice profile from your upload, runs dubbing, applies the cloned voice to the dubbed audio, and may normalize output length. ElevenLabs dubbing is polled until complete (up to about 90 seconds). Plan for **roughly 30–90 seconds** per request for typical clips; longer source audio can take more time and consume more API quota.

## Privacy and data handling

- Uploaded audio is written to a temporary file on the server for processing, then deleted.
- A short-lived voice profile is created on ElevenLabs for your clip and **deleted after each request** when possible.
- Audio and API traffic go to ElevenLabs under your account; review their terms and data policies before production use.

## Configuration reference


| Variable           | Required | Description                                                                                   |
| ------------------ | -------- | --------------------------------------------------------------------------------------------- |
| `ELEVENV3_API_KEY` | Yes      | ElevenLabs API key used for voice clone, dubbing, and speech-to-speech                        |
| `SERVICE_API_KEY`  | No       | When set, clients must send matching `X-API-Key` on `/translate`                              |
| `MAX_UPLOAD_BYTES` | No       | Maximum upload size in bytes (default: 26214400, 25 MiB)                                      |
| `CORS_ORIGINS`     | No       | Comma-separated browser origins allowed for the web client (default: `http://localhost:4321`) |


If the key is missing or invalid, `/translate` returns **503** with an authentication-related message.

## Web client

An Astro + TypeScript UI lives in `[client/](client/)`. It uploads audio and calls the API from the browser.

### Local development

Use two terminals:

```bash
make run          # API on http://34.201.102.73
make client-dev   # UI on http://localhost:4321 (proxies /translate → API)
```

Install client dependencies once:

```bash
make client-install
```

Copy `[client/.env.example](client/.env.example)` to `client/.env` if you need a production API URL or a dev-only `PUBLIC_DEV_API_KEY` when `SERVICE_API_KEY` is set on the API.

### Production deployment

- **Client:** build static assets with `make client-build` and deploy `client/dist/` to your static host.
- **Vercel:** deploy from `client/` (or set the project root to `client`). `[client/vercel.json](client/vercel.json)` rewrites `/api/`* to the EC2 API (for API routes that use that prefix). Leave `PUBLIC_API_BASE_URL` unset so the browser calls `/translate` on your app origin in this client.
- **API:** set `CORS_ORIGINS` to your deployed app origin(s) only if the browser calls the API host directly (e.g. when `PUBLIC_API_BASE_URL` points at EC2). Same-origin proxying via Vercel does not require CORS changes.
- **Client env (optional):** set `PUBLIC_API_BASE_URL` to a dedicated API origin (no trailing slash), e.g. `https://api.your-domain.com`, instead of using `/api` rewrites.

Do not set `PUBLIC_DEV_API_KEY` or `SERVICE_API_KEY` for public browser traffic—the key would be visible to users. Leave `SERVICE_API_KEY` unset in production unless you add server-side auth later.

### Client tests

```bash
make client-test
```

## Verifying the installation

Check that the server is up:

```bash
curl http://34.201.102.73/health
```

Expect: `{"status":"ok"}`.

For a full end-to-end test against the real ElevenLabs API (slow, uses quota):

```bash
ELEVENV3_API_KEY=your_key make test-integration
```

Unit tests, typecheck, and client tests (no ElevenLabs calls):

```bash
make check
```

Or separately:

```bash
make test
make typecheck
make client-test
```

## Troubleshooting

**“Eleven API key invalid or expired” or “Voice Clone API key invalid or expired”**  
Confirm `ELEVENV3_API_KEY` in `.env` or your environment, and that the key has the needed ElevenLabs product access.

**503 / timeout**  
The upstream service may be slow or overloaded. Retry with a shorter clip or wait and try again.

**415 Unsupported audio format**  
Use one of the supported extensions listed above.

**422 Unsupported target language**  
Use a code from `[shared/languages.json](shared/languages.json)` (ISO 639-3, e.g. `spa` for Spanish).

## License and third-party services

Translation quality, availability, and billing depend on ElevenLabs. This application is a thin wrapper around their voice clone, dubbing, and speech-to-speech APIs; usage counts against your ElevenLabs account.
