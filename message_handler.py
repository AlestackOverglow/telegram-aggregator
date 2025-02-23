from typing import List, Dict, Set
from telethon import TelegramClient, types
from telethon.tl.types import Message
from loguru import logger

class MessageHandler:
    def __init__(self, client: TelegramClient):
        self.client = client
        self._processed_messages = set()  # Cache of processed message IDs
        self._processed_albums = set()  # Cache of processed album IDs

    async def process_message(self, message: Message, target_channel_id: int) -> None:
        """Process single message or part of album"""
        try:
            if message.id in self._processed_messages:
                logger.debug(f"Skipping already processed message {message.id}")
                return

            # Handle grouped messages (albums)
            if message.grouped_id:
                group_id = str(message.grouped_id)
                if group_id in self._processed_albums:
                    logger.debug(f"Skipping already processed album {group_id}")
                    return
                    
             
                album_messages = await message.client.get_messages(
                    message.chat_id,
                    ids=[message.id - i for i in range(10)] 
                )
                
                
                is_first_in_album = all(
                    msg is None or msg.grouped_id != message.grouped_id 
                    for msg in album_messages 
                    if msg and msg.id < message.id
                )
                
                if not is_first_in_album:
                    logger.debug(f"Skipping non-first message {message.id} in album {group_id}")
                    return
                    
                logger.debug(f"Processing first message {message.id} of album {group_id}")
                await self._handle_album_message(message, target_channel_id)
            else:
                await self._forward_single_message(message, target_channel_id)
        except Exception as e:
            logger.error(f"Error in process_message: {str(e)}")

    async def _handle_album_message(self, message: Message, target_channel_id: int) -> None:
        """Handle message that is part of an album"""
        if not message.grouped_id:
            return
            
        group_id = str(message.grouped_id)
        logger.debug(f"Starting to process album {group_id} (message {message.id})")
        
        try:
            # Get messages by grouped_id
            album_messages = []
            async for msg in message.client.iter_messages(
                message.chat_id,
                limit=50,  
                wait_time=0  
            ):
                if msg.grouped_id != message.grouped_id:
                    continue
                if isinstance(msg.media, (types.MessageMediaPhoto, types.MessageMediaDocument)):
                    album_messages.append(msg)
                    logger.debug(f"Found album message {msg.id}")
                
                
                if len(album_messages) >= 10 or msg.id < message.id - 20:
                    break
            
            if not album_messages:
                logger.warning(f"No media messages found in album {group_id}")
                return
                
            # Sort messages by ID to maintain order
            album = sorted(album_messages, key=lambda x: x.id)
            logger.info(f"Prepared album {group_id} with {len(album)} messages for forwarding")
            
            # Forward the album
            await self._forward_album(album, target_channel_id)
            
            # Mark all messages as processed
            self._processed_albums.add(group_id)
            for msg in album:
                self._processed_messages.add(msg.id)
                logger.debug(f"Marked message {msg.id} as processed")
            
            logger.info(f"Completed processing album {group_id}")
                
        except Exception as e:
            logger.error(f"Error handling album {group_id}: {str(e)}")

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
            # Forward messages as a group
            await self.client.forward_messages(
                target_channel_id,
                messages=album,
                from_peer=album[0].chat_id
            )
            
            # Mark as read after successful forward
            for message in album:
                await message.mark_read()
            
            logger.info(f"Successfully forwarded album with {len(album)} messages to target channel")
        except Exception as e:
            logger.error(f"Error forwarding album: {str(e)}")
            logger.error(f"Album details: {len(album)} messages, first message ID: {album[0].id if album else 'unknown'}")

    def clear_cache(self) -> None:
        """Clear the cache of processed messages"""
        self._processed_messages.clear()
        self._processed_albums.clear() 