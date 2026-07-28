"""Constants and enumerations for SCOF simulation service."""

from enum import Enum


class Prefix:
    MANUFACTURER = "mfg-"
    SUPPLIER = "sup-"
    WAREHOUSE = "wh-"
    DISTRIBUTION_CENTER = "dc-"
    PRODUCT = "prod-"
    ROUTE = "route-"
    RUN = "run-"
    SCENARIO = "scen-"
    PURCHASE_ORDER = "po-"
    SHIPMENT = "ship-"
    DISRUPTION = "disrupt-"


class OrderStatus(str, Enum):
    PLACED = "PLACED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    DELAYED = "DELAYED"
    CANCELLED = "CANCELLED"


class ShipmentStatus(str, Enum):
    DISPATCHED = "DISPATCHED"
    IN_TRANSIT = "IN_TRANSIT"
    ARRIVED = "ARRIVED"
    DELAYED = "DELAYED"


class DisruptionStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"


class TransportMode(str, Enum):
    SEA = "sea"
    AIR = "air"
    ROAD = "road"
    RAIL = "rail"


GENERATOR_VERSION = "1.0.0"
