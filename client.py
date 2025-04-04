import requests

URL_CHAT = "http://localhost:5000/chat"


def print_response(prompt):
    try:
        response = requests.post(URL_CHAT, json={"prompt": prompt}, stream=True)
        response.raise_for_status()

        for chunk in response.iter_content(chunk_size=None):
            print(chunk.decode("utf-8"), end="", flush=True)

    except requests.exceptions.RequestException as e:
        print("response: " + str(response.text))
        print(f"Error: {e}")

    print()

def reset_chat():
    try:
        response = requests.post("http://localhost:5000/reset")
        response.raise_for_status()
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error resetting chat: {e}")

user_response = ""
while True:
    prompt = input("You: ").strip()
    
    if prompt.lower() == "exit":
        break
    elif prompt.lower() == "reset":
        reset_chat()
        continue

    print("Model: ", end="", flush=True)
    print_response(prompt)
