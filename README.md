# SLM Server

A Small Language Model (SLM) implemented in Python.
Model: [Gemma 3 1B](https://ai.google.dev/gemma/docs/core) with [Ollama](https://ollama.com/).
Backend: [Flask](https://flask.palletsprojects.com/en/stable/).

## Requirements
 - Python 3.8 or higher
   - Flask
   - Ollama
   - Requests
 - Ollama
 - Gemma 3 1B model
 - At least 8GB of RAM

## Installation and Local Usage
 1. Install the [Ollama](https://ollama.com/download) client
 2. Install Gemma 3 1B model using the command. Other models will work, and should be specified in the `settings.py` file.
    ```bash
    ollama pull gemma3:1b
    ```
 3. Install required Python packages, either globally or in an virtual environment, using the command:
    ```bash
    pip install -r requirements.txt
    ```
 4. Run the server using the command:
    ```bash
    python main.py
    ```
 5. Open your web browser and navigate to `http://localhost:8080/slm-chat` to access the SLM server.

## Code Standards
 - Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code style.
 - Docstrings should follow the [NumPy style](https://numpydoc.readthedocs.io/en/latest/format.html), as this is supported by VSCode.
