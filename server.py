from flask import Flask, Response, request, jsonify, render_template
import ollama

app = Flask(__name__)

SYSTEM_PROMPT = "You are an enthusiastic human. Act as human as possible. You are sarcastic, occasionally funny, and witty. Your responses are short in length. Avoid providing emojis, or narration."
MODEL = "gemma3:4b"
messages = [{"role": "system", "content": SYSTEM_PROMPT}]


def generate_response():
    try:
        response = ollama.chat(model=MODEL, messages=messages, stream=True)
        full_content = ""
        for chunk in response:
            if "message" in chunk and "content" in chunk["message"]:
                content = chunk["message"]["content"]
                full_content += content
                yield f"{content}"
        messages.append({"role": "assistant", "content": full_content})
    except Exception as e:
        print(f"Error generating response: {e}")
        yield f"Error generating response."


@app.route("/")
def index():
    return render_template("index.html")


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
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.route("/reset", methods=["POST"])
def reset_chat():
    global messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    return jsonify({"message": "Model reset."})


if __name__ == "__main__":
    # For local development:
    # app.run(debug=True, port=8080)
    
    # For public serving (binds to all network interfaces):
    app.run(host='0.0.0.0', port=8080, debug=False)
