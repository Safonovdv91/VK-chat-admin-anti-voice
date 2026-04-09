# tests/test_video_guard.py
from unittest.mock import AsyncMock, MagicMock

import pytest

from bot.services.guards.video_guard import VideoGuard


def make_video_message(duration: int, peer_id=1, from_id=100, cmid=42):
    att = MagicMock()
    att.type.value = "video_message"
    att.video_message.duration = duration

    message = MagicMock()
    message.peer_id = peer_id
    message.from_id = from_id
    message.conversation_message_id = cmid
    message.attachments = [att]
    message.fwd_messages = []
    return message


def make_forwarded_video_message(peer_id=1, from_id=100, cmid=42):
    att = MagicMock()
    att.type.value = "video_message"
    att.video_message.duration = 5

    fwd = MagicMock()
    fwd.attachments = [att]

    message = MagicMock()
    message.peer_id = peer_id
    message.from_id = from_id
    message.conversation_message_id = cmid
    message.attachments = []
    message.fwd_messages = [fwd]
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
    return VideoGuard(max_duration=20, message_service=msg_service, user_service=user_service)


@pytest.mark.asyncio
async def test_short_video_ignored(guard, services):
    msg_service, _ = services
    await guard.handle(make_video_message(duration=15))
    msg_service.delete.assert_not_called()


@pytest.mark.asyncio
async def test_long_video_deleted(guard, services):
    msg_service, _ = services
    await guard.handle(make_video_message(duration=30))
    msg_service.delete.assert_called_once_with(cmid=42, peer_id=1)


@pytest.mark.asyncio
async def test_long_video_warning_text(guard, services):
    msg_service, _ = services
    await guard.handle(make_video_message(duration=30))
    assert "кружочки" in msg_service.send.call_args.kwargs["text"]


@pytest.mark.asyncio
async def test_forwarded_video_deleted(guard, services):
    msg_service, _ = services
    await guard.handle(make_forwarded_video_message())
    msg_service.delete.assert_called_once_with(cmid=42, peer_id=1)


@pytest.mark.asyncio
async def test_forwarded_video_warning_text(guard, services):
    msg_service, _ = services
    await guard.handle(make_forwarded_video_message())
    assert "кружочков" in msg_service.send.call_args.kwargs["text"]