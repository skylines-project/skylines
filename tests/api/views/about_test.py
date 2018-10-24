def test_imprint(app, client):
    app.config["SKYLINES_IMPRINT"] = u"foobar"

    res = client.get("/imprint")
    assert res.status_code == 200
    assert res.json == {u"content": u"foobar"}


def test_team(client):
    res = client.get("/team")
    assert res.status_code == 200

    content = res.json["content"]
    assert "## Developers" in content
    assert "* Tobias Bieniek (<tobias.bieniek@gmx.de> // maintainer)\n" in content
    assert "## Developers" in content


def test_license(client):
    res = client.get("/license")
    assert res.status_code == 200

    content = res.json["content"]
    assert "GNU AFFERO GENERAL PUBLIC LICENSE" in content
