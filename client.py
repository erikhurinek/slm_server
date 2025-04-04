import requests
import sseclient

url_chat = "http://localhost:5000/chat"

def print_response(prompt):
    try:
        response = requests.post(url_chat, json={"prompt": prompt}, stream=True)
        response.raise_for_status()  # Raise an error for HTTP status codes >= 400
        
        for chunk in response.iter_content(chunk_size=None):
            print(repr(chunk.decode('utf-8')))
        
        client = sseclient.SSEClient(response)
        
        for event in client.events():
            print(event.data, end="", flush=True)  # Print each chunk as it arrives
        print()
    except requests.exceptions.RequestException as e:
        print("response: " + str(response.text))
        print(f"Error: {e}")

user_response = ""
while True:
    prompt = input("You: ").strip()
    if (prompt.lower() == "exit"):
        break
    
    print("Model: ", end="", flush=True)
    print_response(prompt)