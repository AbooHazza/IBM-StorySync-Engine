# IBM-StorySync-Engine

Overview
--------
IBM-StorySync-Engine is a local toolkit integrating IBM cloud services for narrative generation, retrieval, and storage. It contains example tooling and scripts to connect to IBM Cloud services (watsonx.ai, NLU, Cloudant) to process and generate story content.

Features
--------
- Content ingestion and parsing
- Generation via Watson/watsonx.ai
- Retrieval and lightweight persistence (Cloudant example)
- Test connection scripts and examples

Tech Stack
----------
- Python 3.9+
- IBM Cloud SDKs (watsonx.ai, NLU, Cloudant)

Setup
-----
1. Create a Python virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r NarrativeAI/requirements.txt
```

2. Copy `.env.example` to `.env` and fill in your IBM credentials:

```bash
cp NarrativeAI/.env.example .env
# Edit .env and add your API keys and URLs
```

3. Run tests / connection checks:

```bash
python NarrativeAI/test_connections.py
```

Disclaimer
----------
This repository is public-ready, but it requires personal API keys and credentials to function. Do NOT commit your `.env` file or any API keys. Populate the `.env` file locally with your own IBM Cloud API keys (for example `IBM_CLOUD_API_KEY`, `WATSONX_URL`, etc.).

License
-------
Add an appropriate license file if you plan to open-source this project.
