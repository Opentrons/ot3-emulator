from __future__ import annotations
import abc
import argparse

from command_creators.command import CommandList
from settings_models import ConfigurationSettings


class AbstractCommandCreator(abc.ABC):
    """Interface for AbstractCommandCreator classes"""

    @classmethod
    @abc.abstractmethod
    def from_cli_input(
            cls, args: argparse.Namespace, settings: ConfigurationSettings
    ) -> AbstractCommandCreator:
        ...

    @abc.abstractmethod
    def get_commands(self) -> CommandList:
        ...

