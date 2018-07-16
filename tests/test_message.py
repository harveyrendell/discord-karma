from tests.context import karma
from unittest import mock

from karma import message

import discord
import pytest


@pytest.mark.parametrize('valid_inputs', [
    '<@0123456789> ++',
    '<@!0123456789> ++',
    '<@0123456789>++',
    '<@0123456789>++--',
    '<@01234567890123456789>++--',
    'words on <@0123456789> ++ either side',
])
def test_find_karma_in_valid_message(valid_inputs):
    sent_message = discord.Message(content=valid_inputs, reactions=[])
    karma_message = message.Message(sent_message)
    assert karma_message.grants_karma()


@pytest.mark.parametrize('invalid_inputs', [
    'Bob is a goat',
    'wow <@!0123456789> that was cool ++',
    '<@0123456789> + +',
    '<@!0123456789>  ++',
    '<@0123abc456def789> ++',
    '<0123abc456def789> ++',
    '<0123abc456def789> +-',
    '<0123abc456def789> -+-',
])
def test_find_no_karma_in_invalid_message(invalid_inputs):
    sent_message = discord.Message(content=invalid_inputs, reactions=[])
    karma_message = message.Message(sent_message)
    assert not karma_message.grants_karma()


@mock.patch('karma.message.db.update_karma', return_value=mock.Mock(karma=0))
def test_process_grants_single_karma(mock_update_function):
    sent_message = discord.Message(content='<@0123456789> ++', reactions=[])
    karma_message = message.Message(sent_message)
    karma_message.process_karma()

    args, kwargs = mock_update_function.call_args

    assert mock_update_function.called
    assert args == ('0123456789', 1)



@mock.patch('karma.message.db.update_karma', return_value=mock.Mock(karma=0))
def test_process_grants_single_karma_with_extra_input(mock_update_function):
    sent_message = discord.Message(content='<@0123456789> +++++', reactions=[])
    karma_message = message.Message(sent_message)
    karma_message.process_karma()

    args, kwargs = mock_update_function.call_args

    assert mock_update_function.called
    assert args == ('0123456789', 1)


@mock.patch('karma.message.db.update_karma', return_value=mock.Mock(karma=0))
def test_process_grants_multiple_karma_within_higher_limit(mock_update_function):
    karma.message.MAX_KARMA_CHANGE = 5  # Raise limit for maximum single change

    sent_message = discord.Message(content='<@0123456789> ++++++', reactions=[])
    karma_message = message.Message(sent_message)
    karma_message.process_karma()

    args, kwargs = mock_update_function.call_args

    assert mock_update_function.called
    assert args == ('0123456789', 5)


@mock.patch('karma.message.db.update_karma', return_value=mock.Mock(karma=0))
def test_process_limits_negative_karma(mock_update_function):
    karma.message.MAX_KARMA_CHANGE = 5  # Raise limit for maximum single change

    sent_message = discord.Message(content='<@0123456789> --------------', reactions=[])
    karma_message = message.Message(sent_message)
    karma_message.process_karma()

    args, kwargs = mock_update_function.call_args

    assert mock_update_function.called
    assert args == ('0123456789', -5)
