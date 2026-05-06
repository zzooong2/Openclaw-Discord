from __future__ import annotations

import logging
from typing import Any

import discord

log = logging.getLogger(__name__)


def patch_packet_decoder(
    packet_decoder_class: type[Any],
    *,
    opus_error_class: type[BaseException] = discord.opus.OpusError,
) -> None:
    if getattr(packet_decoder_class, "_openclaw_opus_patch", False):
        return

    original_pop_data = packet_decoder_class.pop_data

    def pop_data_with_corrupt_packet_guard(self: Any, *args: Any, **kwargs: Any) -> Any | None:
        try:
            return original_pop_data(self, *args, **kwargs)
        except opus_error_class as exc:
            log.warning("Dropped corrupt Discord voice packet: %s", exc)
            self.reset()
            return None

    packet_decoder_class.pop_data = pop_data_with_corrupt_packet_guard
    packet_decoder_class._openclaw_opus_patch = True


def patch_installed_voice_recv() -> None:
    from discord.ext.voice_recv.opus import PacketDecoder

    patch_packet_decoder(PacketDecoder)
