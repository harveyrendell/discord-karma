import re

import karma.database as db

MAX_KARMA_CHANGE = 1


class Message():

    def __init__(self, message, _match=None):
        self.message = message
        self.match = _match

    def grants_karma(self):
        return True if self._find_karma() else False

    def process_karma(self):
        match = self.match or self._find_karma()

        if match:
            mod = len(match.group('mod')) - 1  # given karma is one fewer than the number of +'es or -'es
            mod = min(mod, MAX_KARMA_CHANGE)  # limit change to 3 karma maximum
            change_type = match.group('mod')[0]
            if change_type == '-':
                mod = mod * -1

            if self.message.author.id == match.group('user_id'):
                return "Don't be a weasel!" if change_type == '+' else "Don't be so hard on yourself."

            user_id = match.group('user_id')
            entry = db.update_karma(user_id, mod)
            change = 'increased' if mod > 0 else 'decreased'
            return "<@{}>'s karma has {} to {}".format(user_id, change, entry.karma)

    def _find_karma(self):
        pattern = re.compile(r'<@!?(?P<user_id>\d+)>\s*(?P<mod>([+]{2,}|[-]{2,}))')
        self.match = pattern.search(self.message.content)
        return self.match
