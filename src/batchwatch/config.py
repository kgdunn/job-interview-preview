"""Connection settings.

Everything is driven off NEO4J_BOLT_URL so the same code runs against the local
compose stack and against the shared box.
"""

import os

from neomodel import config as neomodel_config

DEFAULT_BOLT_URL = "bolt://neo4j:batchwatch1@localhost:7687"


def bolt_url() -> str:
    return os.environ.get("NEO4J_BOLT_URL", DEFAULT_BOLT_URL)


def connect() -> str:
    """Point neomodel at the database. Safe to call more than once."""
    url = bolt_url()
    neomodel_config.DATABASE_URL = url
    neomodel_config.MAX_CONNECTION_POOL_SIZE = int(
        os.environ.get("NEO4J_POOL_SIZE", "50")
    )
    return url
