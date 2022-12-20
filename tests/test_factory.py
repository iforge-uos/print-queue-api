from print_api.app import create_app


def test_config():
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


def test_451(client):
    response = client.get("/api/v1/misc/legal")
    assert response.data == b"Pipis Room"
