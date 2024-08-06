import logging
from pytest import fixture

log = logging.getLogger(__name__)


@fixture
def ten_mb_bytes() -> int:
    return 10485760
