from openclaw_discord.voice_recv_patch import patch_packet_decoder


class FakeOpusError(Exception):
    pass


class FakePacketDecoder:
    def __init__(self, mode):
        self.mode = mode

    def pop_data(self, *args, **kwargs):
        if self.mode == "corrupt":
            raise FakeOpusError("corrupted stream")
        return "voice-data"

    def reset(self):
        self.mode = "reset"


def test_patch_packet_decoder_drops_corrupt_opus_packet_and_resets_decoder():
    patch_packet_decoder(FakePacketDecoder, opus_error_class=FakeOpusError)

    decoder = FakePacketDecoder("corrupt")

    assert decoder.pop_data() is None
    assert decoder.mode == "reset"


def test_patch_packet_decoder_keeps_normal_packets():
    patch_packet_decoder(FakePacketDecoder, opus_error_class=FakeOpusError)

    decoder = FakePacketDecoder("normal")

    assert decoder.pop_data() == "voice-data"


def test_patch_packet_decoder_is_idempotent():
    patch_packet_decoder(FakePacketDecoder, opus_error_class=FakeOpusError)
    patch_packet_decoder(FakePacketDecoder, opus_error_class=FakeOpusError)

    decoder = FakePacketDecoder("normal")

    assert decoder.pop_data() == "voice-data"
