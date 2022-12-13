"""Module containing ConcreteOT3ServiceBuilder class."""
from typing import Optional

from emulation_system import OpentronsEmulationConfiguration, SystemConfigurationModel
from emulation_system.compose_file_creator.types.intermediate_types import (
    IntermediateBuildArgs,
    IntermediateCommand,
    IntermediateDependsOn,
    IntermediateEnvironmentVariables,
    IntermediateHealthcheck,
    IntermediateNetworks,
    IntermediatePorts,
    IntermediateVolumes,
)

from ...config_file_settings import OT3Hardware
from ...images import LocalOT3FirmwareBuilderImage
from ...utilities.shared_functions import get_build_args
from .abstract_service_builder import AbstractServiceBuilder


class ConcreteLocalOT3FirmwareBuilderBuilder(AbstractServiceBuilder):
    """Concrete implementation of AbstractServiceBuilder for building local-ot3-firmware-builder Service."""

    IMAGE_NAME = "local-ot3-firmware-builder"
    CONTAINER_NAME = IMAGE_NAME

    def __init__(
        self,
        config_model: SystemConfigurationModel,
        global_settings: OpentronsEmulationConfiguration,
        dev: bool,
    ) -> None:
        """Instantiates a ConcreteOT3ServiceBuilder object."""
        super().__init__(config_model, global_settings, dev)
        self._ot3 = self.get_ot3(self._config_model)

    @property
    def _image(self) -> str:
        return LocalOT3FirmwareBuilderImage().image_name

    def generate_container_name(self) -> str:
        """Generates value for container_name parameter."""
        system_unique_id = self._config_model.system_unique_id
        container_name = super()._generate_container_name(
            self.CONTAINER_NAME, system_unique_id
        )
        return container_name

    def generate_image(self) -> str:
        """Generates value for image parameter."""
        return self.IMAGE_NAME

    def is_tty(self) -> bool:
        """Generates value for tty parameter."""
        return True

    def generate_networks(self) -> IntermediateNetworks:
        """Generates value for networks parameter."""
        networks = self._config_model.required_networks
        return networks

    def generate_healthcheck(self) -> Optional[IntermediateHealthcheck]:
        """Check to see if ot3-firmware and monorepo exist."""
        return IntermediateHealthcheck(
            interval=10,
            retries=6,
            timeout=10,
            command="(cd /ot3-firmware) && (cd /opentrons)",
        )

    def generate_build_args(self) -> Optional[IntermediateBuildArgs]:
        """Generates value for build parameter."""
        build_args: IntermediateBuildArgs = {}
        if self._ot3_source.is_remote():
            ot3_firmware_build_args = get_build_args(
                self._ot3_source, self._global_settings
            )
            build_args.update(ot3_firmware_build_args)

        if self._monorepo_source.is_remote():
            monorepo_build_args = get_build_args(
                self._monorepo_source, self._global_settings
            )
            build_args.update(monorepo_build_args)

        return build_args if len(build_args) > 0 else None

    def generate_volumes(self) -> Optional[IntermediateVolumes]:
        """Generates value for volumes parameter."""
        return [
            member.generate_executable_storage_volume_string()
            for member in OT3Hardware.__members__.values()
        ] + [self.ENTRYPOINT_MOUNT_STRING]

    def generate_command(self) -> Optional[IntermediateCommand]:
        """Generates value for command parameter."""
        return None

    def generate_ports(self) -> Optional[IntermediatePorts]:
        """Generates value for ports parameter."""
        return None

    def generate_depends_on(self) -> Optional[IntermediateDependsOn]:
        """Generates value for depends_on parameter."""
        return None

    def generate_env_vars(self) -> Optional[IntermediateEnvironmentVariables]:
        """Generates value for environment parameter."""
        return None
