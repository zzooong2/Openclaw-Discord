# Discord Voice Receive Plan

`discord.py` is used for slash commands and voice-channel connection. Receiving user audio is handled as an optional adapter because Discord voice receive is not part of the stable `discord.py` core API.

The planned adapter is `discord-ext-voice-recv`. Its README describes `VoiceRecvClient` as the voice client class to pass to `VoiceChannel.connect()`, and exposes `listen(sink)` / `stop_listening()` on the resulting voice client. The same README warns that the extension is not feature complete and does not guarantee stability, so OpenClaw keeps it behind `openclaw_discord.voice_receive.VoiceReceiveConnection`.

Install the optional receive/STT dependency when starting real Discord voice recognition work:

```bash
python -m pip install .[voice]
```

The first STT sink uses `discord.ext.voice_recv.extras.speechrecognition.SpeechRecognitionSink` with the `google` recognizer. That gives us a fast Korean-capable prototype, but it still depends on a third-party speech service. The code keeps this behind `SpeechRecognitionSinkFactory` so the recognizer can be swapped later.

References:

- https://github.com/imayhaveborkedit/discord-ext-voice-recv
- https://pypi.org/project/discord-ext-voice-recv/
