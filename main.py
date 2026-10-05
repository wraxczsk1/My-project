"""ASGI vstup pro hosting: Flask aplikace LSPD MANUAL zabalená ve FastAPI."""
from a2wsgi import WSGIMiddleware
from fastapi import FastAPI

from app import app as flask_app

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/", WSGIMiddleware(flask_app))
