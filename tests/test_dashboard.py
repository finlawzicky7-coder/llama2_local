def test_index_links(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Ringback" in r.text
    assert "/healthz" in r.text


def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_dashboard_404_for_unknown_tenant(client):
    r = client.get("/dashboard/no-such-tenant")
    assert r.status_code == 404


def test_dashboard_renders_for_known_tenant(client, tenant):
    r = client.get(f"/dashboard/{tenant.id}")
    assert r.status_code == 200
    assert tenant.brand in r.text
    assert "no bookings yet" in r.text
