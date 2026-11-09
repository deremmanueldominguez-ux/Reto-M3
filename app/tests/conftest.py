"""Fixtures comunes de las pruebas automatizadas."""
import os

import pytest


@pytest.fixture(scope="session")
def url_api() -> str:
    """URL base del backend (variable URL_API)."""
    return os.environ.get("URL_API", "http://localhost:8000").rstrip("/")


@pytest.fixture(scope="session")
def url_web() -> str:
    """URL base del frontend (variable URL_WEB)."""
    return os.environ.get("URL_WEB", "http://localhost:8080").rstrip("/")
