# Vinayaka Cloth Store Backend

Backend API for the Vinayaka Cloth Store project, built using FastAPI.

## Requirements

- Python 3.13 or compatible version
- pip

## Setup

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the application

```powershell
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

Health endpoint: `http://127.0.0.1:8000/health`

## Code quality

Check the code with Ruff:

```powershell
python -m ruff check .
```

## Tests

Run the test suite:

```powershell
python -m pytest
```

**Note:** If running tests locally, set the `DATABASE_URL` environment variable to a suitable value. The current health test does not connect to the database, but the application requires the setting during startup.

For the local test environment, you can use:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://vinayaka:vinayaka@localhost:5432/vinayaka"
```

## Continuous integration

GitHub Actions runs Ruff and pytest for pushes to `main` and pull requests targeting `main`.