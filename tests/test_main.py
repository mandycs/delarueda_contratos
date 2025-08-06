from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def get_access_token():
    response = client.post("/token", data={"username": "testuser", "password": "testpassword"})
    return response.json()["access_token"]

def test_create_contract():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/contracts/", 
        headers=headers,
        data={
            "client_data": '{"name": "Test Client", "email": "test@example.com"}'
        },
        files={
            "design_image": ("test_image.png", open("test_image.png", "rb"), "image/png")
        }
    )
    assert response.status_code == 200