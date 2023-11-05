# Stably Discordant Server
Stably Discordant Server is a python library for the server part of a client/server system. Drawing from my [Stable Discord](https://github.com/dankleeman/stable-discord/) project, the Stably Discordant project allows several machines to volunteer to contribute to a worker pool processing images. The distributed work is coordinated by a server (this project) that runs a Discord bot as a frontend. The worker codebase can be found [here](https://github.com/dankleeman/stably-discordant-worker/).

## Communicating With Clients
The client-server communication is handled through ZeroMQ. This allows for the queueing of work units over a simple messaging protocol without the need for an independent broker.

For a client to connect to the server, the client needs to run the worker program and pass in two parameters:
1. The public IP Address of the server host machine
2. The port the server host machine expects to receive communication on

The server host port can be set with the command line parameter `--host-port` on `app/server.py`. This value defaults to `5556`.

**Note: Keep in mind that regular networking rules apply. If the server process is running on a local network and not all of the client machines are on that local network then some basic port forwarding may be in order.**

## Installation
Stably Discordant Server uses poetry to manage dependencies and installation.

**NOTE: Stably Discordant Server currently only supports python 3.10. While it is likely that some minor poetry work could easily extend this to other python versions, absolutely no testing or work has yet been performed to this end.**

### Linux / MacOS
A user may run the following steps manually or if they have `make` installed they may run `make setup`.

	python3 -m pip install poetry
	poetry install

### Windows
A user may run the following steps manually or if they have `make` installed they may run `make setup`.

	python3 -m pip install poetry
	poetry install


## Setting Up Discord
The discord functionality for this project makes heavy use of `discord.py`: https://discordpy.readthedocs.io/en/stable/

Follow the steps recommended by discord.py to create a Bot Account and retrieve a Discord API token: https://discordpy.readthedocs.io/en/stable/discord.html

When at the "Inviting Your Bot" step and selecting permissions the minimum permissions that your bot will need are as follows.

**General Permissions:**
- Read Messages/View Channels

**Text Permissions**
- Send Messages
- Read Message History
- Add Reactions
- Attach Files

## Configuration with config.toml
Stable Discord is intended to require only changes to the single `config.toml` for the vast majority of users. Further, the defaults are such that most users should only have to add their discord token to the `discord_token` entry.

While the config file also has comments, we describe each section and the options therein in detail here.

**Note:** Keep in mind that Stably Discordant Server reads the configuration file at startup. For any changes to be reflected, the program needs to be restarted.
### \[auth\]
- `discord_token` - A string containing the API token assigned by Discord.

### \[discord.settings\]
One of the key features of the bot is to be able to control where it is listening and two whom it is listening. Because this bot is running on hardware the user controls, if the user cannot limit who the bot acknowledges, then a user is susceptible to spam or other types of griefing.

By default the bot listens on all channels to which it is invited and to messages from all users other than itself.

If neither of the channel level settings are set, the bot will listen on all channels to which it is invited.
- `listen_channels` - A list of channels that the bot listens to. Specify in case-sensitive `[server:channel, server:channel]` format. Defaults to empty.
- `ignore_channels`  A list of channels that the bot ignores. Specify in case-sensitive `[server:channel, server:channel]` format. Defaults to empty.

If neither are set, the bot will listen to all members, but never itself. Note that after the [Discord username change](https://discord.com/blog/usernames) the format is likely to be `username#0`. It used to be the case that "id" referred to the (now deprecated) discriminant.
- `listen_users` - A list of users to which the bot listens and responds. Specify in case-sensitive `[username#id, username#id]` format. Defaults to empty.
- `ignore_users` - A list of users that the bot ignores. Specify in case-sensitive `[username#id, username#id]` format. Defaults to empty.

- `wake_word` - The string that a message must start with to invoke the bot to generate art.
### \[discord.style\]
The following settings are small quality-of-life improvements so that users get some kind of feedback about what the bot is doing. This way users can tell if the bot missed their message for some reason and may need to be added to the `listen_users` list or of the bot is still just busy, for example.
- `ack_emoji` - The emoji reaction the bot uses to indicate that it has noticed a user's message. Defaults to 👍.
- `in_prog_emoji` - The emoji reaction the bot uses to indicate that it is currently working on a user's request. Defaults to ⏱️.
- `done_emoji` - he emoji reaction the bot uses to indicate that it has completed a user's request. Defaults to 💯.
### \[misc_settings\]
- `log_dir`  - A path to the desired logging directory. Defaults to `logs`

## Execution
Stably Discordant Server may be started by running the `server.py` file in the `app` director of this repostitory: `poetry run python app/server.py`. The server host port can be set with the command line parameter `--host-port`. This value defaults to `5556`.

## Example Usage on Discord
### Discord Message Parameters
To give a command to the bot a user begins their  message with the `wake_word` which defaults to `/art`. Text after that is interpreted as the prompt, except for some special cases where the user can add parameters.

- `--cfg 7.5` - Adding `--cfg` to the prompt followed by a number alters the CFG parameter passed to the diffusion model. If not specified, this value defaults to 7.5.
- `--steps 50` Adding `--steps` followed by an integer influences the number of diffusion steps the model takes. If not specified this value defaults to 50.
### Example Behavior
Both of the examples below show the bot in use with user info redacted. Note how the bot defaults to responding with the parameters it parsed from the message. This allows the users to understand the inputs and riff off of eachother.

#### Basic Example
![basic_example.png](assets/basic_example.png)

#### Long Prompt Example
![long_prompt_example.png](assets/long_prompt_example.png)

#### Example with Parameters
![params_example.png](assets/params_example.png)

## Contributing
This repository is open for use or to be forked freely. I intend to get Stable Discord to a stable state and leave it there, but I will consider contributions in the unlikely event they are provided.

## Changelog
See `CHANGELOG.md` file in the root directory of this repository. 

## License
[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)
See the `LICENSE` file in the root directory of this repository. 

## Notes
### Conventions
README - https://www.makeareadme.com/

Semantic Versioning - https://semver.org/

Conventional Commits - https://www.conventionalcommits.org/en/v1.0.0/

### Other References
This program uses emojis that can be referenced here: https://unicode.org/emoji/charts/full-emoji-list.html

Licensing for Open Source: https://choosealicense.com/