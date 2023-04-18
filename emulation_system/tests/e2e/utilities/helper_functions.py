"""Module containing pure functions to retrieve general information from Docker containers."""

from typing import Any, Dict, List, Optional

import docker  # type: ignore[import]
from docker.models.containers import Container  # type: ignore[import]

from emulation_system.compose_file_creator import Service
from tests.e2e.utilities.consts import ExpectedMount, ExpectedNamedVolume


def get_volumes(container: Container) -> Optional[List[Dict[str, Any]]]:
    """Gets a list of volumes for a docker container.

    Returns None if no volumes exist
    """
    return [mount for mount in container.attrs["Mounts"] if mount["Type"] == "volume"]


def cast_volume_dict_to_expected_volume(volume: Dict[str, Any]) -> ExpectedNamedVolume:
    return ExpectedNamedVolume(
        VOLUME_NAME=volume["Name"], DEST_PATH=volume["Destination"]
    )


def cast_mount_dict_to_expected_mount(mount: Dict[str, Any]) -> ExpectedMount:
    return ExpectedMount(SOURCE_PATH=mount["Source"], DEST_PATH=mount["Destination"])


def get_mounts(container: Container) -> Optional[List[Dict[str, Any]]]:
    """Gets a list of mounts for a docker container.

    Returns None if no mounts exist
    """
    return [mount for mount in container.attrs["Mounts"] if mount["Type"] == "bind"]


def get_container(service: Optional[Service]) -> Optional[Container]:
    """Gets Docker Container object from local Docker dameon based off of passed Service object.

    Specifically looks for a container with same name as passed Service object.
    """
    if service is None:
        return None
    else:
        return docker.from_env().containers.get(service.container_name)


def get_containers(services: Optional[List[Service]]) -> Optional[List[Container]]:
    """Gets a list of containers based off of passed list."""
    if services is None:
        return None
    else:
        return [get_container(service) for service in services]


def exec_in_container(container: Container, command: str) -> str:
    """Runs a command in passed docker container and returns command's output."""
    api_client = docker.APIClient()
    exec_id = api_client.exec_create(container.id, command)["Id"]
    return api_client.exec_start(exec_id).decode().strip()


def _filter_mounts(
    container: Container, expected_mount: ExpectedMount
) -> List[Dict[str, Any]]:
    mounts = get_mounts(container)
    assert mounts is not None, "mounts are None"
    return [
        mount
        for mount in mounts
        if (
            mount["Type"] == "bind"
            and mount["Source"] == expected_mount.SOURCE_PATH
            and mount["Destination"] == expected_mount.DEST_PATH
        )
    ]


def _filter_volumes(
    container: Container, expected_vol: ExpectedNamedVolume
) -> List[Dict[str, Any]]:
    volumes = get_volumes(container)
    assert volumes is not None, "volumes are None"
    filtered_volume = [
        volume
        for volume in volumes
        if (
            volume["Type"] == "volume"
            and volume["Name"] == expected_vol.VOLUME_NAME
            and volume["Destination"] == expected_vol.DEST_PATH
        )
    ]

    return filtered_volume


def confirm_named_volume_exists(
    container: Container, expected_vol: ExpectedNamedVolume
) -> bool:
    """Helper method to assert that exected named volume exists on Docker container."""
    return len(_filter_volumes(container, expected_vol)) == 1


def confirm_named_volume_does_not_exist(
    container: Container, expected_vol: ExpectedNamedVolume
) -> bool:
    """Helper method to assert that expected named volue does NOT exist on Docker container."""
    return len(_filter_volumes(container, expected_vol)) == 0


def confirm_mount_exists(container: Container, expected_mount: ExpectedMount) -> bool:
    """Helper method to assert that mount exists on Docker container."""
    return len(_filter_mounts(container, expected_mount)) == 1


def confirm_mount_does_not_exist(
    container: Container, expected_mount: ExpectedMount
) -> bool:
    """Helper method to assert that mount does NOT exist on Docker container."""
    return len(_filter_mounts(container, expected_mount)) == 0