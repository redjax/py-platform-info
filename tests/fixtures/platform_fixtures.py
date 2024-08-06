import logging
from pytest import fixture
import platform

log = logging.getLogger(__name__)


@fixture
def detected_system() -> str:
    return platform.system()


@fixture
def fake_linux_system() -> str:
    return "Linux"


@fixture
def fake_windows_system() -> str:
    return "Windows"


@fixture
def fake_mac_system() -> str:
    return "Darwin"
