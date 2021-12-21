"""Models for configuration_settings.json file."""

from __future__ import annotations
import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, parse_obj_as


class ConfigurationFileNotFoundError(FileNotFoundError):
    """Error thrown when config file is not found."""

    pass


class DefaultFolderPaths(BaseModel):
    """Default folder paths to find repos at."""

    opentrons: Optional[str]
    ot3_firmware: Optional[str] = Field(alias="ot3-firmware")
    modules: Optional[str]


class GlobalSettings(BaseModel):
    """Settings that affect all sections in config file."""

    default_folder_paths: DefaultFolderPaths = Field(..., alias="default-folder-paths")


class Heads(BaseModel):
    """Where to download the head of the repos from."""

    opentrons: str
    ot3_firmware: str = Field(..., alias="ot3-firmware")
    modules: str


class Commits(BaseModel):
    """Format string for where to download a specific commit sha from."""

    opentrons: str
    ot3_firmware: str = Field(..., alias="ot3-firmware")
    modules: str


class SourceDownloadLocations(BaseModel):
    """Model representing where to download source code from."""

    heads: Heads
    commits: Commits


class EmulationSettings(BaseModel):
    """All settings related to `em` command."""

    source_download_locations: SourceDownloadLocations = Field(
        ..., alias="source-download-locations"
    )


class SharedFolder(BaseModel):
    """Model for a shared folder. Will map host_path to vm_path."""

    host_path: str = Field(..., alias="host-path")
    vm_path: str = Field(..., alias="vm-path")


class VirtualMachineSettings(BaseModel):
    """All settings related to vm command."""

    dev_vm_name: str = Field(..., alias="dev-vm-name")
    prod_vm_name: str = Field(..., alias="prod-vm-name")
    vm_memory: int = Field(..., alias="vm-memory")
    vm_cpus: int = Field(..., alias="vm-cpus")
    num_socket_can_networks: int = Field(..., alias="num-socket-can-networks")
    shared_folders: List[str] = Field(alias="shared-folders", default=[])


class OpentronsEmulationConfiguration(BaseModel):
    """Model representing entire configuration file."""

    global_settings: GlobalSettings = Field(..., alias="global-settings")
    emulation_settings: EmulationSettings = Field(..., alias="emulation-settings")
    virtual_machine_settings: VirtualMachineSettings = Field(
        ..., alias="virtual-machine-settings"
    )
    aws_ecr_settings: Dict[str, Any] = Field(..., alias="aws-ecr-settings")

    @classmethod
    def from_file_path(cls, json_file_path: str) -> OpentronsEmulationConfiguration:
        """Parse file in OpentronsEmulationConfiguration object."""
        try:
            file = open(json_file_path, "r")
        except FileNotFoundError:
            raise ConfigurationFileNotFoundError(
                f"\nError loading configuration file.\n"
                f"Configuration file not found at: {json_file_path}\n"
                f"Please create a JSON configuration file"
            )

        return parse_obj_as(cls, json.load(file))