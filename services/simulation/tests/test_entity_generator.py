"""Unit tests for Master Data Entity Generator."""

from pathlib import Path
from scof_shared.profile.loader import ProfileLoader
from services.simulation.src.entity_generator import EntityGenerator, calculate_haversine_distance

PROFILE_PATH = Path("profiles/mvp-electronics")


def test_haversine_distance():
    # Distance between Shenzhen (22.5431, 114.0579) and Hong Kong (22.3193, 114.1694) ~ 27 km
    dist = calculate_haversine_distance(22.5431, 114.0579, 22.3193, 114.1694)
    assert 20.0 < dist < 40.0


def test_entity_generator():
    profile = ProfileLoader.load_profile(PROFILE_PATH)
    gen = EntityGenerator(profile)
    data = gen.generate_all()

    assert len(data["manufacturers"]) == 1
    assert data["manufacturers"][0]["id"].startswith("mfg-")

    assert len(data["products"]) == 3
    for p in data["products"]:
        assert p["id"].startswith("prod-")

    assert len(data["suppliers"]) == 5
    for s in data["suppliers"]:
        assert s["id"].startswith("sup-")

    assert len(data["warehouses"]) == 2
    for w in data["warehouses"]:
        assert w["id"].startswith("wh-")

    assert len(data["distribution_centers"]) == 1
    for dc in data["distribution_centers"]:
        assert dc["id"].startswith("dc-")

    # Supplier Products sourcing junction
    sp_list = data["supplier_products"]
    assert len(sp_list) == 6  # 3 products * 2 sourcing options each
    preferred_count = sum(1 for sp in sp_list if sp["is_preferred_supplier"])
    alternate_count = sum(1 for sp in sp_list if not sp["is_preferred_supplier"])
    assert preferred_count == 3
    assert alternate_count == 3

    # Polymorphic routes
    routes = data["routes"]
    assert len(routes) > 0
    for r in routes:
        assert r["id"].startswith("route-")
        assert r["origin_type"] in ("supplier", "warehouse")
        assert r["destination_type"] in ("warehouse", "distribution_center", "manufacturer")
