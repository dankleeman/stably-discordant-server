import tomli

with open("config.toml", "rb") as f:
    config = tomli.load(f)

if config["auth"]["discord_token"] == "XXXX":
    raise ValueError("Invalid Discord token still set to default value. Refer to documentation for instructions.")
