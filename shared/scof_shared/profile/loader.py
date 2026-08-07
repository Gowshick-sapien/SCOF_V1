"""Profile Loader for SCOF Domain Profiles.

Reads entity topologies (topology.yaml), disruption parameters (disruptions.yaml),
and profile metadata (profile.yaml), validates them into Pydantic models, and computes
SHA-256 profile_hash for experiment reproducibility.
"""

import hashlib
from pathlib import Path
from typing import List, Optional, Union
import yaml
from pydantic import BaseModel, Field, ConfigDict


from scof_shared.profile.agents_config import AgentsRosterModel, load_agents_config


class Location(BaseModel):
    lat: float
    lon: float


class ManufacturerModel(BaseModel):
    id: str
    name: str
    location: Location


class ProductModel(BaseModel):
    id: str
    name: str
    sku: str


class SupplierModel(BaseModel):
    id: str
    name: str
    reliability_profile: str
    lead_time_days: int
    location: Location


class WarehouseModel(BaseModel):
    id: str
    name: str
    capacity_units: int
    location: Location


class DistributionCenterModel(BaseModel):
    id: str
    name: str
    location: Location


class TopologyModel(BaseModel):
    manufacturer: ManufacturerModel
    products: List[ProductModel]
    suppliers: List[SupplierModel]
    warehouses: List[WarehouseModel]
    distribution_centers: List[DistributionCenterModel]


class DisruptionTypeModel(BaseModel):
    id: str
    name: str
    severity_range: List[int]
    default_duration_days: int
    target_entity: str


class DisruptionConfigModel(BaseModel):
    disruption_types: List[DisruptionTypeModel]


class ProfileMetaModel(BaseModel):
    profile_id: str
    name: str
    version: str
    description: str
    author: Optional[str] = None


class DomainProfile(BaseModel):
    meta: ProfileMetaModel
    topology: TopologyModel
    disruptions: DisruptionConfigModel
    agents: Optional[AgentsRosterModel] = None
    profile_hash: str
    profile_path: Path

    model_config = ConfigDict(arbitrary_types_allowed=True)


def compute_profile_hash(profile_path: Union[str, Path]) -> str:
    """Computes a SHA-256 cryptographic hash over all YAML files in the profile directory.

    Sorts file paths relative to profile_path for deterministic, reproducible hashing.
    """
    path = Path(profile_path)
    if not path.is_dir():
        raise FileNotFoundError(f"Profile directory does not exist: {profile_path}")

    yaml_files = sorted(
        [f for f in path.rglob("*") if f.is_file() and f.suffix in (".yaml", ".yml")]
    )
    if not yaml_files:
        raise ValueError(f"No YAML configuration files found in profile path: {profile_path}")

    sha256 = hashlib.sha256()
    for file_path in yaml_files:
        rel_path = file_path.relative_to(path).as_posix()
        sha256.update(rel_path.encode("utf-8"))
        with open(file_path, "rb") as f:
            sha256.update(f.read())

    return sha256.hexdigest()


class ProfileLoader:
    """Loader utility for Domain Profiles."""

    @staticmethod
    def load_profile(profile_path: Union[str, Path]) -> DomainProfile:
        """Loads and validates a complete DomainProfile from a directory."""
        path = Path(profile_path)
        if not path.exists():
            raise FileNotFoundError(f"Profile directory not found: {profile_path}")

        meta_file = path / "profile.yaml"
        topology_file = path / "topology.yaml"
        disruptions_file = path / "disruptions.yaml"

        for required_file in [meta_file, topology_file, disruptions_file]:
            if not required_file.exists():
                raise FileNotFoundError(f"Required profile file missing: {required_file}")

        with open(meta_file, "r", encoding="utf-8") as f:
            meta_data = yaml.safe_load(f)
        meta = ProfileMetaModel(**meta_data)

        with open(topology_file, "r", encoding="utf-8") as f:
            topo_data = yaml.safe_load(f)
        topology = TopologyModel(**topo_data)

        with open(disruptions_file, "r", encoding="utf-8") as f:
            disruption_data = yaml.safe_load(f)
        disruptions = DisruptionConfigModel(**disruption_data)

        agents_roster = None
        if (path / "agents.yaml").exists():
            agents_roster = load_agents_config(path)

        p_hash = compute_profile_hash(path)

        return DomainProfile(
            meta=meta,
            topology=topology,
            disruptions=disruptions,
            agents=agents_roster,
            profile_hash=p_hash,
            profile_path=path,
        )


def load_profile(profile_path: Union[str, Path]) -> DomainProfile:
    """Convenience functional interface to ProfileLoader.load_profile."""
    return ProfileLoader.load_profile(profile_path)

