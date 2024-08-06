from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
import logging
import platform as _platform
import sys
from types import ModuleType
import typing as t

log: logging.Logger = logging.getLogger(__name__)

## Control which classes, variables, and functions are available for import.
__all__: list[str] = ["PlatformInfo", "get_platform_info"]

match _platform.system():
    case "Unix" | "Linux":
        __all__.append("PlatformLinuxInfo")
    case "Darwin":
        __all__.append("PlatformMacInfo")
    case "Windows":
        __all__.append("PlatformWinInfo")
    case _:
        ## Unknown system, do not export and platform-specific classes.
        pass

## Generic type for dataclass classes
T = t.TypeVar("T")

## Valid file size strings for byte conversions
VALID_FILESIZE_UNITS: list[str] = ["B", "KB", "MB", "GB", "TB", "PB"]

############################################################
# Helper functions                                         #
# -------------------------------------------------------- #
# These functions are called by dataclass fields           #
#  when a value cannot be initialized with default_factory #
############################################################


def _set_logging_level(
    verbosity: int,
    set_debug: bool = False,
    log_fmt: str = "%(module)s |> %(message)s",
    log_fmt_debug: str = (
        "%(levelname)s | [%(asctime)s] | [logger:%(name)s] | [%(funcName)s:%(lineno)s] |> %(message)s"
    ),
) -> None:
    """Handler function to configure logging & set verbosity/debugging from CLI options."""
    ## Cap verbosity at 2
    verbosity = min(verbosity, 2)

    if verbosity > 1:
        print("Setting log level to DEBUG")
        log_level: int = logging.DEBUG
    else:
        if set_debug:
            log_level: int = logging.DEBUG
        else:
            log_levels: list[int] = [logging.WARNING, logging.INFO, logging.DEBUG]
            ## Set log level based on verbosity counter
            log_level: int = log_levels[verbosity]

    logging.basicConfig(
        level=log_level,
        format=log_fmt_debug if verbosity == 2 else log_fmt,
        datefmt="%Y-%m-%d_%H-%M-%S",
    )

    logging.getLogger().setLevel(log_level)

    log.debug(f"Logging configured")


def get_args() -> argparse.Namespace:
    """Handle CLI args for this script."""
    ## Initialize arg parser
    parser = argparse.ArgumentParser()

    ## Add debugging flag
    parser.add_argument("-d", "--debug", dest="debug", action="store_true")
    ## Add verbosity counter
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbosity",
        action="count",
        default=0,
        help="Increase verbosity level (-v, -vv, etc). Max verbosity: -vv",
    )

    options: argparse.Namespace = parser.parse_args()

    return options


@dataclass
class ConvertedBytes:
    """Store converted bytes amount & unit."""

    amount: t.Union[Decimal, int] = field(default=0.00)
    unit: str = field(default="B")

    def __post_init__(self):
        if self.unit not in VALID_FILESIZE_UNITS:
            raise ValueError(
                f"Invalid unit: {self.unit}. Must be one of {VALID_FILESIZE_UNITS}"
            )

        round_amount: Decimal = round(self.amount, 2)
        self.amount = round_amount


def convert_bytes(
    bytes: int = None, as_obj: bool = False, as_str: bool = False
) -> t.Union[ConvertedBytes, str, int]:
    """Scale bytes up to proper unit (K, M, G, T, P).

    Params:
        bytes (int): Input bytes to convert up to proper unit.

    Example:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'

    """
    if as_obj and as_str:
        raise ValueError(
            f"Cannot pass both as_obj=True and as_str=True. Please use only 1 or the other."
        )

    factor: int = 1024

    for unit in VALID_FILESIZE_UNITS:
        if bytes < factor:
            if as_str:
                return f"{bytes:.2f}{unit}"
            elif as_obj:
                return ConvertedBytes(amount=Decimal(bytes), unit=unit)
            else:
                return round(bytes, 2)
        else:
            bytes /= factor


def get_platform_info() -> PlatformInfo:
    """Entrypoint for platform info class.

    Description:
        This method initializes a `PlatformInfo` object, handling any exceptions
        and returning a PlatformInfo class where possible.
    """
    try:
        p_info: PlatformInfo = PlatformInfo()

        return p_info
    except Exception as exc:
        msg = f"({type(exc)}) Unhandled exception initializing PlatformInfo object. Details: {exc}"
        log.error(msg)

        raise exc


def get_platform_terse() -> str:
    """Return 'terse' platform info."""
    return _platform.platform(terse=True)


def get_platform_aliased() -> str:
    """Return aliased platform info (may be the same as un-aliased)."""
    return _platform.platform(aliased=True)


def get_platform_uname() -> "PlatformUname":
    """Return an initalized PlatformUname instance."""
    PlatformUname()


def get_platform_python() -> "PlatformPython":
    """Return an initalized PlatformPython instance."""
    return PlatformPython()


def get_python_path() -> list[str]:
    """Return Python's PATH."""
    return sys.path


def get_python_modules() -> t.Dict[str, ModuleType]:
    """Return Python's loaded modules."""
    return sys.modules


def get_sys_byteorder() -> str:
    """Return "big" or "little.

    "big" for big-endian (most-significant byte first) platforms.
    "little" on little-endian (least-significant byte first) platforms.
    """
    return sys.byteorder


def get_os_release() -> dict[str, str]:
    """Return Linux OS release information."""
    match _platform.system():
        case "Linux" | "Unix":
            return EnumLinux.OS_RELEASE.value
        case "Darwin":
            return EnumMac.VERSION.value
        case _:
            log.warning(
                f"Checking OS release on platform '{_platform.system()}' is not supported."
            )

            return None


def get_libc_version() -> t.Tuple[str]:
    """Return Unix system's libc version."""
    if _platform.system not in ["Linux", "Unix", "Darwin"]:
        log.warning(
            f"Checking libc version on platform '{_platform.system()}' is not supported."
        )

        return None

    try:
        libc_ver = EnumUnix.LIBC_VER.value

        return libc_ver
    except Exception as exc:
        log.warning(f"({type(exc)}) Unable to detect libc version. Details: {exc}")

        return None


def get_freedesktop_release() -> dict[str, str] | None:
    """Return Linux freedesktop version."""
    match _platform.system():
        case "Unix" | "Linux":
            return _platform.freedesktop_os_release()
        case _:
            log.warning(
                f"Getting freedesktop release on OS '{_platform.system()}' is not supported."
            )

            return None


############################################################
# Enum classes                                             #
# -------------------------------------------------------- #
# Store static values, like platform.uname().system values #
############################################################


class EnumSystemTypes(Enum):
    """Enumerate options for platform.uname().system."""

    LINUX: str = "Linux"
    MAC: str = "Darwin"
    WINDOWS: str = "Windows"
    JAVA: str = "Java"


class EnumMac(Enum):
    """Mac-specific platform info."""

    VERSION: t.Tuple[str] = _platform.mac_ver()


class EnumWin32(Enum):
    """Windows-spectific platform info."""

    VERSION: t.Tuple[str] = _platform.win32_ver()
    EDITION: str = _platform.win32_edition()
    IS_IOT: bool = _platform.win32_is_iot()


class EnumUnix(Enum):
    LIBC_VER: t.Tuple[str] = _platform.libc_ver()


class EnumLinux(Enum):
    OS_RELEASE: dict[str, str] | None = get_freedesktop_release()


#######################################
# Classes                             #
# ----------------------------------- #
# Classes to assist with initializing #
#  PlatformInfo class object.         #
#######################################


@dataclass
class DictMixin:
    """Mixin class to add "as_dict()" method to classes. Equivalent to .__dict__.

    Add a .as_dict() method to classes that inherit from this mixin. For example,
    to add .as_dict() method to a parent class, where all children inherit the .as_dict()
    function, declare parent as:

    @dataclass
    class Parent(DictMixin):
        ...

    and call like:

        p = Parent()
        p_dict = p.as_dict()
    """

    def as_dict(self: t.Generic[T]) -> dict[str, t.Any]:
        """Return dict representation of a dataclass instance."""
        try:
            return self.__dict__.copy()

        except Exception as exc:
            raise Exception(
                f"Unhandled exception converting class instance to dict. Details: {exc}"
            )


@dataclass
class PlatformUname(DictMixin):
    system: str = _platform.uname().system
    node: str = _platform.uname().node
    release: str = _platform.uname().release
    version: str = _platform.uname().version
    machine: str = _platform.uname().machine


@dataclass
class PlatformPython(DictMixin):
    """Information about the Python implementation for the platform."""

    build: t.Tuple[str, str] = field(default_factory=_platform.python_build)
    compiler: str = field(default_factory=_platform.python_compiler)
    branch: str = field(default_factory=_platform.python_branch)
    implementation: str = field(default_factory=_platform.python_implementation)
    revision: str = field(default_factory=_platform.python_revision)
    version: str = field(default_factory=_platform.python_version)
    version_tuple: t.Tuple[str, str, str] = field(
        default_factory=_platform.python_version_tuple
    )
    path: t.List[str] = field(default_factory=get_python_path)
    modules: t.Dict[str, ModuleType] = field(default_factory=get_python_modules)
    base_prefix: str = field(default=sys.base_prefix)
    exec_prefix: str = field(default=sys.exec_prefix)
    copyright: str = field(default=sys.copyright)
    dont_write_bytecode: bool = field(default=sys.dont_write_bytecode)
    executable: str = field(default=sys.executable)
    flags: t.Tuple[t.Union[int, bool]] = field(default=sys.flags)
    float_info: t.Tuple[t.Union[int, float]] = field(default=sys.float_info)
    default_encoding: str = field(default_factory=sys.getdefaultencoding)
    int_max_str_digits: int = field(default_factory=sys.get_int_max_str_digits)
    recursion_limit: int = field(default_factory=sys.getrecursionlimit)
    maxsize: int = field(default=sys.maxsize)
    maxunicode: int = field(default=sys.maxunicode)


@dataclass
class PlatformSpecificInfo(DictMixin):
    """Base class for platform-specific (i.e. Windows, Mac, Linux) info.

    Description:
        Some of the platform module's functions are only available when a
        specific platform is detected. This class serves as a base for
        platform-specific "extra" data.

    """

    os: str = field(default_factory=_platform.system)


@dataclass
class PlatformWinInfo(PlatformSpecificInfo):
    """Windows-specific platform info."""

    win32_ver: t.Tuple = field(default=EnumWin32.VERSION.value)
    win32_edition: str = field(default=EnumWin32.EDITION.value)
    win32_is_iot: bool = field(default=EnumWin32.IS_IOT.value)


@dataclass
class PlatformUnixInfoBase(PlatformSpecificInfo):
    """Unix-specific platform info."""

    libc_ver: t.Tuple[str] = field(default=get_libc_version)


@dataclass
class PlatformMacInfo(PlatformUnixInfoBase):
    """Mac-specific platform info."""

    mac_ver: t.Tuple[str] = field(default=get_os_release)


@dataclass
class PlatformLinuxInfo(PlatformUnixInfoBase):
    """Linux-specific platform info."""

    os_release: dict[str, str] = field(default_factory=get_os_release)


######################
# PlatformInfo Class #
######################


@dataclass
class PlatformInfoBase(DictMixin):
    """Base class for platform information.

    Description:
        Compile platform data common across all OSes to serve as a base for
        building platform-specific classes.
    """

    platform: str = field(default_factory=_platform.platform)
    platform_terse: str = field(default=get_platform_terse)
    platform_aliased: str = field(default=get_platform_aliased)
    machine: str = field(default_factory=_platform.machine)
    system: str = field(default_factory=_platform.system)
    release: str = field(default_factory=_platform.release)
    version: str = field(default_factory=_platform.version)
    processor: str | None = field(default_factory=_platform.processor)
    arch: t.Tuple[str, str] = field(default_factory=_platform.architecture)
    uname: PlatformUname = field(default_factory=get_platform_uname)
    python: PlatformPython = field(default_factory=get_platform_python)
    byteorder: str = field(default_factory=get_sys_byteorder)

    def is_linux(self) -> bool:
        if self.system == EnumSystemTypes.LINUX.value:
            return True
        else:
            return False

    def is_unix(self) -> bool:
        if self.system in [EnumSystemTypes.LINUX.value, EnumSystemTypes.MAC.value]:
            return True
        else:
            return False

    def is_win(self) -> bool:
        if self.system == EnumSystemTypes.WINDOWS.value:
            return True
        else:
            return False

    def is_mac(self) -> bool:
        if self.system == EnumSystemTypes.MAC.value:
            return True
        else:
            return False

    def is_java(self) -> bool:
        if self.system == EnumSystemTypes.JAVA.value:
            return True
        else:
            return False

    def is_32bit(self) -> bool:
        if "32bit" in self.arch:
            return True
        else:
            return False

    def is_64bit(self) -> bool:
        if "64bit" in self.arch:
            return True
        else:
            return False


@dataclass
class PlatformInfo(PlatformInfoBase):
    """Compile information about the OS running this script."""

    @property
    def platform_specific_info(
        self,
    ) -> t.Union[PlatformWinInfo, PlatformMacInfo, PlatformMacInfo]:
        """Detect OS and return platform-specific class with additional platform info."""
        match self.system:
            case EnumSystemTypes.LINUX.value:
                platform_extra: PlatformLinuxInfo = PlatformLinuxInfo()
            case EnumSystemTypes.WINDOWS.value:
                platform_extra: PlatformWinInfo = PlatformWinInfo()
            case EnumSystemTypes.MAC.value:
                platform_extra: PlatformMacInfo = PlatformMacInfo()
            case _:
                log.error(f"Unknown OS: {self.system}")

                return f"<UNKNOWN_OS:'{self.system}'>"

        return platform_extra


def main(options: argparse.Namespace):
    platform_info: PlatformInfo = get_platform_info()

    if options.verbosity > 1:
        log.debug(f"Platform info:")
        log.debug(platform_info)

        log.debug(f"Platform specific info for OS: {_platform.system()}")
        log.debug(platform_info.platform_specific_info)
    else:
        print(f"Platform info initialized")


if __name__ == "__main__":
    options: argparse.Namespace = get_args()

    _set_logging_level(verbosity=options.verbosity, set_debug=options.debug)

    main(options=options)
