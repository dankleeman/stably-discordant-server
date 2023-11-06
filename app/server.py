import argparse

from stably_discordant_server import utils
from stably_discordant_server.config import config
from stably_discordant_server.server_bot import LoadBalancerBot

logger = utils.setup_logger()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--logging-level", dest="logging_level", default="INFO")
    parser.add_argument("--host_port", dest="host_port", default="5556", type=str)
    args = vars(parser.parse_args())
    logger.setLevel(args.pop("logging_level"))

    bot = LoadBalancerBot(**args)
    bot.run(config["auth"]["discord_token"])
