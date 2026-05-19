# Finance VoiceAgent

Repository: https://github.com/Frosty2801/AI_Voiceagent.git


<div align="center">
  <p><strong>Conversational personal finance assistant</strong> with text + voice modes, tool-backed answers, and real-time currency & crypto data.</p>
</div>

<p align="center">
  <img alt="Tool usage badge" src="https://img.shields.io/badge/Tools-Enabled-success" />
  <img alt="Voice mode" src="https://img.shields.io/badge/Voice-Web%20Speech%20Fallback-444" />
  <img alt="License" src="https://img.shields.io/badge/License-MIT-yellowgreen" />
</p>

> [!IMPORTANT]
> Finance VoiceAgent is for educational and personal finance workflows. It is **not** professional financial, investment, legal, or tax advice.

---

## ✨ Features

- 💬 **Chat + session memory** for multi-turn conversations
- 🎙️ **Voice mode** (backend TTS with **Web Speech API fallback**)
- 🔎 **Tool-backed responses** with a persistent visual badge when tools are used
- 💱 **Currency conversion** using a public exchange-rate API
- 📈 **Crypto price lookup** via CoinGecko public API
- 🧮 **Safe calculator** (no `eval`)
- 🐳 **Docker Compose** for one-command setup (backend + frontend)

---

## 🚀 Quick Start

### 1) Run with Docker

```bash
docker compose up --build
```

If your Docker installation uses the legacy command:

```bash
docker-compose up --build
```

Then open:

- Frontend: `http://localhost:5173`
- Backend health check: `http://localhost:8000/health`

---

## 📦 Local Development

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

---

## 🧰 How It Works

The backend orchestrates an agent that can decide whether a user request should be answered directly or handled through tools:

- **Currency converter** (real exchange rates)
- **Crypto price lookup** (CoinGecko)
- **Safe arithmetic calculator** (for budgeting/savings math)

When tools are used, the UI shows a persistent badge so users can tell when the assistant performed an external/structured action.

---

## 🔧 Available Tools

### `currency_converter`

Converts money between currencies using a public exchange-rate API.

**Parameters**

- `amount`: numeric amount to convert
- `from_currency`: ISO currency code (e.g., `USD`)
- `to_currency`: ISO currency code (e.g., `EUR`)

**Example**

```text
Convert 100 USD to EUR.
```

---

### `safe_calculator`

Evaluates arithmetic expressions for budgeting and savings calculations.

**Supported operators**: `+`, `-`, `*`, `/`, `%`, `**`, parentheses.

**Parameters**

- `expression`: arithmetic expression

**Example**

```text
If I save 250 every month for 12 months, how much will I save?
```

---

### `crypto_price_lookup`

Gets current cryptocurrency prices and 24-hour percentage change via CoinGecko public API.

**Parameters**

- `crypto_id`: CoinGecko coin id (e.g., `bitcoin`, `ethereum`)
- `vs_currency`: target currency code (e.g., `usd`, `eur`, `cop`)

**Example prompts**

```text
What is the current Bitcoin price in USD?
How much is ETH in EUR?
What is BTC price in COP?
```

---

## ⚙️ Configuration

### Environment Variables

Create a local `.env` from the example:

```bash
cp .env.example .env
```

Set your variables (example):

```env
NVIDIA_API_KEY=your_key_here
NVIDIA_MODEL=meta/llama-3.1-70b-instruct
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1

CURRENCY_API_BASE_URL=https://open.er-api.com/v6/latest
CRYPTO_API_BASE_URL=https://api.coingecko.com/api/v3

ENABLE_COQUI_TTS=true
COQUI_TTS_MODEL=tts_models/en/ljspeech/vits
TTS_FALLBACK_ENABLED=true

FRONTEND_ORIGIN=*
```

> [!NOTE]
> No secrets should be committed to the repository.

---

## 🧪 Manual Test Scenarios

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

Crypto price tool:

```text
What is the current Bitcoin price in USD?
```

Memory (multi-turn):

```text
My monthly income is 2000 USD.
How much is 20% of that?
```

Voice mode:

1. Select `Voice`.
2. Send any supported question.
3. When Coqui TTS is available, the backend generates audio.
4. If Coqui fails, the browser uses the Web Speech API as fallback.

---

## 🏗️ Architecture

### Backend (Python / FastAPI)

- `app/api`: HTTP routes
- `app/core`: settings + conversation memory
- `app/schemas`: request/response contracts
- `app/services`: agent orchestration and text-to-speech
- `app/tools`: tool implementations

### Frontend (React)

- `frontend/src/components`: chat UI components
- `frontend/src/api`: backend client
- `frontend/src/utils`: session + browser speech helpers

---

## 🤝 Contributing

Contributions are welcome.

Suggested workflow:

1. Fork the repository
2. Create a branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'feat: add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📌 Known Limitations

- Session memory is stored in RAM and resets when the backend restarts.
- Coqui TTS can be slower on CPU and increases Docker image size.
- Public currency/crypto APIs can be rate-limited or temporarily unavailable.
- RAG is intentionally excluded from the first implementation scope.

