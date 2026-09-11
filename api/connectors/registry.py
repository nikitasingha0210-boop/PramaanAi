from api.connectors.mock import (
    GSTNConnector, PANConnector, UdyamConnector, MCA21Connector,
    EPFOESICConnector, StartupIndiaConnector, NSICConnector,
    DigiLockerConnector, DebarmentConnector,
)

# This registry is the single swap point for moving from mock connectors
# to real, authorized government integrations. The rules engine only
# ever calls `registry["gstn"].lookup(...)` — it never imports a mock
# class directly — so a real connector can be dropped in here without
# touching compliance/rules.py.
registry = {
    "gstn": GSTNConnector(),
    "pan": PANConnector(),
    "udyam": UdyamConnector(),
    "mca21": MCA21Connector(),
    "epfo_esic": EPFOESICConnector(),
    "startup_india": StartupIndiaConnector(),
    "nsic": NSICConnector(),
    "digilocker": DigiLockerConnector(),
    "debarment": DebarmentConnector(),
}
