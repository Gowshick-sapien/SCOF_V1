"""Unit tests for Domain Profile loading, hashing, and validation."""

from pathlib import Path
import pytest
from scof_shared.profile.loader import ProfileLoader, compute_profile_hash
from scof_shared.profile.validators import validate_profile_topology

PROFILE_PATH = Path("profiles/mvp-electronics")


def test_load_profile():
    profile = ProfileLoader.load_profile(PROFILE_PATH)
    assert profile.meta.profile_id == "mvp-electronics"
    assert profile.meta.version == "1.0.0"
    assert len(profile.topology.products) == 3
    assert len(profile.topology.suppliers) == 5
    assert len(profile.topology.warehouses) == 2
    assert len(profile.topology.distribution_centers) == 1


def test_profile_hash():
    p_hash = compute_profile_hash(PROFILE_PATH)
    assert isinstance(p_hash, str)
    assert len(p_hash) == 64  # SHA-256 hex string length

    # Re-computing yields identical hash
    p_hash2 = compute_profile_hash(PROFILE_PATH)
    assert p_hash == p_hash2


def test_topology_validation():
    profile = ProfileLoader.load_profile(PROFILE_PATH)
    errors = validate_profile_topology(profile)
    assert errors == []
