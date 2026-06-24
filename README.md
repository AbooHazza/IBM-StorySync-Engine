




<img width="472" height="214" alt="IBM_Logo_Transparent" src="https://github.com/user-attachments/assets/ed49ac61-7bae-456a-aa4b-4825096256ab" />           <img width="200" height="200"                              alt="water_droplets_icon_transparent" src="https://github.com/user-attachments/assets/b0ef9097-007a-4de3-be1f-b1a755dff6d2" />




# IBM-StorySync-Engine

## Overview

 AI narrative continuity companion built around IBM Cloud services. It provides a spoiler-safe experience by restricting AI context to only the portion of the story you have watched so far, while still allowing semantic search, scene retrieval, and generative assistants.




<img width="1600" height="920" alt="WhatsApp Image 2026-06-19 at 7 10 56 PM" src="https://github.com/user-attachments/assets/8c7df5b8-ee70-451f-9d8e-d0728fa84455" />






## Features

- **Spoiler Shield**: hard-locks the AI context window to the specific timeline of the currently watched video.
- **Semantic Search**: powered by IBM dense embeddings to find scenes by meaning, not just keywords.
- **Intent Routing**: detects whether the user needs a focused answer or a broader lore recap.
- **Metadata Entity Boosting**: Watson NLU extracts characters, locations, and organizations to improve relevance.
- Content ingestion, parsing, and rich narrative generation.
- Connection checks and examples for IBM watsonx.ai, Watson NLU, and Cloudant.

## Tech Stack

- Python 3.9+
- IBM watsonx.ai
- IBM Watson NLU
- IBM Cloudant
- Uvicorn / FastAPI (for the app server)

## Setup

1. Clone the repository:

```bash
git clone https://github.com/AbooHazza/IBM-StorySync-Engine.git
cd IBM-StorySync-Engine
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r NarrativeAI/requirements.txt
```

3. Set up environment variables:

```bash
cp NarrativeAI/.env.example NarrativeAI/.env
```

Open `NarrativeAI/.env` and populate your IBM credentials.

4. Populate data and start the server:

```bash
python NarrativeAI/data_parser.py
uvicorn NarrativeAI.app:app --host 0.0.0.0 --port 8000 --reload
```

5. Open the app in your browser:

```bash
http://localhost:8000
```

## Environment Variables

The repository uses `NarrativeAI/.env.example` as a template. Update the copied `.env` file with your personal API keys and service URLs.

## Security Disclaimer

This repository is intended for public use, but it requires your own IBM Cloud API keys and credentials. Do NOT commit your `.env` file or any secret values to GitHub.

## Notes

- Keep all sensitive credentials out of version control.
- Use the `.gitignore` file already included in the repository to block `venv/`, `__pycache__/`, `.env`, `data.json`, and other local artifacts.
- If you add new secret files, add them to `.gitignore` immediately.


## Credits

**Original Idea:**  [EviLooo](https://github.com/EviLooo)

**Developed as part of an IBM Lab Team Project**

### Contributors

- [AbooHazza](https://github.com/AbooHazza)
- [EviLooo](https://github.com/EviLooo)

