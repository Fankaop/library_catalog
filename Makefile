run:
	PYTHONPATH=src .venv/bin/uvicorn src.library_catalog.main:app --host 127.0.0.1 --port 8000 --reload
