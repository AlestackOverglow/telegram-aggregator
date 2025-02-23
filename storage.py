import json
from typing import List, Optional
from config import DB_FILE

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
        except FileNotFoundError:
            self.save()

    def save(self) -> None:
        """Save channels data to file"""
        with open(DB_FILE, 'w') as f:
            json.dump({
                'channels': self.channels,
                'target_channel': self.target_channel
            }, f)

    def add_channel(self, channel_id: int) -> bool:
        """Add channel to monitoring list"""
        if channel_id not in self.channels:
            self.channels.append(channel_id)
            self.save()
            return True
        return False

    def remove_channel(self, channel_id: int) -> bool:
        """Remove channel from monitoring list"""
        if channel_id in self.channels:
            self.channels.remove(channel_id)
            self.save()
            return True
        return False

    def set_target(self, channel_id: int) -> None:
        """Set target channel"""
        self.target_channel = channel_id
        self.save()

    def get_channels(self) -> List[int]:
        """Get list of monitored channels"""
        return self.channels

    def get_target(self) -> Optional[int]:
        """Get target channel"""
        return self.target_channel 