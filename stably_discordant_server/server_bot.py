import asyncio
import base64
import json
import logging
import tempfile
import threading
from typing import Any

import discord
import zmq

from stably_discordant_server.config import config
from stably_discordant_server.parser import PromptParser
from stably_discordant_server.units import WorkUnit

logger = logging.getLogger(__name__)


class DiscordBotBase(discord.Client):
    """A class that handles interacting with the users on discord and coordinating between the different parts
    of the stable-discord system"""

    def __init__(self) -> None:
        intents = discord.Intents(value=68608)
        intents.message_content = True
        intents.messages = True
        intents.guilds = True

        super().__init__(intents=intents)
        self.config: dict = config["discord"]
        self.allowed_users: set[str] = set(self.config["settings"]["listen_users"])
        self.disallowed_users: set[str] = set(self.config["settings"]["ignore_users"])
        self.allowed_channels: set[discord.TextChannel] = set()

        logger.info("Allowed users: %s", self.allowed_users)
        logger.info("Disallowed users: %s", self.disallowed_users)

        self.prompt_parser: PromptParser = PromptParser()

    def set_allowed_channels(self) -> None:
        """Look through the channels available to the bot and apply rules from the config file to decide which
        channels to take input from.

        1. If "listen_channels" has values then set the allowed_channels to be a set of those channel objects
        2. If "listen_channels" is not present and "ignore_channels" is then set the allowed_channels to be a set of
            available channels not in the "ignore_channels" list.
        3. Otherwise, allowed_channels is set to be a set of all seen channels.
        """
        channels_dict = {
            f"{guild.name}:{channel.name}": channel
            for guild in self.guilds
            for channel in guild.text_channels
        }

        if self.config["settings"]["listen_channels"]:
            self.allowed_channels = {
                channels_dict[key]
                for key in channels_dict
                if key in self.config["settings"]["listen_channels"]
            }
        elif self.config["settings"]["ignore_channels"]:
            self.allowed_channels = {
                channels_dict[key]
                for key in channels_dict
                if key not in self.config["settings"]["ignore_channels"]
            }
        else:
            self.allowed_channels = set(channels_dict.values())

    def clean_message(self, user_input: str) -> str:
        """A short helper function that cleans a user message. Here, clean means removing the "wake word" and stripping
            away leading whitespace.

        Args:
            user_input: The raw user message.

        Returns:
            str: The cleaned user message.
        """
        return user_input.replace(self.config["settings"]["wake_word"], "").lstrip()

    async def help_response(self, message: discord.Message) -> None:
        """A short helper function to handle responding to a user that asked for help.

        Args:
            message (discord.Message): The user message object.

        """
        await message.reply(self.prompt_parser.help_text)
        await message.add_reaction(self.config["style"]["done_emoji"])

    async def extract_message_args(self, message: discord.Message) -> dict[str, Any]:
        logger.debug("Extracting inputs")
        cleaned_message_text = self.clean_message(message.content)

        logger.info("Processing prompt '%s' from %s", cleaned_message_text, message.author)
        try:
            known_args, unknown_args = self.prompt_parser.parse_input(cleaned_message_text)
        except ValueError as e:
            if e.args[0] == "No closing quotation":
                await message.reply(
                    "Prompt has open quotation with no closing quotation. Please fix and try again."
                )
            else:
                await message.reply(
                    "Prompt has unspecified syntax error. Please fix and try again."
                )
            return {}
        except SystemExit as e:
            if e.args[0] == 2:
                await message.reply(
                    "Prompt has invalid integer input on integer argument. Please fix and try again."
                )
            else:
                await message.reply(
                    "Prompt has unspecified syntax error. Please fix and try again."
                )
            return {}

        if unknown_args:
            await message.reply(f"Skipping unknown args: {unknown_args}")

        if not known_args["prompt"]:
            await message.reply("Skipping request with empty prompt.")
            return {}

        return known_args

    def user_is_allowed(self, user: discord.User) -> bool:
        """Decide if the given user should be allowed to send input to the diffuser.

        In all cases the bot itself is not allowed.
        1. If allowed_users has values then the user is allowed if their "name#id" string is in allowed_users
        2. If allowed_users is empty and disallowed_users has values then the user is allowed if their "name#id" is not
            in the disallowed_users.
        3. Otherwise, the user is allowed.

        Args:
            user (discord.User): The user to be checked for is_allowed status.

        Returns:
            bool: Whether the user is allowed to send input to the diffuser.
        """
        if self.allowed_users:
            return f"{user.name}#{user.discriminator}" in self.allowed_users and user != self.user

        if self.disallowed_users:
            return (
                f"{user.name}#{user.discriminator}" not in self.disallowed_users
                and user != self.user
            )

        return user != self.user

    async def on_ready(self) -> None:
        raise NotImplementedError

    async def on_message(self, message: discord.Message) -> None:
        raise NotImplementedError


class QueueHandler:
    def __init__(self, host_port: str):
        self.work_queue: list[WorkUnit] = []
        self.work_queue_lock = threading.Lock()
        # self.output_queue = []
        # self.output_queue_lock = threading.Lock()
        self.ready_workers: list[bytes] = []

        self.queue_context = zmq.Context()
        self.sock = self.queue_context.socket(zmq.ROUTER)
        self.sock.bind(f"tcp://*:{host_port}")

        self.pending_work: dict[int, WorkUnit] = dict()

    async def enqueue_work(self, work_unit):
        with self.work_queue_lock:
            self.work_queue.append(work_unit)

    # async def dequeue_output(self):
    #     with self.output_queue_lock:
    #         if self.output_queue:
    #             return self.output_queue.pop(0)

    async def loop(self):
        poller = zmq.Poller()
        poller.register(self.sock, zmq.POLLIN)

        logger.info("Initializing queue handler loop.")

        while True:
            sock_resp = dict(poller.poll(timeout=0))

            # Process messages on the queue
            if self.sock in sock_resp and sock_resp[self.sock] == zmq.POLLIN:
                worker_id, worker_json = self.sock.recv_multipart()
                worker_response = json.loads(worker_json.decode("utf-8"))
                logger.info("Found message on the zmq: ", worker_response)

                if worker_response["type"] == "READY":
                    hostname = worker_response["hostname"]
                    logger.info(
                        "Worker id %s hostname %s reports ready.", worker_id.hex(), hostname
                    )
                    self.ready_workers.append(worker_id)

                elif worker_response["type"] == "OUTPUT":
                    logger.info("Worker %s has returned work", worker_id.hex())
                    image_data_base64 = worker_response["image_data"]
                    image_data = base64.b64decode(image_data_base64)

                    # with self.output_queue_lock:
                    id_num = worker_response["id_num"]
                    if id_num not in self.pending_work:
                        logger.info("Received work unit %s not marked as outstanding.", id_num)
                    else:
                        logger.info("Received work found as pending work item %s", id_num)
                        pending_item = self.pending_work.pop(id_num)
                        message = pending_item.discord_message
                        args = pending_item.args
                        hostname = worker_response["hostname"]
                        with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
                            temp_file.write(image_data)
                            logger.info("Sending output in discord message reply")
                            content = f"Parsed args: {args} processed by hostname: {hostname}"
                            await message.reply(file=discord.File(temp_file.name), content=content)
                            # TODO: Move this in progress to when the item is being added as pending work?
                            # TODO: Rework as part of reviving output queue pattern
                            # await message.remove_reaction(self.config["style"]["in_prog_emoji"],
                            #                               self.user)  # type: ignore
                            # await message.add_reaction(self.config["style"]["done_emoji"])

                # TODO: Handle retry unanswered work
                elif worker_response["type"] == "GOODBYE":
                    pass
                else:
                    raise ValueError("Unhandled message: ", worker_response)

            # Send any pending work
            with self.work_queue_lock:
                if self.work_queue and self.ready_workers:
                    work_unit = self.work_queue.pop(0)
                    worker_id = self.ready_workers.pop(0)
                    logger.info(
                        "Sending work unit args %s id %s to worker id %s",
                        work_unit.args,
                        work_unit.id_num,
                        worker_id.hex(),
                    )
                    logger.info("Sending args: %s", work_unit.args)
                    payload = json.dumps(work_unit.args | {"id_num": work_unit.id_num}).encode(
                        "utf-8"
                    )

                    self.sock.send_multipart([worker_id, payload])
                    self.pending_work[work_unit.id_num] = work_unit

            await asyncio.sleep(1)


class LoadBalancerBot(DiscordBotBase):
    def __init__(self, host_port: str = "5555"):
        super().__init__()
        self.queue_handler = QueueHandler(host_port=host_port)

    async def on_ready(self) -> None:
        """An event-driven function that runs when the bot is first initialized."""
        logger.info("Logged on as %s!", self.user)
        self.set_allowed_channels()
        for channel in self.allowed_channels:
            logger.info("Announcing login in server:channel - '%s:%s'", channel.guild.name, channel)
            await channel.send("I'm here!")

        # TODO: Revisit discord-py.ext.tasks pattern for this.
        # The fact that this function never properly terminates seems like an abuse.
        await self.queue_handler.loop()

    async def on_message(self, message: discord.Message) -> None:
        """An event-driven function that runs whenever the bot sees a message on a channel it is in.

        Args:
            message (discord.Message): The user message object.
        """
        logger.debug(
            "Seen message '%s' from %s on %s channel on %s server",
            message.content,
            message.author,
            message.channel,
            message.channel.guild,
        )

        if (
            message.content.startswith(self.config["settings"]["wake_word"])
            and message.channel in self.allowed_channels
            and self.user_is_allowed(message.author)  # type: ignore
        ):
            logger.debug("Wake-word detected in message on allowed channel.")
            await message.add_reaction(self.config["style"]["ack_emoji"])

            if "--help" in message.content:
                await self.help_response(message)
                return

            args = await self.extract_message_args(message)
            unit = WorkUnit(message, args)
            await self.queue_handler.enqueue_work(unit)
