import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import Channel
from loguru import logger
import signal
import sys
from config import (
    API_ID, API_HASH, SESSION_NAME, PHONE_NUMBER,
    DEVICE_MODEL, SYSTEM_VERSION, APP_VERSION,
    MSG_BOT_STOPPED
)
from storage import Storage
from command_handler import CommandHandler
from message_handler import MessageHandler

logger.add("bot.log", rotation="1 MB")

class ChannelAggregator:
    def __init__(self):
        # Initialize client with custom device info
        self.client = TelegramClient(
            SESSION_NAME,
            API_ID,
            API_HASH,
            device_model=DEVICE_MODEL,
            system_version=SYSTEM_VERSION,
            app_version=APP_VERSION,
            system_lang_code='en'
        )
        self.storage = Storage()
        self.command_handler = CommandHandler(self.client, self.storage)
        self.message_handler = MessageHandler(self.client)
        self._setup_signal_handlers()
        self.is_stopping = False

    def _setup_signal_handlers(self):
        """Setup handlers for graceful shutdown"""
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self._handle_stop_signal)

    def _handle_stop_signal(self, signum, frame):
        """Handle stop signals"""
        if self.is_stopping:
            logger.warning("Forced shutdown...")
            sys.exit(1)
        
        logger.info("Received stop signal, shutting down gracefully...")
        self.is_stopping = True
        # Instead of creating a new task, we set a flag that will be checked
        self.client.disconnect()

    async def _shutdown(self):
        """Perform graceful shutdown"""
        try:
            # Notify user about shutdown
            if self.client.is_connected():
                me = await self.client.get_me()
                await self.client.send_message('me', MSG_BOT_STOPPED)
            
            # Stop command handler
            self.command_handler.is_running = False
            
            # Clear message handler cache
            self.message_handler.clear_cache()
            
            # Disconnect client
            await self.client.disconnect()
            logger.info("Bot stopped gracefully")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")

    async def start(self):
        """Start the bot"""
        try:
            if not self.client.is_connected():
                await self.client.connect()

            if not await self.client.is_user_authorized():
                if not PHONE_NUMBER:
                    logger.error("Phone number not found in configuration!")
                    return
                
                try:
                    # Send code request
                    await self.client.send_code_request(PHONE_NUMBER)
                    logger.info("Authentication code sent to your phone. Please check your messages.")
                    
                    # Get code from user input
                    code = input("Enter the code you received: ")
                    
                    try:
                        # Try to sign in with code
                        await self.client.sign_in(PHONE_NUMBER, code)
                    except Exception as e:
                        if "password" in str(e).lower():
                            # If 2FA is enabled, ask for password
                            password = input("Enter your 2FA password: ")
                            await self.client.sign_in(password=password)
                        else:
                            raise e

                    logger.info("Successfully signed in!")
                except Exception as e:
                    logger.error(f"Error during authentication: {str(e)}")
                    return

            await self.command_handler.setup()
            await self._register_message_handler()
            
            logger.info("Bot started")
            
            try:
                await self.client.run_until_disconnected()
            finally:
                if self.is_stopping:
                    await self._shutdown()
                
        except Exception as e:
            if not self.is_stopping:
                logger.error(f"Unexpected error: {str(e)}")
                await self._shutdown()

    async def _register_message_handler(self):
        """Register handler for new messages in channels"""
        @self.client.on(events.NewMessage)
        async def handle_new_message(event):
            try:
                # Log basic message info
                logger.debug(f"Received message {event.message.id} from chat {event.message.chat_id}")
                
                if not self.command_handler.is_running:
                    logger.debug("Bot is not running, skipping message")
                    return

                # Check if message is from channel
                if not event.is_channel:
                    logger.debug("Message is not from channel, skipping")
                    return
                
                channel_id = event.message.peer_id.channel_id
                logger.debug(f"Message is from channel {channel_id}")
                
                # Check if channel is monitored
                monitored_channels = self.storage.get_channels()
                if channel_id not in monitored_channels:
                    logger.debug(f"Channel {channel_id} is not in monitored list: {monitored_channels}")
                    return

                # Check if target channel is set
                target_channel = self.storage.get_target()
                if not target_channel:
                    logger.warning("Target channel not set")
                    return

                # Process message
                try:
                    logger.debug(f"Processing message {event.message.id} from channel {channel_id} to target {target_channel}")
                    await self.message_handler.process_message(event.message, target_channel)
                except Exception as e:
                    logger.error(f"Error processing message {event.message.id}: {str(e)}")
            except Exception as e:
                logger.error(f"Error in message handler: {str(e)}")

async def main():
    try:
        aggregator = ChannelAggregator()
        await aggregator.start()
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
    finally:
        # Ensure the event loop is stopped properly
        loop = asyncio.get_event_loop()
        loop.stop()

if __name__ == "__main__":
    asyncio.run(main()) 