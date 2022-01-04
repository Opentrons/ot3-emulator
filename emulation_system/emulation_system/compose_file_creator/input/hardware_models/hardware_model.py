"""Parent class for all hardware."""
from __future__ import annotations

import os
from typing import (
    Any,
    Dict,
    Union,
)

from pydantic import (
    BaseModel,
    Field,
    validator,
)

from emulation_system.compose_file_creator.settings.config_file_settings import (
    DirectoryMount,
    EmulationLevels,
    Mount,
    FileMount,
    SourceRepositories,
    SourceType,
)


class NoMountsDefinedException(Exception):
    """Exception thrown when you try to load a mount and none are defined."""

    pass


class HardwareModel(BaseModel):
    """Parent class of all hardware. Define attributes common to all hardware."""

    id: str = Field(..., regex=r"^[a-zA-Z0-9-_]+$")
    hardware: str
    source_type: SourceType = Field(alias="source-type")
    source_location: str = Field(alias="source-location")
    mounts: List[Union[FileMount, DirectoryMount]] = Field(
        alias="extra-mounts", default={}
    )

    source_repos: SourceRepositories = NotImplemented
    emulation_level: EmulationLevels = NotImplemented

    class Config:
        """Config class used by pydantic."""

        allow_population_by_field_name = True
        validate_assignment = True
        use_enum_values = True
        extra = "forbid"

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self._post_init()

    def _post_init(self) -> None:
        """Methods to always run after initialization."""
        self._add_source_bind_mount()

    def _add_source_bind_mount(self) -> None:
        """If running a local type image add the mount to the mounts attribute."""
        if self.source_type == SourceType.LOCAL:
            self.mounts.append(
                DirectoryMount(
                    type="directory",
                    source_path=self.source_location,
                    mount_path=f"/{self.get_source_repo()}",
                )
            )

    @validator("source_location")
    def check_source_location(cls, v: str, values: Dict[str, Any]) -> str:
        """If source type is local, confirms directory path specified exists."""
        if values["source_type"] == SourceType.LOCAL:
            assert os.path.isdir(v), f'"{v}" is not a valid directory path'
        return v

    def get_mount_by_name(self, name: str) -> Mount:
        """Lookup and return Mount by name."""
        if len(self.mounts) == 0:
            raise NoMountsDefinedException("You have no mounts defined.")
        else:
            return self.mounts[name]


    def get_mount_strings(self) -> List[str]:
        """Get list of all mount strings for hardware."""
        mounts = [mount.get_bind_mount_string() for mount in list(self.mounts)]
        return mounts
