import argparse
import logging
import shlex
from typing import Any

logger = logging.getLogger(__name__)


class PromptParser:
    """A wrapper class that utilizes the argparse ArgumentParser to parse a string of input into the arguments
    that can be consumed by a stable diffusion model.
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser(prog="StableDiscord", add_help=False)
        self.parser.add_argument(
            "prompt",
            nargs="*",
            help=(
                "The prompt is a positional argument meaning text not assigned to an argument is presumed to be"
                "the prompt."
            ),
        )
        self.parser.add_argument(
            "--cfg",
            type=float,
            default=7.5,
            help=(
                "A float value for the 'Context Free Guidance' parameter. Sometimes called 'style' in other models."
                " (Defaults to 7.5)"
            ),
        )
        self.parser.add_argument(
            "--steps",
            type=int,
            default=50,
            help=(
                "The number of diffusion steps. More will take longer, but usually returns better results."
                " (Defaults to 50)"
            ),
        )

    @property
    def help_text(self) -> str:
        """Generate the help text for the argument parser.

        Returns:
            str: The help text to explain what arguments are understood and what they do.
        """
        return self.parser.format_help()

    def parse_input(self, user_input: str) -> tuple[dict[str, Any], str]:
        """

        Args:
            user_input: The string of input that needs to be parsed

        Returns:
            known_args: A dict of the correctly parsed arguments.
            unknown_args: A string of all the arguments that were not correctly parsed. This may be useful for
                user feedback or logging.
        """
        logger.debug("Parsing args from: %s", user_input)
        known_args, unknown_args = self.parser.parse_known_args(shlex.split(user_input, posix=False))
        known_args = vars(known_args)

        known_args["prompt"] = " ".join(known_args["prompt"])
        unknown_args = " ".join(unknown_args)
        logger.debug("Parsed known args: %s", known_args)
        logger.debug("Parsed unknown args: %s", unknown_args)

        return known_args, unknown_args
