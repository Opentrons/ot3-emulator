"""One-stop shop for all errors."""

from typing import List


class MountError(Exception):
    """Base mount exception."""

    ...


class NoMountsDefinedError(MountError):
    """Exception thrown when you try to load a mount and none are defined."""

    def __init__(self) -> None:
        super().__init__("You have no mounts defined.")


class MountNotFoundError(MountError):
    """Exception thrown when mount of a certain name is not found."""

    def __init__(self, name: str) -> None:
        super().__init__(f'Mount named "{name}" not found.')


class EmulationLevelNotSupportedError(Exception):
    """Exception thrown when emulation level is not supported."""
    def __init__(self, emulation_level: str, hardware: str) -> None:
        super().__init__(
            f'Emulation level, "{emulation_level}" not supported for "{hardware}"'
        )


class LocalSourceDoesNotExistError(Exception):
    """Exception thrown when local source-location does not exist."""
    def __init__(self, path: str) -> None:
        super().__init__(f'"{path}" is not a valid directory path')


class DuplicateHardwareNameError(Exception):
    """Exception thrown when there is hardware with duplicate names."""
    def __init__(self, duplicate_names: List[str]) -> None:
        super().__init__(
            "The following container names are duplicated in the configuration file: "
            f"{', '.join(duplicate_names)}"
        )


class ImageNotDefinedError(Exception):
    """Exception thrown when there is no image defined for specified emulation level/source type."""  # noqa: E501
    def __init__(
        self, emulation_level: str, source_type: str, hardware: str
    ) -> None:
        super().__init__(
            f'Image with emulation level of "{emulation_level}" and source type '
            f'"{source_type}" does not exist for {hardware}'
        )