# SLM Server

A Small Language Model (SLM) implemented in Python.
Model: [Mistral 7B](https://huggingface.co/mistralai/Mistral-7B-v0.1) from [Ollama](https://ollama.com/).
Backend: [Flask](https://flask.palletsprojects.com/en/stable/).

## Requirements
 - Python 3.8 or higher
   - Flask
   - Ollama
   - Requests
 - Ollama
 - Mistral 7B model
 - At least 8GB of RAM

## Installation and Usage
 1. Install the [Ollama](https://ollama.com/download) client
 2. Install Mistral 7B model using the command:
    ```bash
    ollama pull mistral
    ```
 3. Install required Python packages, either globally or in an virtual environment, using the command:
    ```bash
    pip install -r requirements.txt
    ```
 4. Run the server using the command:
    ```bash
    python server.py
    ```
 5. Run the client and start chatting, using the command:
    ```bash
    python client.py
    ```