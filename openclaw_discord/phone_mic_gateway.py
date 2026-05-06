from __future__ import annotations

import socket
from collections.abc import Awaitable, Callable
from typing import Any

from aiohttp import web

from openclaw_discord.speech_pipeline import SpeechCommandPipeline


def build_phone_mic_html() -> str:
    return """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>OpenClaw Phone Mic</title>
  <style>
    :root { color-scheme: dark; font-family: system-ui, sans-serif; }
    body { margin: 0; min-height: 100vh; display: grid; place-items: center; background: #101318; color: #f4f7fb; }
    main { width: min(680px, calc(100vw - 32px)); display: grid; gap: 16px; }
    h1 { font-size: 24px; margin: 0; }
    p { margin: 0; color: #aeb8c8; line-height: 1.5; }
    button, input { font: inherit; border-radius: 8px; border: 1px solid #344054; padding: 14px 16px; }
    button { background: #2f6fed; color: white; font-weight: 700; }
    button.secondary { background: #1b2029; color: #e6edf7; }
    input { background: #161b22; color: #f4f7fb; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    #status, #result { min-height: 24px; }
  </style>
</head>
<body>
  <main>
    <h1>OpenClaw Phone Mic</h1>
    <p id="status">대기 중</p>
    <p id="diagnostics">브라우저 상태 확인 중</p>
    <div class="row">
      <button id="start">말하기 시작</button>
      <button id="stop" class="secondary">중지</button>
    </div>
    <input id="manual" autocomplete="off" placeholder="예: 클로 온">
    <button id="send" class="secondary">텍스트 전송</button>
    <p id="result"></p>
  </main>
  <script>
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const statusEl = document.querySelector('#status');
    const diagnosticsEl = document.querySelector('#diagnostics');
    const resultEl = document.querySelector('#result');
    const manualEl = document.querySelector('#manual');
    const startButton = document.querySelector('#start');
    const stopButton = document.querySelector('#stop');
    let recognition = null;

    function setDiagnostics(message) {
      diagnosticsEl.textContent = `브라우저 상태: ${message}`;
    }

    async function sendText(text) {
      const value = String(text || '').trim();
      if (!value) return;
      statusEl.textContent = `전송: ${value}`;
      const response = await fetch('/speech', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: value }),
      });
      const data = await response.json();
      resultEl.textContent = data.message;
      statusEl.textContent = data.ok ? '완료' : '차단됨';
    }

    document.querySelector('#send').addEventListener('click', () => sendText(manualEl.value));
    manualEl.addEventListener('keydown', event => {
      if (event.key === 'Enter') sendText(manualEl.value);
    });

    const secureStatus = window.isSecureContext ? '보안 컨텍스트' : '보안 컨텍스트 아님';
    const speechStatus = SpeechRecognition ? '음성 인식 지원' : '음성 인식 미지원';
    setDiagnostics(`${secureStatus}, ${speechStatus}, ${location.protocol}`);

    if (!SpeechRecognition) {
      statusEl.textContent = '브라우저 음성 인식을 사용할 수 없습니다. 텍스트 전송을 사용하세요.';
      startButton.disabled = true;
      stopButton.disabled = true;
    } else {
      recognition = new SpeechRecognition();
      recognition.lang = 'ko-KR';
      recognition.continuous = true;
      recognition.interimResults = false;
      recognition.onstart = () => statusEl.textContent = '듣는 중';
      recognition.onerror = event => statusEl.textContent = `오류: ${event.error}`;
      recognition.onend = () => statusEl.textContent = '대기 중';
      recognition.onresult = event => {
        const transcript = event.results[event.results.length - 1][0].transcript;
        manualEl.value = transcript;
        sendText(transcript);
      };
      startButton.addEventListener('click', () => {
        try {
          statusEl.textContent = '음성 인식 시작 요청 중';
          recognition.start();
        } catch (error) {
          statusEl.textContent = `start failed: ${error.message}`;
        }
      });
      stopButton.addEventListener('click', () => {
        try {
          recognition.stop();
        } catch (error) {
          statusEl.textContent = `stop failed: ${error.message}`;
        }
      });
    }
  </script>
</body>
</html>
"""


async def handle_phone_mic_index(_: web.Request) -> web.Response:
    return web.Response(text=build_phone_mic_html(), content_type="text/html")


async def handle_phone_mic_speech(
    request: web.Request,
    *,
    pipeline: SpeechCommandPipeline,
    owner_user_id: str,
    max_text_chars: int,
) -> web.Response:
    try:
        payload = await request.json()
    except Exception:
        return web.json_response({"ok": False, "message": "Invalid JSON body."}, status=400)

    text = str(payload.get("text", "")).strip()
    if not text:
        return web.json_response({"ok": False, "message": "No speech text was received."}, status=400)
    if len(text) > max_text_chars:
        return web.json_response({"ok": False, "message": "Speech text is too long."}, status=413)

    result = await pipeline.process_recognized_text(text, user_id=owner_user_id)
    return web.json_response({"ok": result.ok, "message": result.message})


def build_phone_mic_app(
    *,
    pipeline: SpeechCommandPipeline,
    owner_user_id: str,
    max_text_chars: int,
) -> web.Application:
    app = web.Application()

    async def speech_handler(request: web.Request) -> web.Response:
        return await handle_phone_mic_speech(
            request,
            pipeline=pipeline,
            owner_user_id=owner_user_id,
            max_text_chars=max_text_chars,
        )

    app.router.add_get("/", handle_phone_mic_index)
    app.router.add_post("/speech", speech_handler)
    return app


async def start_phone_mic_site(app: web.Application, *, host: str, port: int) -> web.AppRunner:
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    return runner


def find_lan_ip() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        try:
            probe.connect(("8.8.8.8", 80))
            return str(probe.getsockname()[0])
        except OSError:
            return "127.0.0.1"


def phone_mic_urls(*, host: str, port: int, lan_ip_factory: Callable[[], str] = find_lan_ip) -> list[str]:
    if host in {"0.0.0.0", "::"}:
        return [f"http://127.0.0.1:{port}", f"http://{lan_ip_factory()}:{port}"]
    return [f"http://{host}:{port}"]
