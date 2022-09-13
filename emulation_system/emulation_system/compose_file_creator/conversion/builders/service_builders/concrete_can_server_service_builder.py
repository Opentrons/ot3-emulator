from typing import Optional

from emulation_system.compose_file_creator.errors import (
    HardwareDoesNotExistError,
    IncorrectHardwareError,
)
from emulation_system.compose_file_creator.input.configuration_file import (
    SystemConfigurationModel,
)
from emulation_system.compose_file_creator.output.compose_file_model import BuildItem
from emulation_system.compose_file_creator.settings.config_file_settings import (
    Hardware,
    OpentronsRepository,
    SourceType,
)
from emulation_system.compose_file_creator.settings.images import CANServerImages
from emulation_system.logging.can_server_logging_client import CANServerLoggingClient
from emulation_system.opentrons_emulation_configuration import (
    OpentronsEmulationConfiguration,
)

from ...intermediate_types import (
    Command,
    DependsOn,
    EnvironmentVariables,
    Ports,
    RequiredNetworks,
    Volumes,
)
from ...service_creation.shared_functions import (
    add_opentrons_named_volumes,
    get_build_args,
    get_entrypoint_mount_string,
    get_service_build,
)
from .abstract_service_builder import AbstractServiceBuilder


class ConcreteCANServerServiceBuilder(AbstractServiceBuilder):

    CAN_SERVER_NAME = "can-server"
    NO_BUILD_ARGS_REASON = 'can-server-source-type is "local"'
    BUILD_ARGS_REASON = 'can-server-source-type is "remote"'

    def __init__(
        self,
        config_model: SystemConfigurationModel,
        global_settings: OpentronsEmulationConfiguration,
        dev: bool,
    ) -> None:
        super().__init__(config_model, global_settings)
        self._logging_client = CANServerLoggingClient()
        self._logging_client.log_header("CAN Server")
        self._dev = dev
        self._ot3 = self._get_ot3(config_model)
        self._image = self._generate_image()

    @staticmethod
    def _get_ot3(config_model: SystemConfigurationModel):
        ot3 = config_model.robot
        if ot3 is None:
            raise HardwareDoesNotExistError(Hardware.OT3)
        if ot3.hardware != Hardware.OT3:
            raise IncorrectHardwareError(ot3.hardware, Hardware.OT3)

        return ot3

    def _generate_image(self) -> str:
        source_type = self._ot3.can_server_source_type
        image_name = (
            CANServerImages().local_firmware_image_name
            if source_type == SourceType.LOCAL
            else CANServerImages().remote_firmware_image_name
        )
        self._logging_client.log_image_name(image_name, source_type)
        return image_name

    def generate_container_name(self) -> str:
        system_unique_id = self._config_model.system_unique_id
        container_name = super()._generate_container_name(
            self.CAN_SERVER_NAME, system_unique_id
        )
        self._logging_client.log_container_name(container_name, system_unique_id)
        return container_name

    def generate_image(self) -> str:
        return self._image

    def is_tty(self) -> bool:
        tty = True
        self._logging_client.log_tty(tty)
        return tty

    def generate_networks(self) -> RequiredNetworks:
        networks = self._config_model.required_networks
        self._logging_client.log_networks(networks)
        return networks

    def generate_build(self) -> Optional[BuildItem]:
        repo = OpentronsRepository.OPENTRONS
        if self._ot3.can_server_source_type == SourceType.REMOTE:
            build_args = get_build_args(
                repo,
                self._ot3.can_server_source_location,
                self._global_settings.get_repo_commit(repo),
                self._global_settings.get_repo_head(repo),
            )

        else:
            build_args = None
        self._logging_client.log_build(build_args)
        return get_service_build(self._image, build_args, self._dev)

    def generate_volumes(self) -> Optional[Volumes]:
        if self._ot3.can_server_source_type == SourceType.LOCAL:
            volumes = [get_entrypoint_mount_string()]
            volumes.extend(self._ot3.get_can_mount_strings())
            add_opentrons_named_volumes(volumes)
        else:
            volumes = None
        self._logging_client.log_volumes(volumes)
        return volumes

    def generate_command(self) -> Optional[Command]:
        command = None
        self._logging_client.log_command(command)
        return command

    def generate_ports(self) -> Optional[Ports]:
        ports = self._ot3.get_can_server_bound_port()
        self._logging_client.log_ports(ports)
        return ports

    def generate_depends_on(self) -> Optional[DependsOn]:
        depends_on = None
        self._logging_client.log_depends_on(depends_on)
        return depends_on

    def generate_env_vars(self) -> Optional[EnvironmentVariables]:
        env_vars = None
        self._logging_client.log_env_vars(env_vars)
        return env_vars
