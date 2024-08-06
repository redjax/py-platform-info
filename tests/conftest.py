from __future__ import annotations

import logging

import pytest

## Configure logging for test modules
logging.basicConfig(
    level="DEBUG",
    format="%(levelname)s | [%(asctime)s] | [logger:%(name)s] |> %(message)s",
    datefmt="%Y-%m-%d_%H:%M:%S",
)

## Add pytest fixtures
pytest_plugins = ["fixtures.platform_fixtures", "fixtures.misc_fixtures"]
