import json
from typing import List, Optional
from config import DB_FILE
from loguru import logger

class Storage:
    def __init__(self):
        self.channels: List[int] = []
        self.target_channel: Optional[int] = None
        self.load()

    def load(self) -> None:
        """Load channels data from file"""
        try:
            with open(DB_FILE, 'r') as f:
                data = json.load(f)
                self.channels = data.get('channels', [])
                self.target_channel = data.get('target_channel')
                logger.debug(f"Loaded channels: {self.channels}, target: {self.target_channel}")
        except FileNotFoundError:
            logger.debug("No existing channels file, creating new one")
            self.save()

    def save(self) -> None:
        """Save channels data to file"""
        with open(DB_FILE, 'w') as f:
            data = {
                'channels': self.channels,
                'target_channel': self.target_channel
            }
            json.dump(data, f)
            logger.debug(f"Saved channels: {self.channels}, target: {self.target_channel}")

    def add_channel(self, channel_id: int) -> bool:
        """Add channel to monitoring list"""
        if channel_id not in self.channels:
            self.channels.append(channel_id)
            logger.info(f"Added channel {channel_id} to monitoring list")
            self.save()
            return True
        logger.debug(f"Channel {channel_id} already in monitoring list")
        return False

    def remove_channel(self, channel_id: int) -> bool:
        """Remove channel from monitoring list"""
        if channel_id in self.channels:
            self.channels.remove(channel_id)
            logger.info(f"Removed channel {channel_id} from monitoring list")
            self.save()
            return True
        logger.debug(f"Channel {channel_id} not in monitoring list")
        return False

    def set_target(self, channel_id: int) -> None:
        """Set target channel"""
        old_target = self.target_channel
        self.target_channel = channel_id
        logger.info(f"Changed target channel from {old_target} to {channel_id}")
        self.save()

    def get_channels(self) -> List[int]:
        """Get list of monitored channels"""
        return self.channels

    def get_target(self) -> Optional[int]:
        """Get target channel"""
        return self.target_channel 