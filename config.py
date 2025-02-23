import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram API credentials
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')

# Create sessions directory if not exists
SESSIONS_DIR = 'sessions'
if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

# Session configuration
SESSION_NAME = os.path.join(SESSIONS_DIR, 'aggregator_bot')
DEVICE_MODEL = 'Channel Aggregator Bot'
SYSTEM_VERSION = 'Bot 1.0'
APP_VERSION = '1.0'

# Database file name
DB_FILE = 'channels.json'

# Commands
CMD_START = '/start'
CMD_STOP = '/stop'
CMD_ADD_CHANNEL = '/add_channel'
CMD_ADD_ALL_CHANNELS = '/add_all_channels'
CMD_REMOVE_CHANNEL = '/remove_channel'
CMD_SET_TARGET = '/set_target'
CMD_LIST = '/list'
CMD_STATUS = '/status'

# Message templates
MSG_BOT_STARTED = "Bot started. Monitoring channels..."
MSG_BOT_STOPPED = "Bot stopped."
MSG_CHANNEL_ADDED = "Channel {} added to monitoring list."
MSG_CHANNEL_REMOVED = "Channel {} removed from monitoring list."
MSG_TARGET_SET = "Target channel set to {}."
MSG_INVALID_CHANNEL = """Invalid channel format. Please use one of these formats:
1. Username: @channelname
2. Link: https://t.me/channelname"""
MSG_CHANNEL_NOT_FOUND = "Channel not found. Please check if the channel exists and is accessible."
MSG_NO_TARGET = "Target channel not set."
MSG_ADDING_ALL_CHANNELS = "Adding all your subscribed channels (this might take a moment)..."
MSG_ALL_CHANNELS_ADDED = "Added {} channels to monitoring list. Use /list to see them all." 