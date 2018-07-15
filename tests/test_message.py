from tests.context import karma

from karma import message

import discord
import pytest



@pytest.mark.parametrize('input', [
    '<@0123456789> ++',
    '<@!0123456789> ++',
    '<@0123456789>++',
    '<@0123456789>++--',
    'words on <@0123456789> ++ either side',
])
def test_find_karma_in_valid_message(input):
    sent_message = discord.Message(content=input, reactions=[])
    karma_message = message.Message(sent_message)
    assert karma_message.grants_karma()


@pytest.mark.parametrize('input', [
    'Bob is a goat',
    'wow <@!0123456789> that was cool ++',
    '<@0123456789> + +',
    '<@!0123456789>  ++',
    '<@0123abc456def789> ++',
])
def test_find_no_karma_in_invalid_message(input):
    sent_message = discord.Message(content=input, reactions=[])
    karma_message = message.Message(sent_message)
    assert not karma_message.grants_karma()
