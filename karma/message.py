"""Message processing and handling."""

import re

import karma.database as db

MAX_KARMA_CHANGE = 1


class Message():
    """Represents a message object in Discord."""

    def __init__(self, message, _match=None):
        self.message = message
        self.match = _match

    def grants_karma(self):
        """Boolean expression to check if karma was given."""
        return True if self._find_karma() else False

    def process_karma(self, author):
        """Update the database with data for a karma event."""
        match = self.match or self._find_karma()

        if match:
            mod = len(match.group('mod')) - 1  # given karma is one fewer than the number of +'es or -'es
            mod = min(mod, MAX_KARMA_CHANGE)  # limit change to 3 karma maximum
            change_type = match.group('mod')[0]
            if change_type == '-':
                mod = mod * -1

            if self.message.author.id == int(match.group('user_id')):
                return "Don't be a weasel!" if change_type == '+' else "Don't be so hard on yourself."

            user_id = match.group('user_id')
            entry = db.update_karma(user_id, mod)
            db.add_karma_event(self.message, user_id, mod)
            change = 'increased' if mod > 0 else 'decreased'
            return f"<@{user_id}>'s karma has {change} to {entry.karma}"

    def _find_karma(self):
        pattern = re.compile(r'<@!?(?P<user_id>\d+)>[\s]{0,2}(?P<mod>([+]{2,}|[-]{2,}))')
        self.match = pattern.search(self.message.content)
        return self.match
