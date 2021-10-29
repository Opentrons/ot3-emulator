from parser_utils import ParserWithError, get_formatter
from parsers.emulation import emulation_parser
from parsers.repo import repo_parser
from parsers.virtual_machine import virtual_machine_parser


SUBPARSER_FUNCTIONS = [
    emulation_parser,
    virtual_machine_parser,
    repo_parser
]

def main_parser() -> ParserWithError:
    parser = ParserWithError(
        description="Utility for managing Opentrons Emulation system",
        formatter_class=get_formatter(),
        prog="opentrons-emulation"
    )

    subparsers = parser.add_subparsers(
        dest="command", title="subcommands", required=True
    )
    subparsers.metavar = ''
    for parser_function in SUBPARSER_FUNCTIONS:
        parser_function(subparsers)

    return parser
