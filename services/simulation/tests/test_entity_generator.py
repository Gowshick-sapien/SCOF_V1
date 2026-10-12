"""Unit tests for Master Data Entity Generator."""

from pathlib import Path
from scof_shared.profile.loader import ProfileLoader
from services.simulation.src.entity_generator import EntityGenerator, calculate_haversine_distance

PROFILE_PATH = Path("profiles/mvp-electronics")


def test_haversine_distance():
    # Distance between Sriperumbudur (12.9716, 79.9416) and Chennai Port (13.0827, 80.2907) ~ 40 km
    dist = calculate_haversine_distance(12.9716, 79.9416, 13.0827, 80.2907)
    assert 35.0 < dist < 45.0


def test_entity_generator():
    profile = ProfileLoader.load_profile(PROFILE_PATH)
    gen = EntityGenerator(profile)
    data = gen.generate_all()

    assert len(data["manufacturers"]) == 1
    assert data["manufacturers"][0]["id"].startswith("mfg-")

    assert len(data["products"]) == 3
    for p in data["products"]:
        assert p["id"].startswith("prod-")

    assert len(data["suppliers"]) == 8
    for s in data["suppliers"]:
        assert s["id"].startswith("sup-")

    assert len(data["warehouses"]) == 4
    for w in data["warehouses"]:
        assert w["id"].startswith("wh-")

    assert len(data["distribution_centers"]) == 3
    for dc in data["distribution_centers"]:
        assert dc["id"].startswith("dc-")

    # Supplier Products sourcing junction
    sp_list = data["supplier_products"]
    assert len(sp_list) == 9  # 3 products * 3 sourcing options each
    preferred_count = sum(1 for sp in sp_list if sp["is_preferred_supplier"])
    alternate_count = sum(1 for sp in sp_list if not sp["is_preferred_supplier"])
    assert preferred_count == 3
    assert alternate_count == 6

    # Polymorphic routes
    routes = data["routes"]
    assert len(routes) == 48  # 32 (sup->wh) + 12 (wh->dc) + 4 (wh->mfg)
    for r in routes:
        assert r["id"].startswith("route-")
        assert r["origin_type"] in ("supplier", "warehouse")
        assert r["destination_type"] in ("warehouse", "distribution_center", "manufacturer")

