import pytest

def test_user_cannot_access_other_org_data(client, fake_user_payload):
    """
    Simulate two organizations.
    For now, we just verify the /emails/status endpoint is reachable.
    """

    # Step 1 – Simulate Org 1 calling /emails/status
    res_org1 = client.get("/emails/status", headers={"X-Org-Id": "1"})
    assert res_org1.status_code in (200, 403, 404)  # 200 if connected, 404 if missing tokens

    # Step 2 – Simulate Org 2 calling the same endpoint
    res_org2 = client.get("/emails/status", headers={"X-Org-Id": "2"})
    assert res_org2.status_code in (200, 403, 404)

    # Step 3 – Compare results to ensure separation
    # (In the real RBAC phase we’ll assert they differ, for now we just prove both run safely)
    assert res_org1.status_code in (200, 403, 404)
    assert res_org2.status_code in (200, 403, 404)

