"""Integrity validators for Domain Profile topologies."""

from typing import List
from scof_shared.profile.loader import DomainProfile


def validate_profile_topology(profile: DomainProfile) -> List[str]:
    """Validates domain profile topology for entity duplicate IDs, invalid coordinates,

    duplicate SKUs, and negative constraints. Returns a list of validation error strings.
    """
    errors: List[str] = []
    seen_ids = set()

    # Check manufacturer
    mfg = profile.topology.manufacturer
    if mfg.id in seen_ids:
        errors.append(f"Duplicate entity ID detected: {mfg.id}")
    else:
        seen_ids.add(mfg.id)

    if not (-90 <= mfg.location.lat <= 90) or not (-180 <= mfg.location.lon <= 180):
        errors.append(f"Invalid location coordinates for manufacturer {mfg.id}: {mfg.location}")

    # Check products
    seen_skus = set()
    for prod in profile.topology.products:
        if prod.id in seen_ids:
            errors.append(f"Duplicate entity ID detected: {prod.id}")
        else:
            seen_ids.add(prod.id)

        if prod.sku in seen_skus:
            errors.append(f"Duplicate SKU detected: {prod.sku}")
        else:
            seen_skus.add(prod.sku)

    # Check suppliers
    for sup in profile.topology.suppliers:
        if sup.id in seen_ids:
            errors.append(f"Duplicate entity ID detected: {sup.id}")
        else:
            seen_ids.add(sup.id)

        if sup.lead_time_days <= 0:
            errors.append(f"Supplier {sup.id} lead_time_days must be positive: {sup.lead_time_days}")

        if not (-90 <= sup.location.lat <= 90) or not (-180 <= sup.location.lon <= 180):
            errors.append(f"Invalid location coordinates for supplier {sup.id}: {sup.location}")

    # Check warehouses
    for wh in profile.topology.warehouses:
        if wh.id in seen_ids:
            errors.append(f"Duplicate entity ID detected: {wh.id}")
        else:
            seen_ids.add(wh.id)

        if wh.capacity_units <= 0:
            errors.append(f"Warehouse {wh.id} capacity_units must be positive: {wh.capacity_units}")

        if not (-90 <= wh.location.lat <= 90) or not (-180 <= wh.location.lon <= 180):
            errors.append(f"Invalid location coordinates for warehouse {wh.id}: {wh.location}")

    # Check distribution centers
    for dc in profile.topology.distribution_centers:
        if dc.id in seen_ids:
            errors.append(f"Duplicate entity ID detected: {dc.id}")
        else:
            seen_ids.add(dc.id)

        if not (-90 <= dc.location.lat <= 90) or not (-180 <= dc.location.lon <= 180):
            errors.append(f"Invalid location coordinates for distribution center {dc.id}: {dc.location}")

    return errors
