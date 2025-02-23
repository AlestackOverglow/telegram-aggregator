from typing import Optional, Tuple
from telethon import TelegramClient, events
from telethon.tl.types import User, Channel, PeerChannel
from telethon.tl.functions.channels import JoinChannelRequest
from loguru import logger
from config import *
from storage import Storage
import re

class CommandHandler:
    def __init__(self, client: TelegramClient, storage: Storage):
        self.client = client
        self.storage = storage
        self.is_running = False
        self.me: Optional[User] = None

    async def setup(self) -> None:
        """Setup command handler"""
        self.me = await self.client.get_me()
        await self._register_handlers()

    def _parse_channel_input(self, input_str: str) -> str:
        """Parse channel input to get username"""
        # Remove leading/trailing whitespace
        input_str = input_str.strip()
        
        # Handle t.me links
        if 't.me/' in input_str:
            username = input_str.split('t.me/')[-1].split('/')[0]
            return username.strip()
            
        # Handle @ usernames
        if input_str.startswith('@'):
            return input_str[1:].strip()
            
        return input_str.strip()

    async def _get_channel(self, channel_input: str) -> Tuple[Optional[Channel], str]:
        """Get channel entity and formatted name"""
        try:
            username = self._parse_channel_input(channel_input)
            
            # Try to get channel
            channel = await self.client.get_entity(username)
            
            if not isinstance(channel, (Channel, PeerChannel)):
                return None, MSG_INVALID_CHANNEL
                
            # Try to join the channel if not already joined
            try:
                await self.client(JoinChannelRequest(channel))
            except Exception as e:
                logger.warning(f"Could not join channel {username}: {str(e)}")
            
            return channel, channel.username or channel.title
            
        except ValueError:
            return None, MSG_INVALID_CHANNEL
        except Exception as e:
            logger.error(f"Error getting channel {channel_input}: {str(e)}")
            return None, MSG_CHANNEL_NOT_FOUND

    async def _register_handlers(self) -> None:
        """Register message handlers for commands"""
        @self.client.on(events.NewMessage(pattern=CMD_START))
        async def start_handler(event):
            if not await self._is_saved_messages(event):
                return
            self.is_running = True
            await event.reply(MSG_BOT_STARTED)

        @self.client.on(events.NewMessage(pattern=CMD_STOP))
        async def stop_handler(event):
            if not await self._is_saved_messages(event):
                return
            self.is_running = False
            await event.reply(MSG_BOT_STOPPED)

        @self.client.on(events.NewMessage(pattern=CMD_ADD_ALL_CHANNELS))
        async def add_all_channels_handler(event):
            if not await self._is_saved_messages(event):
                return
            
            await event.reply(MSG_ADDING_ALL_CHANNELS)
            added_count = 0

            try:
                # Get all dialogs (channels, chats, etc.)
                async for dialog in self.client.iter_dialogs():
                    # Check if it's a channel (not a group or private chat)
                    if isinstance(dialog.entity, Channel) and not dialog.entity.broadcast:
                        continue  # Skip if it's a group chat
                    
                    if isinstance(dialog.entity, Channel) and dialog.entity.broadcast:
                        # Skip if it's the target channel
                        if dialog.entity.id == self.storage.get_target():
                            continue
                            
                        # Add channel to monitoring list
                        if self.storage.add_channel(dialog.entity.id):
                            added_count += 1
                            
                await event.reply(MSG_ALL_CHANNELS_ADDED.format(added_count))
            except Exception as e:
                logger.error(f"Error adding all channels: {str(e)}")
                await event.reply(f"Error occurred while adding channels: {str(e)}")

        @self.client.on(events.NewMessage(pattern=CMD_ADD_CHANNEL + r'\s+(.+)'))
        async def add_channel_handler(event):
            if not await self._is_saved_messages(event):
                return
            channel_input = event.pattern_match.group(1)
            channel, name = await self._get_channel(channel_input)
            
            if channel:
                self.storage.add_channel(channel.id)
                await event.reply(MSG_CHANNEL_ADDED.format(name))
            else:
                await event.reply(name)  # Error message

        @self.client.on(events.NewMessage(pattern=CMD_REMOVE_CHANNEL + r'\s+(.+)'))
        async def remove_channel_handler(event):
            if not await self._is_saved_messages(event):
                return
            channel_input = event.pattern_match.group(1)
            channel, name = await self._get_channel(channel_input)
            
            if channel:
                self.storage.remove_channel(channel.id)
                await event.reply(MSG_CHANNEL_REMOVED.format(name))
            else:
                await event.reply(name)  # Error message

        @self.client.on(events.NewMessage(pattern=CMD_SET_TARGET + r'\s+(.+)'))
        async def set_target_handler(event):
            if not await self._is_saved_messages(event):
                return
            channel_input = event.pattern_match.group(1)
            channel, name = await self._get_channel(channel_input)
            
            if channel:
                self.storage.set_target(channel.id)
                await event.reply(MSG_TARGET_SET.format(name))
            else:
                await event.reply(name)  # Error message

        @self.client.on(events.NewMessage(pattern=CMD_LIST))
        async def list_handler(event):
            if not await self._is_saved_messages(event):
                return
            channels = []
            for channel_id in self.storage.get_channels():
                try:
                    channel = await self.client.get_entity(channel_id)
                    channels.append(f"- {channel.username or channel.title}")
                except Exception as e:
                    logger.error(f"Error getting channel info: {str(e)}")
            
            target = self.storage.get_target()
            target_info = ""
            if target:
                try:
                    target_channel = await self.client.get_entity(target)
                    target_info = f"\nTarget channel: {target_channel.username or target_channel.title}"
                except Exception as e:
                    logger.error(f"Error getting target channel info: {str(e)}")
            
            message = "Monitored channels:\n" + "\n".join(channels) + target_info
            await event.reply(message)

        @self.client.on(events.NewMessage(pattern=CMD_STATUS))
        async def status_handler(event):
            if not await self._is_saved_messages(event):
                return
            status = "running" if self.is_running else "stopped"
            await event.reply(f"Bot status: {status}")

    async def _is_saved_messages(self, event) -> bool:
        """Check if message is from Saved Messages"""
        return event.message.peer_id.user_id == self.me.id 