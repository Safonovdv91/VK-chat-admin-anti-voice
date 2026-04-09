# tests/test_voice_guard.py
from unittest.mock import AsyncMock, MagicMock

import pytest

from bot.services.voice_guard import VoiceGuard


def make_message(duration: int | None = None, peer_id=1, from_id=100, cmid=42):
    message = MagicMock()
    message.peer_id = peer_id
    message.from_id = from_id
    message.conversation_message_id = cmid

    if duration is None:
        message.attachments = []
    else:
        att = MagicMock()
        att.type.value = "audio_message"
        att.audio_message.duration = duration
        message.attachments = [att]

    return message


@pytest.fixture
def services():
    msg_service = AsyncMock()
    msg_service.delete = AsyncMock(return_value=True)
    msg_service.send = AsyncMock()
    user_service = AsyncMock()
    user_service.get_first_name = AsyncMock(return_value="Иван")
    return msg_service, user_service


@pytest.fixture
def guard(services):
    msg_service, user_service = services
    return VoiceGuard(
        max_duration=20,
        message_service=msg_service,
        user_service=user_service,
    )


@pytest.mark.asyncio
async def test_no_attachments_ignored(guard, services):
    msg_service, _ = services
    await guard.handle(make_message(duration=None))
    msg_service.delete.assert_not_called()


@pytest.mark.asyncio
async def test_short_voice_ignored(guard, services):
    msg_service, _ = services
    await guard.handle(make_message(duration=15))
    msg_service.delete.assert_not_called()


@pytest.mark.asyncio
async def test_long_voice_deleted(guard, services):
    msg_service, _ = services
    await guard.handle(make_message(duration=30))
    msg_service.delete.assert_called_once_with(cmid=42, peer_id=1)


@pytest.mark.asyncio
async def test_warning_sent_after_delete(guard, services):
    msg_service, _ = services
    await guard.handle(make_message(duration=30))
    msg_service.send.assert_called_once()
    assert "20с" in msg_service.send.call_args.kwargs["text"]


@pytest.mark.asyncio
async def test_no_warning_if_delete_failed(guard, services):
    msg_service, _ = services
    msg_service.delete = AsyncMock(return_value=False)
    await guard.handle(make_message(duration=30))
    msg_service.send.assert_not_called()

def make_forwarded_message(peer_id=1, from_id=100, cmid=42):
    """Сообщение с пересланным голосовым внутри"""
    att = MagicMock()
    att.type.value = "audio_message"
    att.audio_message.duration = 5  # короткое, но пересланное

    fwd = MagicMock()
    fwd.attachments = [att]

    message = MagicMock()
    message.peer_id = peer_id
    message.from_id = from_id
    message.conversation_message_id = cmid
    message.attachments = []
    message.fwd_messages = [fwd]

    return message


@pytest.mark.asyncio
async def test_forwarded_voice_deleted(guard, services):
    msg_service, _ = services
    await guard.handle(make_forwarded_message())
    msg_service.delete.assert_called_once_with(cmid=42, peer_id=1)


@pytest.mark.asyncio
async def test_forwarded_voice_warning_text(guard, services):
    msg_service, _ = services
    await guard.handle(make_forwarded_message())
    msg_service.send.assert_called_once()
    assert "пересылка" in msg_service.send.call_args.kwargs["text"]