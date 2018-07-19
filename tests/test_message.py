from tests.context import karma
from unittest import mock
import unittest

from karma import message

import discord
import pytest


@pytest.mark.parametrize('valid_input', [
    '<@0123456789> ++',
    '<@!0123456789> ++',
    '<@0123456789>++',
    '<@0123456789>++--',
    '<@01234567890123456789> ++',
    'words on <@0123456789> ++ either side',
])
def test_find_karma_in_valid_message(valid_input):
    sent_message = discord.Message(content=valid_input, reactions=[])
    karma_message = message.Message(sent_message)
    assert karma_message.grants_karma()


@pytest.mark.parametrize('invalid_input', [
    'Bob is a goat',
    'wow <@!0123456789> that was cool ++',
    '<@0123456789> + +',
    '<@!0123456789>  ++',
    '<@0123abc456def789> ++',
    '<0123abc456def789> ++',
    '<0123abc456def789> +-',
    '<0123abc456def789> -+--+',
    '<@0123456789> +--+',
    '<@0123456789>',
])
def test_find_no_karma_in_invalid_message(invalid_input):
    sent_message = discord.Message(content=invalid_input, reactions=[])
    karma_message = message.Message(sent_message)
    assert not karma_message.grants_karma()


@pytest.fixture
@mock.patch('karma.message.db.update_karma', return_value=mock.Mock(karma=0))
def send_karma_message(mock_db, content):
    sent_message = discord.Message(content=content, reactions=[])
    karma_msg = message.Message(sent_message)
    karma_msg.process_karma()
    return mock_db


@pytest.fixture
def set_max_karma_change():
    karma.message.MAX_KARMA_CHANGE = 5  # Raise limit for maximum single change


@pytest.mark.parametrize('content', ['<@0123456789> ++'])
def test_process_grants_single_karma(send_karma_message):
    send_karma_message.assert_called_once()
    args, kwargs = send_karma_message.call_args
    assert args == ('0123456789', 1)


@pytest.mark.parametrize('content', ['I give <@0123456789> ++ because why not'])
def test_process_grants_single_karma_with_extra_input(send_karma_message):
    send_karma_message.assert_called_once()
    args, kwargs = send_karma_message.call_args
    assert args == ('0123456789', 1)


@pytest.mark.parametrize('content', ['<@0123456789> +++++++++++'])
def test_process_limits_karma_in_single_message(send_karma_message):
    send_karma_message.assert_called_once()
    args, kwargs = send_karma_message.call_args
    assert args == ('0123456789', 1)


@pytest.mark.parametrize('content', ['<@0123456789> +++++++++'])
def test_process_grants_multiple_karma_within_higher_limit(set_max_karma_change, send_karma_message):
    send_karma_message.assert_called_once()
    args, kwargs = send_karma_message.call_args
    assert args == ('0123456789', 5)


@pytest.mark.parametrize('content', ['<@0123456789> --------------'])
def test_process_limits_negative_karma(set_max_karma_change, send_karma_message):
    send_karma_message.assert_called_once()
    args, kwargs = send_karma_message.call_args
    assert args == ('0123456789', -5)


@mock.patch('karma.message.db.update_karma', return_value=mock.Mock(karma=23))
def test_process_karma_produces_correct_output_for_increase(mock_update_function):
    sent_message = discord.Message(content='<@0123456789> ++', reactions=[])
    karma_message = message.Message(sent_message)
    response = karma_message.process_karma()

    assert mock_update_function.called
    assert response == "<@0123456789>'s karma has increased to 23"


@mock.patch('karma.message.db.update_karma', return_value=mock.Mock(karma=-14))
def test_process_karma_produces_correct_output_for_decrease(mock_update_function):
    sent_message = discord.Message(content='<@9876543210> --', reactions=[])
    karma_message = message.Message(sent_message)
    response = karma_message.process_karma()

    assert mock_update_function.called
    assert response == "<@9876543210>'s karma has decreased to -14"
