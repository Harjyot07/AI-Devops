import requests

# Read log file
with open("error.log", "r") as f:
    logs = f.read()

prompt = f"""
You are DevOps AI assistant.

Analyze this Docker/Jenkins error:

{logs}

Explain:
1. What is the issue
2. Why it happened
3. How to fix it
"""

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }
)

result = response.json()

print(result["response"])
