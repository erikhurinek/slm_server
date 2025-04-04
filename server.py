from flask import Flask, Response, request, jsonify
import ollama

app = Flask(__name__)

SYSTEM_PROMPT = "You are limited to only saying one short sentence at a time."
messages = [{"role": "system", "content": SYSTEM_PROMPT}]


def generate_response():
    try:
        response = ollama.chat(model="Mistral", messages=messages, stream=True)
        full_content = ""
        for chunk in response:
            if "message" in chunk and "content" in chunk["message"]:
                content = chunk["message"]["content"]
                full_content += content
                yield f"data: {content}\n\n"
        messages.append({"role": "assistant", "content": full_content})
    except Exception as e:
        print(f"Error generating response: {e}")
        yield f"data: Error generating response\n\n"

@app.route("/chat", methods=["POST"])
def chat():
    global messages
    
    print("Received request:", request.json)
    
    data = request.json
    prompt = data.get("prompt", "<No message>")
    messages.append({"role": "user", "content": prompt})
    
    
    return Response(
        generate_response(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )

@app.route("/reset", methods=["POST"])
def reset_chat():
    global messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    return jsonify({"message": "Chat history cleared."})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
