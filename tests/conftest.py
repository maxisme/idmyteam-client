import pytest

@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    monkeypatch.delattr("camera.run")
