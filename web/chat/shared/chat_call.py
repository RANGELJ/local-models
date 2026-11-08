import os, json
import requests

def chat_call(content: str):
    OLLAMA = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    MODEL = os.environ.get("MODEL", "qwen3:8b")
    ROOT = os.path.realpath(os.path.dirname(__file__))
    MAX_LINES = 200

    response = requests.post(f"{OLLAMA}/api/chat", json={
        "model": MODEL,
        "messages": [{ "role": "user", "content": content }],
        "tools": [],
        "stream": False,
        "think": False,
        "options": {"num_ctx": 8192},
    }, timeout=300)
    response.raise_for_status()
    response_json = response.json()
    print(f"Response JSON: {json.dumps(response_json, indent=2)}")