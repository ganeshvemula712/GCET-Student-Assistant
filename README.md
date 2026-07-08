# GCET Student Assistant

Phase 1 foundation starter scaffold for a Python 3.12 AI project.

Project structure:

- `backend/`
  - `app/`
    - `core/`
  - `main.py`
- `frontend/`
- `documents/`
- `tests/`
- `README.md`
- `requirements.txt`
- `.env.example`
- `.gitignore`

## What each file is for

- `backend/main.py`: FastAPI entrypoint for the backend API.
- `backend/app/core/config.py`: Minimal Pydantic settings loader using `.env`.
- `frontend/streamlit_app.py`: Starter Streamlit app shell.
- `tests/test_basic.py`: Simple test to verify the backend app imports.
- `requirements.txt`: Phase 1 dependency list.
- `.env.example`: Minimal environment variables.
- `.gitignore`: Common local files to ignore.

## Setup

1. Create a virtual environment:
   `python -m venv .venv`
2. Activate the environment:
   `.\.venv\Scripts\Activate.ps1`
3. Install dependencies:
   `pip install -r requirements.txt`
4. Copy environment example:
   `copy .env.example .env`
5. Start the backend:
   `uvicorn backend.main:app --reload`
6. Start the frontend:
   `streamlit run frontend/streamlit_app.py`
