from pathlib import Path

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Engine


def schema_is_current(engine: Engine, alembic_ini: Path) -> bool:
    config = Config(str(alembic_ini))
    script = ScriptDirectory.from_config(config)
    expected_heads = set(script.get_heads())
    if len(expected_heads) != 1:
        return False
    with engine.connect() as connection:
        current_heads = set(MigrationContext.configure(connection).get_current_heads())
    return current_heads == expected_heads
