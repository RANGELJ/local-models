import os, sys, json, requests, logging

logging.basicConfig(level=logging.DEBUG)

OLLAMA = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("MODEL", "qwen3:8b")
ROOT = os.path.realpath(os.path.dirname(__file__))  # /app in the container
MAX_LINES = 200


def read_file(path):
    full = os.path.realpath(os.path.join(ROOT, path))
    if not full.startswith(ROOT + os.sep):
        return "error: path is outside the allowed directory"
    try:
        with open(full, errors="replace") as f:
            lines = f.read().splitlines()
    except OSError as exception:
        return f"error: {exception}"
    out = "\n".join(f"{i + 1}: {line}" for i, line in enumerate(lines[:MAX_LINES]))
    if len(lines) > MAX_LINES:
        out += f"\n[truncated: {len(lines)} lines total]"
    return out


FUNCTIONS = {"read_file": read_file}

TOOLS = [{
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read a text file, returned with line numbers.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Relative file path, e.g. agent.py"}},
            "required": ["path"],
        },
    },
}]

messages = [{"role": "system", "content": "You are a concise assistant. Use read_file when asked about a file; do not guess its contents."}]


def chat_call():
    response = requests.post(f"{OLLAMA}/api/chat", json={
        "model": MODEL,
        "messages": messages,
        "tools": TOOLS,
        "stream": False,
        "think": False,
        "options": {"num_ctx": 8192},
    }, timeout=300)
    response.raise_for_status()
    response_json = response.json()
    logging.debug(f"Response JSON: {json.dumps(response_json, indent=2)}")
    return response_json["message"]


while True:
    try:
        messages.append({"role": "user", "content": input("User: ")})
    except (KeyboardInterrupt, EOFError):
        print("\nExiting...")
        sys.exit(0)

    try:
        for _ in range(5):
            reply = chat_call()
            messages.append(reply)
            calls = reply.get("tool_calls")
            if not calls:
                print(f"Assistant: {reply['content']}")
                break
            for call in calls:
                name = call["function"]["name"]
                args = call["function"]["arguments"]
                print(f"[tool] {name}({json.dumps(args)})")
                function = FUNCTIONS.get(name)
                try:
                    result = function(**args) if function else f"error: unknown tool {name}"
                except TypeError as exception:
                    result = f"error: bad arguments: {exception}"
                messages.append({"role": "tool", "tool_name": name, "content": result})
        else:
            print("Assistant: stopped after 5 tool rounds")
    except requests.exceptions.RequestException as exception:
        print(f"Error connecting to Ollama API: {exception}")
        sys.exit(1)