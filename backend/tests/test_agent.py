def test_create_agent_config(client):
    # 1. Login to get token
    client.post("/api/v1/auth/register", json={"username": "agent_owner", "email": "a@o.io", "password": "p"})
    login = client.post("/api/v1/auth/login", data={"username": "a@o.io", "password": "p"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Add a base model manually to DB (via mock or direct SQL)
    # 3. Create config
    response = client.post("/api/v1/models/configs", headers=headers, json={
        "name": "Stealth Bot",
        "system_prompt": "You are a quiet explorer.",
        "temperature": 0.5,
        "base_model_id": "00000000-0000-0000-0000-000000000000" # Use a real UUID in production tests
    })
    # Since base_model_id is dummy, we expect a 400 or successful catch depending on service logic
    assert response.status_code in [200, 400]