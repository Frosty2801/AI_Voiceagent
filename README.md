# Finance VoiceAgent

Finance VoiceAgent is a conversational web app for personal finance questions. Users can ask in a chat interface, choose text or voice responses, and see when the assistant uses a real tool.

The project is built with React, FastAPI, LangChain, NVIDIA AI Endpoints, and Coqui TTS.

## Features

- Conversational finance assistant with session memory.
- Text or voice response mode.
- Persistent visual badge when a tool is used.
- Real currency conversion through a free public API.
- Safe arithmetic calculator without Python `eval`.
- Docker Compose setup for backend and frontend.
- Browser speech fallback when Coqui TTS is unavailable.

## Use Case

The assistant helps with simple personal finance workflows:

- Currency conversion.
- Savings and budget calculations.
- General educational budgeting guidance.

It does not provide professional financial, investment, legal, or tax advice.

## Tools

### `currency_converter`

Converts money between currencies using a free public exchange-rate API.

Parameters:

- `amount`: numeric amount to convert.
- `from_currency`: ISO currency code, for example `USD`.
- `to_currency`: ISO currency code, for example `EUR`.

Example prompt:

```text
Convert 100 USD to EUR.
```

### `safe_calculator`

Evaluates arithmetic expressions for budgeting and savings calculations.

Parameters:

- `expression`: numeric expression with `+`, `-`, `*`, `/`, `%`, `**`, and parentheses.

Example prompt:

```text
If I save 250 every month for 12 months, how much will I save?
```

## Requirements

- Docker and Docker Compose.
- NVIDIA API key for full LLM behavior.

The app also includes a local fallback for basic demos when `NVIDIA_API_KEY` is empty.

## Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Then set:

```env
NVIDIA_API_KEY=your_key_here
NVIDIA_MODEL=meta/llama-3.1-70b-instruct
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
CURRENCY_API_BASE_URL=https://open.er-api.com/v6/latest
ENABLE_COQUI_TTS=true
TTS_FALLBACK_ENABLED=true
FRONTEND_ORIGIN=*
```

No API key should be committed to the repository.

## Run With Docker

```bash
docker compose up --build
```

If your Docker installation uses the legacy command, run:

```bash
docker-compose up --build
```

Open:

```text
http://localhost:5173
```

Backend health check:

```text
http://localhost:8000/health
```

## Local Development

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Manual Test Scenarios

Direct response without tool:

```text
What is a good way to organize my monthly budget?
```

Calculator tool:

```text
If I save 250 every month for 12 months, how much will I save?
```

Currency converter tool:

```text
Convert 100 USD to EUR.
```

Memory:

```text
My monthly income is 2000 USD.
How much is 20% of that?
```

Voice mode:

1. Select `Voice`.
2. Send any supported question.
3. The app plays backend-generated audio when Coqui is available.
4. If Coqui fails, the browser uses Web Speech API as fallback.

## Architecture

Backend modules:

- `app/api`: HTTP routes.
- `app/core`: settings and conversation memory.
- `app/schemas`: request and response contracts.
- `app/services`: agent orchestration and text-to-speech.
- `app/tools`: reusable tool implementations.

Frontend modules:

- `src/components`: chat UI components.
- `src/api`: backend client.
- `src/utils`: session and browser speech helpers.

## Known Limitations

- Session memory is stored in RAM and resets when the backend restarts.
- Coqui TTS can be slow on CPU and increases Docker image size.
- The public currency API can be rate-limited or temporarily unavailable.
- RAG is intentionally excluded from the first implementation scope.
