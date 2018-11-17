from threading import Thread

import discord
import asyncio

from config.cst import *
from services.abstract_service import *


class DiscordService(AbstractService):
    REQUIRED_CONFIG = {"token": "", "channel_id": ""}

    def __init__(self):
        super().__init__()
        self.discord_api = None
        self.discord_thread = None
        self.discord_channel = None

    @staticmethod
    def is_setup_correctly(config):
        return CONFIG_DISCORD in config[CONFIG_CATEGORY_SERVICES] \
               and CONFIG_SERVICE_INSTANCE in config[CONFIG_CATEGORY_SERVICES][CONFIG_DISCORD]

    def prepare(self):
        if not self.discord_api or not self.discord_thread:
            self.discord_api = discord.Client()
            self.discord_channel = discord.Object(id=
                                                  self.config[CONFIG_CATEGORY_SERVICES][CONFIG_DISCORD]["channel_id"])

            self.discord_thread = Thread(target=self.discord_api.run,
                                         args=(self.config[CONFIG_CATEGORY_SERVICES][CONFIG_DISCORD]["token"], ))
            self.discord_thread.start()

    def get_type(self):
        return CONFIG_DISCORD

    def get_endpoint(self):
        return self.discord_api

    def has_required_configuration(self):
        return CONFIG_CATEGORY_SERVICES in self.config \
               and CONFIG_DISCORD in self.config[CONFIG_CATEGORY_SERVICES] \
               and self.check_required_config(self.config[CONFIG_CATEGORY_SERVICES][CONFIG_DISCORD])

    def send_message(self, content, error_on_failure=True):
        try:
            self.discord_api.send_message(destination=self.discord_channel, content=content)
            return True
        except Exception as e:
            error = f"Failed to execute send message : {e} with content:{content}"
            if error_on_failure:
                self.logger.error(error)
            else:
                self.logger.info(error)
        return None

    def get_successful_startup_message(self):
        return f"Successfully initialized."

    def stop(self):
        self.discord_api.logout()
        self.discord_thread = None
