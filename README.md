# `smolagents-gcc-crossref`

A simple agent built with [smolagents](https://github.com/huggingface/smolagents).

## Architecture

```
smolagents-gcc-crossref/
├── pyproject.toml    # Project metadata & dependencies
├── agent.py          # Main agent script
├── tools.py          # Custom tools for the agent
├── .env              # API key configuration (not committed)
└── README.md         # Documentation (this file)
```

## Installation

You will need:

- Python **3.13+**
- An LLM ApiKey

Then, clone the repository and install the dependencies:

```bash
# 1. Clone or navigate into the project folder
cd smolagents-gcc-crossref

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate

# 3. Install the project
pip install -e .
```

### Configuration

You will need to edit/create the `.env` file inside the project root and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-key-here
```

## Usage

```bash
# Make sure your virtual environment is activated
source .venv/bin/activate

# Run the agent
python agent.py
```
