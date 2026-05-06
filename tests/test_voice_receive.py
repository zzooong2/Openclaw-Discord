import asyncio

from openclaw_discord.voice_receive import VoiceReceiveConnection


class FakeVoiceRecvModule:
    class VoiceRecvClient:
        pass


class FakeVoiceClient:
    def __init__(self):
        self.listened = []
        self.stopped = False
        self.disconnected = False

    def listen(self, sink):
        self.listened.append(sink)

    def stop_listening(self):
        self.stopped = True

    async def disconnect(self):
        self.disconnected = True


class FakeVoiceChannel:
    def __init__(self, voice_client):
        self.voice_client = voice_client
        self.connected_with = []

    async def connect(self, *, cls):
        self.connected_with.append(cls)
        return self.voice_client


class FakeBot:
    def __init__(self, channel):
        self.channel = channel

    def get_channel(self, channel_id):
        if channel_id == 123:
            return self.channel
        return None


class FakePipeline:
    pass


class FakeSinkFactory:
    def __init__(self, *, bridge, text_notifier=None):
        self.bridge = bridge
        self.text_notifier = text_notifier

    def create(self):
        return "sink"


class FakeNotifier:
    def __init__(self):
        self.messages = []

    async def send(self, message):
        self.messages.append(message)


def test_voice_receive_connection_joins_with_voice_recv_client():
    voice_client = FakeVoiceClient()
    channel = FakeVoiceChannel(voice_client)
    connection = VoiceReceiveConnection(bot=FakeBot(channel), voice_recv=FakeVoiceRecvModule)

    asyncio.run(connection.join("123"))

    assert channel.connected_with == [FakeVoiceRecvModule.VoiceRecvClient]


def test_voice_receive_connection_can_start_sink_after_join():
    voice_client = FakeVoiceClient()
    channel = FakeVoiceChannel(voice_client)
    connection = VoiceReceiveConnection(
        bot=FakeBot(channel),
        voice_recv=FakeVoiceRecvModule,
        pipeline=FakePipeline(),
        sink_factory_class=FakeSinkFactory,
    )

    asyncio.run(connection.join("123"))

    assert voice_client.listened == ["sink"]


def test_voice_receive_connection_notifies_when_listening_starts():
    voice_client = FakeVoiceClient()
    channel = FakeVoiceChannel(voice_client)
    notifier = FakeNotifier()
    connection = VoiceReceiveConnection(
        bot=FakeBot(channel),
        voice_recv=FakeVoiceRecvModule,
        pipeline=FakePipeline(),
        text_notifier=notifier,
        sink_factory_class=FakeSinkFactory,
    )

    asyncio.run(connection.join("123"))

    assert notifier.messages == ["음성 수신을 시작했습니다."]


def test_voice_receive_connection_starts_and_stops_listening():
    voice_client = FakeVoiceClient()
    channel = FakeVoiceChannel(voice_client)
    connection = VoiceReceiveConnection(bot=FakeBot(channel), voice_recv=FakeVoiceRecvModule)
    sink = object()

    asyncio.run(connection.join("123"))
    connection.listen(sink)
    connection.stop_listening()

    assert voice_client.listened == [sink]
    assert voice_client.stopped is True


def test_voice_receive_connection_leaves_channel():
    voice_client = FakeVoiceClient()
    channel = FakeVoiceChannel(voice_client)
    connection = VoiceReceiveConnection(bot=FakeBot(channel), voice_recv=FakeVoiceRecvModule)

    asyncio.run(connection.join("123"))
    asyncio.run(connection.leave())

    assert voice_client.disconnected is True
