from typing import List, Dict, Set
from telethon import TelegramClient
from telethon.tl.types import Message
from loguru import logger

class MessageHandler:
    def __init__(self, client: TelegramClient):
        self.client = client
        self.album_cache: Dict[str, List[Message]] = {}
        self._processed_messages = set()  # Cache of processed message IDs

    async def process_message(self, message: Message, target_channel_id: int) -> None:
        """Process single message or part of album"""
        if message.id in self._processed_messages:
            return

        # Handle grouped messages (albums)
        if message.grouped_id:
            await self._handle_album_message(message, target_channel_id)
        else:
            await self._forward_single_message(message, target_channel_id)

    async def _handle_album_message(self, message: Message, target_channel_id: int) -> None:
        """Handle message that is part of an album"""
        group_id = str(message.grouped_id)
        
        if group_id not in self.album_cache:
            self.album_cache[group_id] = []
        
        self.album_cache[group_id].append(message)
        
        # Get all messages from the same chat with this grouped_id
        try:
            messages = await message.client.get_messages(
                message.peer_id,
                limit=10,  # Reasonable limit for album size
                filter=lambda m: m.grouped_id == message.grouped_id
            )
            total_messages = len(messages)
            
            # If we have all messages in the album
            if len(self.album_cache[group_id]) >= total_messages:
                # Sort messages by ID to maintain order
                album = sorted(self.album_cache[group_id], key=lambda x: x.id)
                await self._forward_album(album, target_channel_id)
                
                # Clear cache and mark messages as processed
                for msg in album:
                    self._processed_messages.add(msg.id)
                del self.album_cache[group_id]
                
        except Exception as e:
            logger.error(f"Error handling album message: {str(e)}")
            # Clean up cache in case of error
            if group_id in self.album_cache:
                del self.album_cache[group_id]

    async def _forward_single_message(self, message: Message, target_channel_id: int) -> None:
        """Forward single message to target channel"""
        try:
            await self.client.forward_messages(target_channel_id, message)
            await message.mark_read()
            self._processed_messages.add(message.id)
            logger.info(f"Forwarded message {message.id} to target channel")
        except Exception as e:
            logger.error(f"Error forwarding message {message.id}: {str(e)}")

    async def _forward_album(self, album: List[Message], target_channel_id: int) -> None:
        """Forward album to target channel"""
        try:
            await self.client.forward_messages(target_channel_id, album)
            for message in album:
                await message.mark_read()
            logger.info(f"Forwarded album with {len(album)} messages to target channel")
        except Exception as e:
            logger.error(f"Error forwarding album: {str(e)}")

    def clear_cache(self) -> None:
        """Clear the cache of processed messages"""
        self._processed_messages.clear()
        self.album_cache.clear() 