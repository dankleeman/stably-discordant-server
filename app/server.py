import argparse

from stabley_discordant_server import utils
from stabley_discordant_server.server_bot import LoadBalancerBot
from stabley_discordant_server.config import config

logger = utils.setup_logger()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--logging-level", dest="logging_level", default="INFO")
    args = vars(parser.parse_args())
    logger.setLevel(args.pop("logging_level"))

    bot = LoadBalancerBot()
    bot.run(config["auth"]["discord_token"])
