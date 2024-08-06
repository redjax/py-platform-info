from __future__ import annotations

import importlib.util
import logging
import logging.config
import logging.handlers
import os
from pathlib import Path
import platform
import shutil

import nox

## Set nox options
if importlib.util.find_spec("uv"):
    nox.options.default_venv_backend = "uv|virtualenv"
else:
    nox.options.default_venv_backend = "virtualenv"
nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_external_run = False
nox.options.error_on_missing_interpreters = False
# nox.options.report = True

## Define sessions to run when no session is specified
nox.sessions = ["lint", "export", "tests"]

## Detect container env, or default to False
if "CONTAINER_ENV" in os.environ:
    CONTAINER_ENV: bool = os.environ["CONTAINER_ENV"]
else:
    CONTAINER_ENV: bool = False

## Create logger for this module
log: logging.Logger = logging.getLogger("nox")

## Define versions to test
PY_VERSIONS: list[str] = ["3.12", "3.11"]
## Get tuple of Python ver ('maj', 'min', 'mic')
PY_VER_TUPLE: tuple[str, str, str] = platform.python_version_tuple()
## Dynamically set Python version
DEFAULT_PYTHON: str = f"{PY_VER_TUPLE[0]}.{PY_VER_TUPLE[1]}"

## Set PDM version to install throughout
PDM_VER: str = "2.15.4"
## Set paths to lint with the lint session
LINT_PATHS: list[str] = ["platform_info.py", "tests"]


def setup_nox_logging(
    level_name: str = "DEBUG", disable_loggers: list[str] | None = []
) -> None:
    """Configure a logger for the Nox module.

    Params:
        level_name (str): The uppercase string repesenting a logging logLevel.
        disable_loggers (list[str] | None): A list of logger names to disable, i.e. for 3rd party apps.
            Note: Disabling means setting the logLevel to `WARNING`, so you can still see errors.

    """
    ## If container environment detected, default to logging.DEBUG
    if CONTAINER_ENV:
        level_name: str = "DEBUG"

    logging_config: dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "loggers": {
            "nox": {
                "level": level_name.upper(),
                "handlers": ["console"],
                "propagate": False,
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "nox",
                "level": "DEBUG",
                "stream": "ext://sys.stdout",
            }
        },
        "formatters": {
            "nox": {
                "format": "[NOX] [%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
                "datefmt": "%Y-%m-%D %H:%M:%S",
            }
        },
    }

    ## Configure logging. Only run this once in an application
    logging.config.dictConfig(config=logging_config)

    ## Disable loggers by name. Sets logLevel to logging.WARNING to suppress all but warnings & errors
    for _logger in disable_loggers:
        logging.getLogger(_logger).setLevel(logging.WARNING)


def append_lint_paths(
    search_patterns: str | list[str] = None, lint_paths: list[str] = None
):
    if lint_paths is None:
        lint_paths = []

    if search_patterns is None:
        return lint_paths

    if isinstance(search_patterns, str):
        search_patterns = [search_patterns]

    for pattern in search_patterns:
        for path in Path(".").rglob(pattern):
            relative_path = (
                Path(".").joinpath(path).resolve().relative_to(Path(".").resolve())
            )

            if f"{relative_path}" not in lint_paths:
                lint_paths.append(f"./{relative_path}")

    log.debug(f"Lint paths: {lint_paths}")
    return lint_paths


setup_nox_logging()

log.info(f"[container_env:{CONTAINER_ENV}]")


@nox.session(python=[DEFAULT_PYTHON], name="lint", tags=["quality"])
def run_linter(session: nox.Session):
    session.install("ruff")
    session.install("black")

    log.info("Linting code")
    for d in LINT_PATHS:
        if not Path(d).exists():
            log.warning(f"Skipping lint path '{d}', could not find path")
            pass
        else:
            lint_path: Path = Path(d)
            log.info(f"Running ruff imports sort on '{d}'")
            session.run(
                "ruff",
                "check",
                lint_path,
                "--select",
                "I",
                "--fix",
            )

            log.info(f"Formatting '{d}' with Black")
            session.run(
                "black",
                lint_path,
            )

            log.info(f"Running ruff checks on '{d}' with --fix")
            session.run(
                "ruff",
                "check",
                lint_path,
                "--fix",
            )

    log.info("Linting noxfile.py")
    session.run(
        "ruff",
        "check",
        f"{Path('./noxfile.py')}",
        "--fix",
    )


@nox.session(python=PY_VERSIONS, name="tests", tags=["test"])
def run_tests(session: nox.Session):
    session.install("-r", "requirements.txt")

    log.info("Running Pytest tests")

    session.run(
        "pytest",
        "-n",
        "auto",
        "--tb=auto",
        "-v",
        "-rsXxfP",
    )


@nox.session(python=PY_VERSIONS, name="pre-commit-all", tags=["repo", "pre-commit"])
def run_pre_commit_all(session: nox.Session):
    session.install("pre-commit")
    session.run("pre-commit")

    log.info("Running all pre-commit hooks")
    session.run("pre-commit", "run")


@nox.session(python=PY_VERSIONS, name="pre-commit-update", tags=["repo", "pre-commit"])
def run_pre_commit_autoupdate(session: nox.Session):
    session.install(f"pre-commit")

    log.info("Running pre-commit autoupdate")
    session.run("pre-commit", "autoupdate")


@nox.session(
    python=PY_VERSIONS, name="pre-commit-nbstripout", tags=["repo", "pre-commit"]
)
def run_pre_commit_nbstripout(session: nox.Session):
    session.install(f"pre-commit")

    log.info("Running nbstripout pre-commit hook")
    session.run("pre-commit", "run", "nbstripout")
