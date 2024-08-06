import logging
import sys
import os
import typing as t
import platform
from decimal import Decimal
from pytest import mark

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import platform_info

log = logging.getLogger(__name__)


@mark.xfail
def test_expect_fail(detected_system: str):
    assert detected_system is None


@mark.xfail
@mark.platform
def test_fail_platform_system(detected_system: str):
    assert detected_system == "Force test failure", ValueError("This test should fail")


@mark.xfail
def test_fail_get_full_platform_info():

    plat: platform_info.PlatformInfo = platform_info.get_platform_info()

    assert plat.system == "Force test failure", ValueError("This test should fail")


@mark.platform
def test_get_full_platform_info():
    log.info("Getting full PlatformInfo()")

    try:
        plat: platform_info.PlatformInfo = platform_info.get_platform_info()

        assert plat, ValueError("'plat' should be an instance of PlatformInfo().")
        assert isinstance(plat, platform_info.PlatformInfo), TypeError(
            f"Invalid type for 'plat': ({type(plat)}). Should have been a platform_info.PlatformInfo class."
        )

    except Exception as exc:
        msg = (
            f"({type(exc)}) Unhandled exception getting PlatformInfo(). Details: {exc}"
        )
        log.error(msg)

        raise exc


@mark.xfail
def test_fail_platform_ascii():
    plat: platform_info.PlatformInfo = platform_info.get_platform_info()

    _art = plat.ascii_art
    assert _art == "Force test failure", ValueError("This test should fail")


@mark.platform
def test_platform_ascii():
    log.info("Getting full PlatformInfo()")

    try:
        plat: platform_info.PlatformInfo = platform_info.get_platform_info()

        assert plat, ValueError("'plat' should be an instance of PlatformInfo().")
        assert isinstance(plat, platform_info.PlatformInfo), TypeError(
            f"Invalid type for 'plat': ({type(plat)}). Should have been a platform_info.PlatformInfo class."
        )

    except Exception as exc:
        msg = (
            f"({type(exc)}) Unhandled exception getting PlatformInfo(). Details: {exc}"
        )
        log.error(msg)

        raise exc

    log.debug(f"Displaying ASCII art for platform")
    log.debug(f"\n{plat.ascii_art}")


@mark.xfail
def test_fail_convert_bytes_int(ten_mb_bytes: int):
    _converted = platform_info.convert_bytes(bytes=ten_mb_bytes)

    assert isinstance(_converted, int), TypeError("This test should fail")


@mark.platform
def test_convert_bytes_int(ten_mb_bytes: int):
    _converted = platform_info.convert_bytes(bytes=ten_mb_bytes)
    assert _converted, ValueError("Missing Pytest fixture containing 10MB in bytes.")
    assert isinstance(_converted, int) or isinstance(_converted, float), TypeError(
        f"Invalid type for converted bytes. Should have been an int or float, got type: ({type(_converted)})"
    )

    log.debug(f"Converted {ten_mb_bytes} bytes to: {_converted}")


@mark.xfail
def test_fail_convert_bytes_obj(ten_mb_bytes: int):
    _converted = platform_info.convert_bytes(bytes=ten_mb_bytes, as_obj=True)

    assert _converted.amount == 150000, ValueError("This test should fail")


@mark.platform
def test_convert_bytes_obj(ten_mb_bytes: int):
    _converted = platform_info.convert_bytes(bytes=ten_mb_bytes, as_obj=True)

    assert _converted, ValueError("Missing Pytest fixture containing 10MB in bytes.")
    assert isinstance(_converted, platform_info.ConvertedBytes), TypeError(
        f"Invalid type for converted bytes. Should have been a platform_info.ConvertedBytes object, got type: ({type(_converted)})"
    )

    log.debug(f"Converted {ten_mb_bytes} bytes to: {_converted}")


@mark.xfail
def test_fail_convert_bytes_str(ten_mb_bytes: int):
    _converted = platform_info.convert_bytes(bytes=ten_mb_bytes, as_str=True)

    assert isinstance(_converted, int), ValueError("This test should fail")


@mark.platform
def test_convert_bytes_str(ten_mb_bytes: int):
    _converted = platform_info.convert_bytes(bytes=ten_mb_bytes, as_str=True)
    assert _converted, ValueError("Missing Pytest fixture containing 10MB in bytes.")
    assert isinstance(_converted, str), TypeError(
        f"Invalid type for converted bytes. Should have been a str, got type: ({type(_converted)})"
    )

    log.debug(f"Converted {ten_mb_bytes} bytes to: {_converted}")


@mark.xfail
def test_fail_get_cpu_count():
    cpu_count = platform_info.get_cpu_count()

    assert cpu_count < 0, ValueError("This test should fail")


@mark.platform
def test_get_cpu_count():
    cpu_count = platform_info.get_cpu_count()

    assert cpu_count, ValueError("'cpu_count' should not have been None.")
    assert isinstance(cpu_count, int), TypeError(
        f"'cpu_count' should be of type int, got type: ({type(cpu_count)})"
    )

    log.debug(f"CPU count: {cpu_count}")


@mark.xfail
def test_fail_platform_terse():
    platform_terse = platform_info.get_platform_terse()

    assert platform_terse == "Force test fail", ValueError("This test should fail")


@mark.platform
def test_platform_terse():
    platform_terse = platform_info.get_platform_terse()

    assert platform_terse, ValueError("'platform_terse' should not have been None")
    assert isinstance(platform_terse, str), TypeError(
        f"'platform_terse' should be a str, got type: ({type(platform_terse)})"
    )

    log.debug(f"Platform terse: {platform_terse}")


@mark.xfail
def test_fail_platform_aliased():
    platform_aliased = platform_info.get_platform_aliased()

    assert platform_aliased == "Force test fail", ValueError("This test should fail")


@mark.platform
def test_platform_aliased():
    platform_aliased = platform_info.get_platform_terse()

    assert platform_aliased, ValueError("'platform_aliased' should not have been None")
    assert isinstance(platform_aliased, str), TypeError(
        f"'platform_aliased' should be a str, got type: ({type(platform_aliased)})"
    )

    log.debug(f"Platform aliased: {platform_aliased}")


@mark.xfail
def test_fail_platform_uname():
    platform_uname = platform_info.get_platform_uname()

    assert isinstance(platform_uname, str), TypeError("This test should fail")


@mark.platform
def test_platform_uname():
    platform_uname = platform_info.get_platform_uname()

    assert platform_uname, ValueError("'platform_uname' should not have been None")
    assert isinstance(platform_uname, platform_info.PlatformUname), TypeError(
        f"'platform_uname' should be a platform_info.PlatformUname object. Got type: ({type(platform_uname)})"
    )

    log.debug(f"Platform uname: {platform_uname}")


@mark.xfail
def test_fail_platform_python():
    platform_python = platform_info.get_platform_python()

    assert isinstance(platform_python, str), TypeError("This test should fail")


@mark.platform
def test_platform_python():
    platform_python = platform_info.get_platform_python()

    assert platform_python, ValueError("'platform_python' should not have been None")
    assert isinstance(platform_python, platform_info.PlatformPython), TypeError(
        f"'platform_python' should be a platform_info.PlatformPython object. Got type: ({type(platform_python)})"
    )

    msg: str = f"""Implementation: {platform_python.implementation}
Version: {platform_python.version}
Build: {platform_python.build}
Executable location: {platform_python.exec_prefix}
"""

    log.debug(f"Detected Python:\n{msg}")


@mark.xfail
def test_fail_platform_os_release(detected_system: str):
    platform_os_release = platform_info.get_os_release()

    if detected_system == "Windows":
        assert platform_os_release is not None, ValueError("This test should fail")
    else:
        assert isinstance(platform_os_release, int), TypeError("This test should fail")


@mark.platform
def test_platform_os_release(detected_system: str):
    platform_os_release = platform_info.get_os_release()

    if platform_os_release is None:
        log.warning(f"OS release info for system '{detected_system}' is not supported.")

    else:
        assert isinstance(platform_os_release, dict), TypeError(
            f"'platform_os_release' should be a dict, got type: ({type(platform_os_release)})"
        )

    log.debug(f"Platform OS release: {platform_os_release}")


@mark.xfail
def test_fail_platform_libc_version(detected_system: str):
    platform_libc_version = platform_info.get_libc_version()

    if detected_system == "Windows":
        assert platform_libc_version is not None, ValueError("This test should fail")
    else:
        assert isinstance(platform_libc_version, str), TypeError(
            "This test should fail"
        )


@mark.platform
def test_platform_libc_version(detected_system: str):
    platform_libc_version = platform_info.get_libc_version()

    if platform_libc_version is None:
        log.warning(
            f"LIBC version info for system '{detected_system}' is not supported."
        )

    else:
        assert isinstance(platform_libc_version, t.Tuple), TypeError(
            f"'platform_libc_version' should be a tuple, got type: ({type(platform_libc_version)})"
        )

    log.debug(f"Platform LIBC version: {platform_libc_version}")
