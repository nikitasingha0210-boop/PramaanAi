"""
Common normalized connector interface.

Every government data source — GSTN, Udyam, PAN, MCA21, EPFO, ESIC,
DPIIT/Startup India, NSIC, DigiLocker, the Blacklisting/Debarment
registry — implements this same interface so the compliance/rules
engine never needs to know which underlying source it is talking to.

These are MOCK connectors built for the prototype. They do not call any
live government system. The `registry` module is the intended swap
point: replacing a mock with a real, authorized integration means
implementing this same `Connector` protocol and registering it, with
no changes required in the rules engine.
"""
from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class ConnectorResponse:
    found: bool
    source: str                     # e.g. "GSTN Mock API"
    fields: dict = field(default_factory=dict)   # normalized field -> value
    confidence: float = 0.0         # 0-1, how confident the source is in this record
    as_of: str | None = None        # ISO timestamp the mock portal record represents
    raw_note: str | None = None     # human-readable note about the mock condition


class Connector(Protocol):
    name: str

    def lookup(self, identifier: str, context: dict | None = None) -> ConnectorResponse:
        ...
