def test_get_live(client):
    res = client.get("/live")
    assert res.status_code == 200
