"""Pure functions related to creating Service objects from definitions in input file."""

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
    cast,
)

from emulation_system.compose_file_creator.conversion.intermediate_types import (
    RequiredNetworks,
)
from .shared_functions import (
    generate_container_name,
    get_service_build,
    get_service_image,
)
from emulation_system.compose_file_creator.input.configuration_file import (
    SystemConfigurationModel,
)
from emulation_system.compose_file_creator.input.hardware_models import (
    ModuleInputModel,
    OT3InputModel,
    RobotInputModel,
)
from emulation_system.compose_file_creator.output.compose_file_model import (
    ListOrDict,
    Port,
    Service,
    Volume1,
)
from emulation_system.compose_file_creator.settings.custom_types import Containers


def _get_service_depends_on(
    container: Containers, emulator_proxy_name: Optional[str]
) -> Optional[List[str]]:
    # If emulator proxy exists and container is module then it needs to
    # depend on emulator proxy.
    return (
        [emulator_proxy_name]
        if emulator_proxy_name is not None
        and issubclass(container.__class__, ModuleInputModel)
        else None
    )


def _get_command(
    container: Containers, emulator_proxy_name: Optional[str]
) -> Optional[str]:
    # If emulator proxy exists and container is module then the emulator proxy name
    # should be the command.
    return (
        emulator_proxy_name
        if emulator_proxy_name is not None
        and issubclass(container.__class__, ModuleInputModel)
        else None
    )


def _get_port_bindings(
    container: Containers,
) -> Optional[List[Union[float, str, Port]]]:
    # If container is a robot add a port binding.
    if issubclass(container.__class__, RobotInputModel):
        return [container.get_port_binding_string()]
    else:
        return None


def _get_env_vars(
    container: Containers, emulator_proxy_name: Optional[str]
) -> ListOrDict:
    temp_vars: Dict[str, Any] = {}
    if (
        issubclass(container.__class__, RobotInputModel)
        and emulator_proxy_name is not None
    ):
        # TODO: If emulator proxy port is ever not hardcoded will have to update from
        #  11000 to a variable
        temp_vars["OT_SMOOTHIE_EMULATOR_URI"] = f"socket://{emulator_proxy_name}:11000"
        temp_vars["OT_EMULATOR_module_server"] = f'{{"host": "{emulator_proxy_name}"}}'
    elif issubclass(container.__class__, OT3InputModel):
        temp_vars["OT_API_FF_enableOT3HardwareController"] = True
    elif issubclass(container.__class__, ModuleInputModel):
        temp_vars.update(container.get_serial_number_env_var())
        temp_vars.update(container.get_proxy_info_env_var())
    else:
        temp_vars = {}

    return ListOrDict(__root__=temp_vars)


def _get_mount_strings(container: Containers) -> Optional[List[Union[str, Volume1]]]:
    mount_strings = container.get_mount_strings()
    return (
        cast(List[Union[str, Volume1]], mount_strings)
        if len(mount_strings) > 0
        else None
    )


def configure_input_service(
    container: Containers,
    emulator_proxy_name: Optional[str],
    config_model: SystemConfigurationModel,
    required_networks: RequiredNetworks,
) -> Service:
    """Configures services that are defined in input file."""
    service = Service(
        container_name=generate_container_name(container.id, config_model),
        image=get_service_image(container.get_image_name()),
        tty=True,
        build=get_service_build(container.get_image_name()),
        networks=required_networks.networks,
        volumes=_get_mount_strings(container),
        depends_on=_get_service_depends_on(container, emulator_proxy_name),
        ports=_get_port_bindings(container),
        command=_get_command(container, emulator_proxy_name),
        environment=_get_env_vars(container, emulator_proxy_name),
    )
    return service
