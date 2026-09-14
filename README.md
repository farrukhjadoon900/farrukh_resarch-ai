# Jarvis — Groq + CrewAI

Repo: farrukh_resarch-ai

Secret name: `groq_api_key`

## Mobile run
1. Settings → Secrets → `groq_api_key` = your gsk_ key
2. Issues → new issue → comment:
   `/jarvis learn React performance`
3. Actions tab → wait → answer on same issue

## Local (optional)
```bash
pip install -r requirements.txt
cp .env.example .env
export PYTHONPATH=src
python -m jarvis.cli ask "hello"
