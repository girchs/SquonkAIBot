# $SquonkAIChatBot

A Telegram bot powered by OpenAI and hosted on Railway.  
This bot responds in a sad, funny, and emotionally unstable style — just like the legendary $SQUONK.

## Features

- Telegram bot integration
- GPT-3.5 powered responses
- Fully Squonkified tone
- Deployable on Railway

---

## Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/squonk-ai-chatbot.git
cd squonk-ai-chatbot
```

### 2. Add Environment Variables

Create a `.env` file or use Railway’s environment dashboard.

```
TELEGRAM_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

Alternatively, copy the template:

```bash
cp .env.example .env
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Locally

```bash
python main.py
```

### 5. Deploy to Railway

- Push your repo to GitHub
- Go to [Railway](https://railway.app/)
- Create a new project from GitHub
- Set the environment variables
- Done!

---

## Example Prompt

User: *Hi Squonk, how are you?*  
Bot: *"Oh you know... still crying. But thanks for asking. I guess."*

---

## License

MIT
