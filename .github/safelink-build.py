"""Assemble the SafeLink Pages build from the existing standalone atlas."""

from html import escape
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen
import re
import shutil
import subprocess

VOICE_ENDPOINT = ''

NIGHT_STYLE = r"""

.safelink-extra{background:var(--night-panel,#1d2548);color:var(--night-ink,#fff9ed);border:1px solid var(--night-edge,#8291b8);padding:.9rem;margin-block:.6rem;border-radius:.75rem}
.safelink-extra:focus-within{box-shadow:0 0 0 1px var(--night-edge)} .safelink-extra a{color:var(--night-teal,#95e7de)}
.safelink-extra button,.safelink-extra select{min-height:44px;margin:.25rem;padding:.45rem .65rem;border:1px solid var(--night-edge);background:var(--night-bg);color:var(--night-ink);border-radius:.35rem}
.safelink-extra canvas{display:block;max-width:100%;height:auto;margin:.5rem auto}
.safelink-extra [hidden]{display:none!important}
.safelink-utilities{width:min(980px,94%);margin:1.2rem auto}
.safelink-refuge{background:#154241;color:white;border:2px solid white;border-radius:50%;padding:2px 6px;font-weight:900}
.safelink-exhibit{max-width:min(92vw,580px);min-width:min(82vw,480px);font-size:1.2rem}
.safelink-hazard-scene{height:80px;display:flex;justify-content:center;align-items:center;gap:16px;perspective:260px}
.safelink-hazard-scene i{display:block;width:42px;height:42px;background:#87652d;box-shadow:5px 8px 0 #482d15;transform:rotateX(24deg) rotateY(-20deg)}
.safelink-hazard-scene i:nth-child(2){background:#226963}.safelink-hazard-scene i:nth-child(3){background:#753f61}

:root { --night-bg:#111633;--night-panel:#1e2548;--night-ink:#fff9ed;--night-accent:#ffce79;--night-teal:#71dfcf;--night-edge:#6f78a2;--night-sky:#191f49; }
:root[data-night-phase="day"] { --night-bg:#e6edf4;--night-panel:#f7fafc;--night-ink:#1c2645;--night-accent:#71531a;--night-teal:#046557;--night-edge:#8c9db2;--night-sky:#dce8f3; }
:root[data-night-phase="dawn"] { --night-bg:#322543;--night-panel:#443451;--night-sky:#65436b;--night-edge:#ae839b; }
:root[data-night-phase="dusk"] { --night-bg:#241d40;--night-panel:#352952;--night-sky:#4e3461;--night-edge:#9d79a9; }
body.safelink-has-dock { background:var(--night-bg);color:var(--night-ink); }
body.safelink-has-dock, body.safelink-has-dock * { font-family:Nunito,"Baloo Thambi 2",system-ui,sans-serif!important; }
body.safelink-has-dock :is(h1,h2,h3,#brand-title) { font-family:"Baloo 2","Baloo Thambi 2",Nunito,sans-serif!important;color:inherit!important;text-shadow:none;line-height:1.1; }
body.safelink-has-dock #intro { background:var(--night-sky);color:var(--night-ink);border-color:var(--night-edge); }
body.safelink-has-dock #intro::before { border-color:var(--night-edge); }
body.safelink-has-dock #intro #brand-title { color:var(--night-accent)!important; }
body.safelink-has-dock .atlas-sub[data-typing="true"]::after { color:var(--night-ink); }
body.safelink-has-dock .atlas-top,body.safelink-has-dock .workspace-nav,body.safelink-has-dock .safelink-dock { background:var(--night-panel);color:var(--night-ink);border-color:var(--night-edge); }
body.safelink-has-dock .atlas-top a,body.safelink-has-dock .safelink-dock button,body.safelink-has-dock .safelink-contact a,body.safelink-has-dock .safelink-connectivity span { color:var(--night-ink); }
body.safelink-has-dock .atlas-top a:focus-visible,body.safelink-has-dock .atlas-cta:focus-visible { outline:3px solid var(--night-accent); }
body.safelink-has-dock .state-mapcard,body.safelink-has-dock .state-card { background:var(--night-panel);background:color-mix(in srgb,var(--night-panel) 96%,transparent);backdrop-filter:blur(8px);color:var(--night-ink);border-color:var(--night-edge);box-shadow:0 16px 45px #05091c35; }
body.safelink-has-dock .state-card a,body.safelink-has-dock .state-mapcard a,body.safelink-has-dock .state-intro a { color:var(--night-teal); }
body.safelink-has-dock .state-card button:not([data-condition]),.night-sheet nav button,.night-preferences button,.night-preferences select,.night-time input { background:var(--night-bg);color:var(--night-ink);border:1px solid var(--night-edge);border-radius:.6rem;padding:.55rem .75rem; }
body.safelink-has-dock .state-card :is(p,small,label),body.safelink-has-dock .state-mapcard p,body.safelink-has-dock .state-intro p { color:var(--night-ink); }
.night-preferences { display:flex;flex-wrap:wrap;gap:.75rem;margin-top:1rem;align-items:center;position:relative;z-index:2; }
.night-preferences select,.night-preferences button,.night-sheet nav button { min-height:44px; }
.night-sheet { grid-column:1 / -1;min-width:0;border:1px solid var(--night-edge);background:var(--night-panel);color:var(--night-ink);padding:.7rem;border-radius:1rem; }
.night-sheet summary { font-size:1.15rem;font-weight:900;cursor:pointer;padding:.4rem; }
.night-sheet nav { display:flex;flex-wrap:wrap;gap:.4rem;padding:.4rem; }
.night-sheet .state-card { margin-top:.5rem; }
.night-time { display:grid;gap:.3rem;margin-block:.65rem; }
.night-canvas { position:absolute;inset:0;width:100%;height:100%;pointer-events:none; }
.night-rendered :is(.atlas-paper,.atlas-pin) { opacity:0!important; }
.night-rendered figcaption { visibility:hidden; }
#intro .atlas-graphic { rotate:var(--lean,0deg);transition:rotate .2s ease; }
.night-firefly { display:none;position:fixed;left:0;top:0;width:6px;height:6px;border-radius:50%;background:#ffdead;box-shadow:0 0 12px 4px #ffd080;pointer-events:none;z-index:5; }
@media (hover:hover) and (pointer:fine) { .night-firefly:not([hidden]){display:block} }
.night-sos { position:fixed;z-index:2147483000;right:max(.7rem,env(safe-area-inset-right));bottom:max(1rem,env(safe-area-inset-bottom));display:grid;place-items:center;min-width:100px;min-height:48px;padding:.25rem .65rem;background:#930d2e;color:#fff!important;border:2px solid #fff;font:900 1rem Nunito,sans-serif;text-decoration:none;border-radius:.72rem;box-shadow:0 3px 14px #100415aa; }
dialog .night-sos { position:absolute;bottom:1rem; }
.night-sos:focus-visible,.night-sheet :focus-visible,.night-preferences :focus-visible { outline:3px solid #ffc861;outline-offset:3px; }
@media(max-width:740px){.night-sos{bottom:calc(68px + env(safe-area-inset-bottom));}.night-sheet{padding:.5rem;}.night-sheet nav button{flex:1 1 auto;}}
@media(prefers-reduced-motion:reduce){#intro .atlas-graphic{rotate:none;transition:none}.night-firefly{display:none!important}}

"""

STYLE = r"""
.safelink-featured { margin:.55rem 0; padding:.55rem; border:1px solid #ba9488; }
.safelink-featured button { min-height:44px; margin:.2rem; }

.safelink-nearby { max-height:26rem; }
.safelink-nearby details { margin:.4rem 0; padding:.35rem; border-bottom:1px solid #c9aea1; }
.safelink-nearby button, #state-feature button { display:inline-block; min-height:44px; padding:.4rem .65rem; margin:.2rem; }
#state-feature { scroll-margin-top:5rem; }
.safelink-contact { padding:1.4rem; }
.safelink-contact a { overflow-wrap:anywhere; }

body.safelink-has-dock :is(h1,h2,h3,#brand-title) { font-family:Nunito,sans-serif!important; font-style:normal!important; font-weight:900!important; letter-spacing:.025em!important; color:#601d36ed!important; text-shadow:1px 1px 0 #d4a2a080,2px 2px 1px #ae688e44,0 0 8px #c7759e4d; }
.safelink-route-choices { display:flex; flex-wrap:wrap; gap:.45rem; }
.safelink-route-choices button { min-height:42px; padding:.5rem; color:#fff; border:2px solid transparent; border-radius:.3rem; font-weight:800; }
.safelink-route-choices [data-condition="red"] { background:#8b2237; }
.safelink-route-choices [data-condition="green"] { background:#13603a; }
.safelink-route-choices [aria-pressed="true"] { outline:2px solid #493843; outline-offset:2px; }

.safelink-landmark-search { padding:.65rem; border:1px solid #ba9488; margin-bottom:.65rem; }
.safelink-landmark-search label { display:inline-block; margin:.3rem; }
.safelink-landmark-search input[type="search"] { max-width:100%; min-height:42px; }
.safelink-landmark-search li { padding:.35rem 0; }
.safelink-landmark-search button, #state-feature button { margin:.2rem; min-height:38px; }
#state-feature small { display:block; }

#call-level { display: block; width: min(220px,90%); height: 16px; margin: .45rem auto; }
#call-level[hidden] { display: none; }
.safelink-place-label { color:#352322; background:#fff9ed; border:1px solid #82545f; border-radius:5px; padding:3px 5px; cursor:pointer; max-width:150px; text-overflow:ellipsis; white-space:nowrap; overflow:hidden; }
.safelink-stops button { margin-inline-end:.4rem; }

#state-view select[aria-label="Map view"], #state-view select[aria-label="Nearby radius"] { padding: .4rem; color: #352322; background: #fff6e9; border: 1px solid #aa857c; border-radius: 5px; }
.safelink-nearby { max-height: 15rem; overflow: auto; padding-inline-start: 1.4rem; }
.safelink-nearby:empty { display: none; }
.safelink-nearby li { padding: .25rem 0; }
.safelink-nearby button { font: inherit; cursor: pointer; color: inherit; text-align: left; }
.safelink-nearby a { margin-inline-start: .55rem; font-size: .78em; }
.safelink-imagery-credit { display: block; font-size: .68rem; }
.safelink-imagery-credit[hidden] { display: none; }

.safelink-has-dock, .safelink-has-dock * { font-family: "Nunito", sans-serif !important; }
.safelink-has-dock #brand-title { font-weight: 900; }
.atlas-sub { position: relative; }
.atlas-sub[data-typing="true"] { color: transparent !important; }
.atlas-sub[data-typing="true"]::after { content: attr(data-visible-copy); position: absolute; inset: 0; color: #54192c; }
#intro .atlas-graphic .atlas-piece { animation: safelink-piece-in 1.85s both; }
#intro .atlas-piece:nth-child(2) { --piece-x: -36px; --piece-y: 20px; animation-delay: .18s; }
#intro .atlas-piece:nth-child(3) { --piece-x: 34px; --piece-y: -25px; animation-delay: .34s; }
#intro .atlas-piece:nth-child(4) { --piece-x: 8px; --piece-y: 28px; animation-delay: .5s; }
@keyframes safelink-piece-in {
  from { opacity: 0; translate: var(--piece-x, -24px) var(--piece-y, -25px); scale: .82; }
  to { translate: 0 0; scale: 1; }
}
@media (prefers-reduced-motion: reduce) {
  #intro .atlas-graphic .atlas-piece { animation: none; }
}
#call-replay:not([hidden]) { margin-top: .45rem; }
#call-audio-state { display: block; color: #f3d9df; font-size: .82rem; }
#call-audio-state:empty { display: none; }


.safelink-has-dock { background-color: #f6efe4; color: #24201d; }
.safelink-has-dock #intro { position: relative; isolation: isolate; background: #f5e9d9; color: #352322; border-block: 1px solid #b99b87; }
.safelink-has-dock #intro::before { content: ""; position: absolute; inset: clamp(7px, 2vw, 24px); border: 1px solid #ad8a75; pointer-events: none; z-index: -1; }
.safelink-has-dock #brand-title { font-family: "Nunito", sans-serif; font-weight: 600; font-style: italic; letter-spacing: -.07em; color: #54192c; }
.safelink-has-dock .atlas-top { background: #fcf6eb; border-bottom: 1px solid #a68176; }
.safelink-has-dock .state-intro h2, .safelink-has-dock .ride-head h2, .safelink-has-dock .journey h1 { font-family: "Nunito", sans-serif; font-weight: 600; color: #54192c; }
.safelink-has-dock .state-mapcard, .safelink-has-dock .state-card, .safelink-has-dock .j-card { border-color: #c9aea1; border-radius: 4px; box-shadow: 4px 4px 0 #e7d7ca; }
.safelink-has-dock .ride-settings { background: #fff6e9; border: 1px solid #9c6f70; border-radius: 8px; }
.safelink-has-dock .ride-screen { background: #271922; }
.safelink-has-dock .ride-screen #ride-pickup, .safelink-has-dock .call-mute, .safelink-has-dock .call-replies button { color: #fff5ee; background: #472638; border-color: #b18292; }
.safelink-has-dock .call-mute:hover, .safelink-has-dock .call-replies button:hover { background: #66374f; }
#call-type { margin: .6rem 0; }
#call-type:not([hidden]) { display: flex; gap: .4rem; flex-wrap: wrap; justify-content: center; }
#call-type input { flex: 1 1 170px; min-width: 0; padding: .6rem; background: #fff6e9; color: #271922; border: 1px solid #ad8896; border-radius: .35rem; font: inherit; }

.safelink-dock { display: none; }
.safelink-connectivity { display: flex; flex-wrap: wrap; align-items: center; gap: .4rem .9rem; margin: .1rem auto .9rem; font-size: .78rem; font-weight: 850; color: #3d4936; }
.safelink-connectivity span { display: inline-flex; align-items: center; gap: .4rem; }
.safelink-connectivity [hidden] { display: none; }
.safelink-connectivity span::before { content: ""; display: block; width: .48rem; height: .48rem; border-radius: 50%; background: #507741; }
#safelink-network[data-online="false"]::before { background: #98622c; }
#safelink-cache { color: #59634d; }
.safelink-has-dock #workspace, .safelink-has-dock #journey { scroll-margin-top: 4.5rem; }

.ride-settings { padding: clamp(18px, 4vw, 26px); }
.ride-head h2 { font-size: 1.55rem; }
.ride-settings .ride-icon, .ride-settings input, .ride-settings select, .ride-settings .ride-primary { min-height: 44px; }
.ride-settings .ride-icon { width: 44px; }
.ride-settings .ride-audio input { min-height: 0; }
.ride-settings .call-options { margin-top: .85rem; }
.call-cloud { margin-top: .8rem; padding: .7rem .85rem; border: 1px solid #c7ceba; border-radius: 10px; background: #edf0e3; }
.call-cloud label { display: grid; gap: .3rem; font-size: .83rem; font-weight: 850; }
.call-cloud input { width: 100%; padding: 6px 9px; color: #263020; background: #fffdf5; border-radius: 7px; border: 1px solid #a8b29e; font: inherit; }
.call-cloud p { margin: .55rem 0 0; font-size: .76rem; }
#call-setup-note:empty { display: none; }
.ride-screen .ride-display { padding-top: clamp(42px, 11svh, 110px); padding-bottom: max(26px, env(safe-area-inset-bottom)); }
.ride-screen .ride-avatar { width: 86px; height: 86px; border: 1px solid #657468; box-shadow: 0 0 0 10px #2c3831; }
.ride-screen[data-live="true"] .ride-avatar { border-color: #91deb2; }
.ride-screen #ride-pickup { font-size: .87rem; font-weight: 850; color: #d2e5d9; padding: .5rem .85rem; background: #29382f; border-radius: 22px; max-width: 340px; }
.call-voice-tools { width: min(100%, 360px); margin-top: 1.1rem; }
.call-replies { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; }
.call-replies[hidden] { display: none; }
.call-replies button, .call-mute { font: inherit; font-size: .83rem; font-weight: 850; min-height: 44px; padding: .45rem .82rem; color: #f1f6ef; border: 1px solid #66776b; background: #202e26; border-radius: 24px; }
.call-replies button:hover, .call-mute:hover { background: #33473b; }
.call-mute[aria-pressed="true"] { border-color: #fed395; color: #fed395; }
.call-caption { min-height: 1.6em; margin: .65rem 0 0; color: #d6e0d5; }
.call-caption:empty { display:none; }
.ride-screen .ride-controls { padding-top: 3rem; padding-bottom: .7rem; }
.ride-screen .ride-controls button { min-width: 111px; min-height: 52px; }

@media (max-width: 740px) {
  .safelink-has-dock { padding-bottom: calc(65px + env(safe-area-inset-bottom)); }
  .safelink-dock { position: fixed; z-index: 29; bottom: 0; left: 0; right: 0; display: grid; grid-template-columns: repeat(4,minmax(0,1fr)); padding: 5px max(7px, env(safe-area-inset-right)) calc(5px + env(safe-area-inset-bottom)) max(7px, env(safe-area-inset-left)); gap: 3px; border-top: 1px solid #cdd2bd; background: #f8f6eb; box-shadow: 0 -5px 22px #303b2823; }
  .safelink-dock button { display: grid; min-height: 48px; place-content: center; justify-items: center; gap: 1px; border: 0; border-radius: 7px; background: transparent; color: #293824; font: inherit; font-size: .74rem; font-weight: 900; }
  .safelink-dock button span { font-size: 1.12rem; line-height: 1.05; }
  .safelink-dock button:last-child { background: #f0e2dc; color: #742a27; }
  .safelink-dock button:focus-visible { outline: 2px solid #385d36; outline-offset: -2px; }
  .safelink-upgrade #ride-open, .safelink-upgrade #top-sos { display: none; }
  .ride-timer { bottom: calc(66px + env(safe-area-inset-bottom)); }
}

.call-cloud .call-preview { display: flex; }
.call-cloud .call-preview input { width: 17px; min-height: 17px; }
"""

CLIPS = r"""
/* English fallback clips generated with the Flite SLT voice. */
window.safeLinkRideClips = {
  "hello": "data:audio/mpeg;base64,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",
  "stay": "data:audio/mpeg;base64,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",
  "wait": "data:audio/mpeg;base64,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",
  "bye": "data:audio/mpeg;base64,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"
};
"""

LIVE = r"""
(() => {
  "use strict";
  const base = new URL("./", document.currentScript.src);
  const socketURL = "wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContentConstrained";
  const Audio = window.AudioContext || window.webkitAudioContext;

  async function startGemini({ endpoint, code, lang, preview, signal, onState, onFallback }) {
    if (!Audio || (!preview && (!window.AudioWorkletNode || !navigator.mediaDevices?.getUserMedia))) {
      onFallback("Live microphone audio is unavailable on this device.");
      return;
    }
    const context = new Audio();
    const activeAudio = new Set();
    const sessionAbort = new AbortController();
    let stream, socket, source, worklet, timer, finish, next = 0, ready = false, muted = false, stopped = false;
    const stopPlayback = () => {
      for (const audio of activeAudio) {
        audio.onended = null;
        audio.stop();
      }
      activeAudio.clear();
      next = 0;
    };
    function stop() {
      if (stopped) return;
      stopped = true;
      sessionAbort.abort();
      signal.removeEventListener("abort", stop);
      clearTimeout(timer);
      clearTimeout(finish);
      stopPlayback();
      worklet?.disconnect();
      source?.disconnect();
      stream?.getTracks().forEach(track => track.stop());
      if (socket && socket.readyState < WebSocket.CLOSING) socket.close();
      context.close().catch(() => {});
    }
    function fail(message) {
      if (stopped) return;
      stop();
      onFallback(message);
    }
    function send(message) {
      if (socket?.readyState === WebSocket.OPEN) socket.send(JSON.stringify(message));
    }
    signal.addEventListener("abort", stop, { once: true });
    if (signal.aborted) {
      stop();
      return;
    }
    timer = setTimeout(() => fail("Live voice timed out. Use the call replies below."), 16000);

    try {
      await context.resume();
      if (stopped) return;
      if (!preview) {
        stream = await navigator.mediaDevices.getUserMedia({
          audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true },
        });
        if (stopped) {
          stream.getTracks().forEach(track => track.stop());
          return;
        }
        await context.audioWorklet.addModule(new URL("mic-worklet.js?v=1", base));
        if (stopped) return;
      }
      const tokenURL = new URL(endpoint);
      tokenURL.searchParams.set("lang", lang);
      const response = await fetch(tokenURL, {
        method: "POST",
        headers: { Authorization: "Bearer " + code },
        signal: sessionAbort.signal,
        cache: "no-store",
        redirect: "error",
      });
      if (response.status === 401) return fail("That demo code did not match. The call replies are still available.");
      if (response.status === 429) return fail("Live voice limit reached. Use the call replies below.");
      if (!response.ok) return fail("Live voice is unavailable. Use the call replies below.");
      const { token, setup } = await response.json();
      if (!token || !setup || stopped) return fail("Live voice is unavailable. Use the call replies below.");
      socket = new WebSocket(socketURL + "?access_token=" + encodeURIComponent(token));
      socket.binaryType = "arraybuffer";
      socket.onopen = () => send({ setup });
      socket.onerror = () => fail("Live voice disconnected. Use the call replies below.");
      socket.onclose = () => fail("Live voice disconnected. Use the call replies below.");
      socket.onmessage = (event) => {
        if (stopped) return;
        let message;
        try {
          message = JSON.parse(typeof event.data === "string" ? event.data : new TextDecoder().decode(event.data));
        } catch {
          return;
        }
        if (message.setupComplete && !ready) {
          ready = true;
          clearTimeout(timer);
          finish = setTimeout(() => fail("Live voice finished. You can stay on the call with the replies below."), 150000);
          send({ realtimeInput: { text: "Start the simulated call with a short hello in the selected language." } });
          if (preview) {
            onState("Gemini voice preview · mic off");
            return;
          }
          source = context.createMediaStreamSource(stream);
          worklet = new AudioWorkletNode(context, "safelink-mic", { channelCount: 1, channelCountMode: "explicit" });
          worklet.port.onmessage = ({ data }) => {
            if (stopped || muted || socket.bufferedAmount > 128000) return;
            send({ realtimeInput: { audio: { mimeType: "audio/pcm;rate=16000", data: btoa(String.fromCharCode(...data)) } } });
          };
          source.connect(worklet).connect(context.destination);
          onState("Live voice · mic on", (nextMuted) => {
            muted = nextMuted;
            stream.getAudioTracks().forEach(track => { track.enabled = !muted; });
            if (muted) send({ realtimeInput: { audioStreamEnd: true } });
          });
        }
        const content = message.serverContent;
        if (content?.interrupted) stopPlayback();
        for (const part of content?.modelTurn?.parts || []) {
          const blob = part.inlineData;
          if (!blob?.mimeType?.startsWith("audio/pcm") || !blob.data) continue;
          const bytes = Uint8Array.from(atob(blob.data), x => x.charCodeAt(0));
          const rate = Number(blob.mimeType.match(/rate=(\d+)/)?.[1]) || 24000;
          const view = new DataView(bytes.buffer), length = bytes.length >> 1;
          if (!length) continue;
          const buffer = context.createBuffer(1, length, rate);
          const samples = buffer.getChannelData(0);
          for (let i = 0; i < length; i++) samples[i] = view.getInt16(i * 2, true) / 32768;
          const audio = context.createBufferSource();
          audio.buffer = buffer;
          audio.connect(context.destination);
          activeAudio.add(audio);
          onState(null, undefined, true);
          audio.onended = () => activeAudio.delete(audio);
          next = Math.max(context.currentTime + 0.02, next);
          audio.start(next);
          next += buffer.duration;
        }
        if (message.goAway) fail("Live voice is ending. The call replies are ready.");
      };
    } catch (error) {
      const micDenied = error.name === "NotAllowedError" || error.name === "NotFoundError";
      fail(micDenied ? "Microphone unavailable. Use the call replies below." : "Could not connect live voice. Use the call replies below.");
    }
  }
  window.safeLinkLiveVoice = startGemini;
})();
"""

UPGRADE = r"""
(() => {
  "use strict";
  const base = new URL("./", document.currentScript.src);
  const endpoint = document.currentScript.dataset.voiceEndpoint;
  const el = id => document.getElementById(id);
  const settings = el("ride-settings"), screen = el("ride-screen"), form = el("ride-form");
  const audio = new Audio();
  let plan, session, mute, muted = false;
  const lines = {
    en: {
      hello: "Hello. I am here. Can you hear me?",
      stay: "Of course. I will stay on the line.",
      wait: "Take your time. I am still here.",
      bye: "Okay. Talk to you soon.",
    },
    ta: {
      hello: "ஹலோ, நான் பேசுறேன். கேட்குதா?",
      stay: "சரி, நான் லைனிலேயே இருக்கேன்.",
      wait: "அவசரம் இல்லை. நான் லைனில் இருக்கேன்.",
      bye: "சரி, அப்புறம் பேசலாம்.",
    },
  };

  el("ride-title").textContent = "Ride call";
  settings.querySelector(":scope > form > p").textContent = "Stage an incoming call with a voice that can stay on the line.";
  el("ride-pickup").textContent = "";
  el("ride-pickup").setAttribute("role", "status");
  el("ride-pickup").classList.add("call-status");
  el("ride-pickup").insertAdjacentHTML("afterend", `
    <div id="call-voice-tools" class="call-voice-tools" data-tamil-clips="__TAMIL_CLIPS__" hidden>
      <button type="button" id="call-talk" class="call-mute" hidden>Tap to speak</button>
      <button type="button" id="call-mute" class="call-mute" aria-pressed="false" hidden>Mute mic</button>
      <meter id="call-level" min="0" max="1" value="0" aria-label="Microphone level" hidden></meter>
      <div id="call-type" hidden>
        <input id="call-message" type="text" aria-label="Type what you want to say" placeholder="Type what you want to say" maxlength="160" autocomplete="off">
        <button type="button" id="call-send" class="call-mute">Speak reply</button>
      </div>
      <div class="call-replies" role="group" aria-label="Play a staged reply">
        <button type="button" data-line="stay">Stay on the line</button>
        <button type="button" data-line="wait">Give me a moment</button>
        <button type="button" data-line="bye">Talk soon</button>
      </div>
      <p id="call-caption" class="call-caption" role="status"></p>
      <button type="button" id="call-replay" class="call-mute" hidden>Replay reply</button>
      <small id="call-audio-state" role="status"></small>
    </div>`);
  el("ride-ring").closest("label").insertAdjacentHTML("beforebegin", `
    <div class="ride-fields call-options">
      <label for="call-mode">Voice<select id="call-mode">
        <option value="browser">Interactive voice</option>
        <option value="offline">Offline replies</option>
        <option value="live">Gemini Live</option>
        <option value="silent">Silent screen</option>
      </select></label>
      <label for="call-language">Language<select id="call-language">
        <option value="en">English</option>
        <option value="ta">தமிழ்</option>
        <option value="mixed">Tanglish</option>
      </select></label>
    </div>
    <div id="call-cloud" class="call-cloud" hidden>
      <label for="call-code">Demo access code
        <input id="call-code" maxlength="128" type="password" autocomplete="off" spellcheck="false">
      </label>
      <label class="ride-audio call-preview"><input id="call-preview" type="checkbox"> Preview voice with mic off</label>
      <p id="call-privacy">Answering uses your microphone and streams audio to Google. Free-tier inputs may be used to improve Google’s products. Use fictional details.</p>
    </div>`);
  el("ride-ring").closest("label").insertAdjacentHTML("afterend", '<p id="call-setup-note" class="ride-meta" role="status"></p>');
  form.querySelector(".ride-meta:last-child").textContent = "Simulated call only. Use SOS to reach real help. Keep SafeLink open for a scheduled ring.";

  const mode = el("call-mode"), language = el("call-language"), code = el("call-code");
  function describeMode() {
    const live = mode.value === "live";
    el("call-cloud").hidden = !live || !endpoint;
    code.required = live && !!endpoint;
    language.querySelector('[value="mixed"]').hidden = !live;
    if (!live && language.value === "mixed") language.value = "en";
    el("call-setup-note").textContent = live
      ? (endpoint ? "Live voice uses internet. Offline replies are available if the connection drops." : "Gemini Live is awaiting server setup. This call will use offline replies.")
      : mode.value === "offline" && language.value === "ta" ? "Tamil audio needs a Tamil voice installed. Replies also appear on screen." : mode.value === "browser" ? "Tap to speak after answering. Your browser may process speech online. Use fictional details." : "";
  }
  const preview = el("call-preview");
  preview.addEventListener("change", () => {
    el("call-privacy").textContent = preview.checked
      ? "This preview sends a sample line to Gemini. The microphone stays off."
      : "Answering uses your microphone and streams audio to Google. Free-tier inputs may be used to improve Google’s products. Use fictional details.";
  });
  mode.addEventListener("change", describeMode);
  language.addEventListener("change", describeMode);
  describeMode();

  function pauseVoice() {
    audio.pause();
    window.speechSynthesis?.cancel();
  }
  function say(key) {
    if (!plan) return;
    const lang = plan.lang === "ta" ? "ta" : "en";
    const text = lines[lang][key];
    el("call-caption").textContent = text;
    el("call-caption").lang = lang;
    pauseVoice();
    if (lang === "en" && window.safeLinkRideClips?.[key]) {
      audio.src = window.safeLinkRideClips[key];
      audio.play().catch(() => {});
      return;
    }
    if (lang === "ta" && el("call-voice-tools").dataset.tamilClips === "true") {
      playTamil(key, text);
      return;
    }
    if (!window.speechSynthesis || !window.SpeechSynthesisUtterance) return;
    const voice = speechSynthesis.getVoices().find(candidate => candidate.localService && candidate.lang.toLowerCase().startsWith(lang));
    if (!voice) return;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = voice;
    utterance.lang = voice.lang;
    speechSynthesis.speak(utterance);
  }
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let listener;
  const talk = el("call-talk");
  const responses = [
    [/\b(where|location|pickup|pick up)\b|எங்க|இடம்/i,
      "Let's meet at the main entrance, near the lights.", "வெளிச்சம் இருக்கும் பிரதான வாசல் பக்கம் சந்திப்போம்."],
    [/\b(when|how long|minutes?|eta)\b|எப்ப|நிமிஷ/i,
      "About five minutes. I'll stay on the line while you wait.", "இன்னும் ஐந்து நிமிஷம். அதுவரை லைனில் இருக்கேன்."],
    [/\b(wait|stay|hold)\b|இரு|காத்து/i,
      "Sure. Take your time. I'm right here.", "சரி, அவசரம் இல்லை. நான் லைனில் இருக்கேன்."],
    [/\b(bye|goodbye|thanks)\b|நன்றி/i,
      "Okay, talk soon.", "சரி, அப்புறம் பேசலாம்."],
  ];
  const typed = el("call-type"), messageField = el("call-message");
  const replay = el("call-replay"), audioState = el("call-audio-state");
  let repeatReply;
  function setReplay(play) {
    repeatReply = play;
    replay.hidden = false;
  }
  replay.addEventListener("click", () => { if (screen.open) repeatReply?.(); });
  audio.addEventListener("timeupdate", () => {
    if (!audio.paused && audio.currentTime > .08 && audio.src.includes("/safelink-ta-"))
      audioState.textContent = "Tamil audio playing";
  });
  audio.addEventListener("ended", () => {
    if (audio.src.includes("/safelink-ta-")) audioState.textContent = "Tamil audio played";
  });
  function speakReply(text, tamil) {
    setReplay(() => { pauseVoice(); speakReply(text, tamil); });
    if (!window.SpeechSynthesisUtterance || !window.speechSynthesis) return;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = tamil ? "ta-IN" : "en-IN";
    utterance.onstart = () => { audioState.textContent = "Voice reply playing"; };
    utterance.onend = () => { audioState.textContent = "Voice reply played"; };
    utterance.onerror = event => {
      if (!["canceled", "interrupted"].includes(event.error)) audioState.textContent = "Device voice unavailable. Read the reply above.";
    };
    const voice = speechSynthesis.getVoices().find(item => item.lang.toLowerCase().split(/[-_]/)[0] === (tamil ? "ta" : "en"));
    if (voice) utterance.voice = voice;
    speechSynthesis.speak(utterance);
  }
  function playTamil(key, text) {
    setReplay(() => { pauseVoice(); playTamil(key, text); });
    audioState.textContent = "Loading Tamil audio…";
    audio.src = new URL("safelink-ta-" + key + ".wav", base).href;
    audio.play().catch(() => { if (screen.open && plan?.lang === "ta") speakReply(text, true); });
  }
  function replyToSpeech(text, tamil) {
    const match = responses.findIndex(([pattern]) => pattern.test(text));
    const message = responses[match]?.[tamil ? 2 : 1] ||
      (tamil ? "கேட்குது. எங்கே சந்திக்கணும், எப்போ வருவேன், அல்லது லைனில் இருக்கணுமான்னு கேளுங்க." :
        "I hear you. Ask where to meet, how long I'll be, or ask me to stay on the line.");
    el("call-caption").textContent = message;
    el("call-caption").lang = tamil ? "ta" : "en";
    pauseVoice();
    if (tamil && el("call-voice-tools").dataset.tamilClips === "true") {
      playTamil(match < 0 ? "prompt" : "intent-" + match, message);
    } else {
      speakReply(message, tamil);
    }
  }
  function sendTyped() {
    if (plan?.mode !== "browser" || !messageField.value.trim()) return;
    stopListening();
    el("ride-pickup").textContent = "Interactive voice · reply";
    replyToSpeech(messageField.value.trim(), plan.lang === "ta");
    messageField.value = "";
  }
  el("call-send").addEventListener("click", sendTyped);
  messageField.addEventListener("keydown", event => {
    if (event.key !== "Enter" || event.isComposing) return;
    event.preventDefault();
    sendTyped();
  });
  const micLevel = el("call-level");
  let recordingTimer, inputStream, inputAudio, levelFrame;
  function endLevel() {
    cancelAnimationFrame(levelFrame);
    inputStream?.getTracks().forEach(track => track.stop());
    inputAudio?.close().catch(() => {});
    inputStream = inputAudio = null;
    micLevel.value = 0;
    micLevel.hidden = true;
  }
  async function measureLevel(active) {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext || !navigator.mediaDevices?.getUserMedia) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({audio:true});
      if (listener !== active) { stream.getTracks().forEach(track => track.stop()); return; }
      inputStream = stream;
      inputAudio = new AudioContext();
      const analyser = inputAudio.createAnalyser();
      analyser.fftSize = 256;
      inputAudio.createMediaStreamSource(stream).connect(analyser);
      await inputAudio.resume();
      const samples = new Float32Array(analyser.fftSize);
      const tick = () => {
        if (listener !== active) return;
        analyser.getFloatTimeDomainData(samples);
        micLevel.hidden = false;
        micLevel.value = Math.min(1, 6 * Math.sqrt(samples.reduce((sum,n) => sum+n*n,0)/samples.length));
        levelFrame = requestAnimationFrame(tick);
      };
      tick();
    } catch { if (listener === active) endLevel(); }
  }
  talk.addEventListener("click", () => {
    if (!plan || plan.mode !== "browser" || !Recognition) return;
    if (listener) { stopListening(); el("ride-pickup").textContent = "Tap to speak again"; return; }
    pauseVoice();
    const active = new Recognition();
    const tamil = plan.lang === "ta";
    active.lang = tamil ? "ta-IN" : "en-IN";
    active.interimResults = false;
    active.continuous = false;
    const label = el("ride-pickup");
    const finish = (message, transcript) => {
      if (listener !== active) return;
      stopListening();
      label.textContent = message;
      if (transcript) replyToSpeech(transcript,tamil);
    };
    active.onresult = event => finish("Interactive voice · reply",event.results[0][0].transcript);
    active.onerror = () => finish("Speech recognition stalled. Try again or type your question.");
    active.onend = () => finish("No speech heard. Tap to try again.");
    listener = active;
    talk.textContent = "Stop listening";
    label.textContent = "Listening…";
    recordingTimer = setTimeout(() => finish("Listening timed out. Tap to try again."),11000);
    try { active.start(); measureLevel(active); } catch { active.onerror(); }
  });
  function stopListening() {
    const active = listener;
    listener = null;
    clearTimeout(recordingTimer);
    endLevel();
    talk.textContent = "Tap to speak";
    active?.abort();
  }
  function wipeSession() {
    stopListening();
    talk.hidden = true;
    typed.hidden = true;
    replay.hidden = true;
    repeatReply = null;
    audioState.textContent = "";
    messageField.value = "";
    session?.abort();
    session = null;
    mute = null;
    muted = false;
    pauseVoice();
    el("call-mute").hidden = true;
    el("call-mute").textContent = "Mute mic";
    el("call-mute").setAttribute("aria-pressed", "false");
    el("call-caption").textContent = "";
    screen.removeAttribute("data-live");
    screen.removeAttribute("data-audio");
    if (plan) plan.code = "";
    plan = null;
  }
  form.addEventListener("submit", () => {
    wipeSession();
    plan = { mode: mode.value, lang: language.value, code: code.value.trim(), preview: preview.checked };
    code.value = "";
  }, { capture: true });
  settings.addEventListener("close", () => { code.value = ""; });
  el("ride-answer").addEventListener("click", () => {
    const selected = plan || { mode: "offline", lang: "en" };
    const tools = el("call-voice-tools"), label = el("ride-pickup");
    const replies = tools.querySelector(".call-replies");
    tools.hidden = selected.mode === "silent";
    label.hidden = selected.mode === "silent";
    if (selected.mode === "silent") return;
    const fallback = (message, hello = false) => {
      if (!screen.open || plan !== selected) return;
      label.textContent = message;
      replies.hidden = false;
      el("call-mute").hidden = true;
      screen.removeAttribute("data-live");
      if (hello) say("hello");
    };
    if (selected.mode === "browser") {
      const supported = !!Recognition;
      typed.hidden = false;
      fallback(supported ? "Interactive voice · tap to speak" : "Speech recognition is unavailable. Type what you want to say.", true);
      talk.hidden = !supported;
      return;
    }
    if (selected.mode !== "live" || !endpoint || !navigator.onLine || !window.safeLinkLiveVoice) {
      fallback("Offline replies", true);
      return;
    }
    label.textContent = "Connecting live voice…";
    replies.hidden = true;
    session = new AbortController();
    const access = selected.code;
    selected.code = "";
    window.safeLinkLiveVoice({
      endpoint, code: access, lang: selected.lang, preview: selected.preview, signal: session.signal,
      onState(message, toggle, audioReceived) {
        if (audioReceived) {
          screen.dataset.audio = "received";
          if (selected.preview) label.textContent = "Gemini replied · mic off";
          return;
        }
        label.textContent = message;
        el("call-mute").hidden = !toggle;
        screen.dataset.live = "true";
        mute = toggle;
      },
      onFallback: fallback,
    }).catch(() => fallback("Live voice is unavailable. Use the call replies below."));
  });
  el("call-mute").addEventListener("click", () => {
    if (!mute) return;
    muted = !muted;
    mute(muted);
    el("ride-pickup").textContent = muted ? "Live voice · mic muted" : "Live voice · mic on";
    el("call-mute").textContent = muted ? "Unmute mic" : "Mute mic";
    el("call-mute").setAttribute("aria-pressed", String(muted));
  });
  for (const button of screen.querySelectorAll("[data-line]")) {
    button.addEventListener("click", () => say(button.dataset.line));
  }
  for (const id of ["ride-cancel", "ride-decline", "ride-hangup"]) el(id).addEventListener("click", wipeSession);
  screen.addEventListener("cancel", wipeSession);
  screen.addEventListener("close", () => { if (!screen.open) wipeSession(); });
  window.addEventListener("pagehide", wipeSession);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) stopListening();
    if (!document.hidden || !session || session.signal.aborted) return;
    session.abort();
    mute = null;
    el("call-mute").hidden = true;
    screen.removeAttribute("data-live");
    el("ride-pickup").textContent = "Live voice stopped while SafeLink was in the background.";
    screen.querySelector(".call-replies").hidden = false;
  });

  const top = el("app-brand").closest("header");
  top.classList.add("safelink-upgrade");
  top.insertAdjacentHTML("afterend", `
    <nav class="safelink-dock" aria-label="Quick actions">
      <button type="button" data-jump="state"><span aria-hidden="true">⌖</span>Plan</button>
      <button type="button" data-jump="journey"><span aria-hidden="true">↓</span>Offline</button>
      <button type="button" data-jump="ride"><span aria-hidden="true">◉</span>Ride call</button>
      <button type="button" data-jump="sos"><span aria-hidden="true">!</span>SOS</button>
    </nav>`);
  el("workspace").querySelector(".workspace-nav").insertAdjacentHTML("afterend", `
    <div class="safelink-connectivity aa-width">
      <span id="safelink-network"></span>
      <span id="safelink-cache" role="status" hidden></span>
    </div>`);
  document.body.classList.add("safelink-has-dock");
  const introCopy = document.querySelector("#intro .atlas-sub");
  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");
  if (introCopy && !reducedMotion.matches) {
    const copy = Array.from(introCopy.textContent.trim());
    let count = 0;
    introCopy.dataset.typing = "true";
    introCopy.dataset.visibleCopy = "";
    const tick = () => {
      if (reducedMotion.matches || count >= copy.length) {
        delete introCopy.dataset.typing;
        delete introCopy.dataset.visibleCopy;
        return;
      }
      introCopy.dataset.visibleCopy = copy.slice(0, ++count).join("");
      setTimeout(tick, 44);
    };
    setTimeout(tick, 230);
  }
  for (const button of document.querySelectorAll(".safelink-dock button")) {
    button.addEventListener("click", () => {
      const jump = button.dataset.jump;
      if (jump === "ride" || jump === "sos") {
        el(jump === "sos" ? "top-sos" : "ride-open").click();
      } else {
        el(jump + "-tab").click();
        el(jump === "state" ? "workspace" : "journey").scrollIntoView({ block: "start" });
      }
    });
  }
  function networkStatus() {
    const badge = el("safelink-network");
    badge.textContent = navigator.onLine ? "Connected to a network" : "Offline · Trichy maps and ride replies available";
    badge.dataset.online = String(navigator.onLine);
  }
  window.addEventListener("online", networkStatus);
  window.addEventListener("offline", networkStatus);
  networkStatus();

  const appRoot = new URL("../", base);
  if ("serviceWorker" in navigator && location.protocol !== "file:" &&
      (location.pathname === appRoot.pathname || location.pathname === appRoot.pathname + "index.html")) {
    const showOfflineStatus = async () => {
      const cache = await caches.open("safelink-kit-v14:" + appRoot.pathname);
      if (!await cache.match(appRoot)) return;
      const status = el("safelink-cache");
      status.textContent = "Offline kit saved";
      status.hidden = false;
    };
    navigator.serviceWorker.addEventListener("controllerchange", () => showOfflineStatus().catch(() => {}));
    navigator.serviceWorker.register(new URL("safelink-sw.js", appRoot), { scope: appRoot.pathname })
      .then(() => navigator.serviceWorker.ready)
      .then(showOfflineStatus)
      .catch(() => {});
  }
})();
"""

WORKLET = r"""
class SafeLinkMic extends AudioWorkletProcessor {
  constructor() {
    super();
    this.bytes = new Uint8Array(1280);
    this.view = new DataView(this.bytes.buffer);
    this.offset = 0;
    this.phase = 0;
    this.sum = 0;
    this.count = 0;
  }
  process(inputs) {
    const input = inputs[0]?.[0];
    if (!input) return true;
    for (const sample of input) {
      this.sum += sample;
      this.count++;
      this.phase += 16000;
      if (this.phase < sampleRate) continue;
      const bounded = Math.max(-1, Math.min(1, this.sum / this.count));
      this.view.setInt16(this.offset, Math.round(bounded * (bounded < 0 ? 32768 : 32767)), true);
      this.offset += 2;
      this.phase -= sampleRate;
      this.sum = 0;
      this.count = 0;
      if (this.offset === this.bytes.length) {
        this.port.postMessage(this.bytes);
        this.offset = 0;
      }
    }
    return true;
  }
}
registerProcessor("safelink-mic", SafeLinkMic);
"""

OFFLINE = r"""
"use strict";
const home = new URL("./", self.location.href);
const cacheKey = "safelink-kit-v14:" + home.pathname;
const assetURLs = [new URL("mic-worklet.js?v=1", home).href, ...["night-city.js","walk-toolkit.js","i18n-ta.json","manifest.webmanifest","safelink-icon.svg","impact.html","credits.html","night-assets/fonts.css",...__NIGHT_FILES__].map(path=>new URL(path,home).href), ...__TAMIL_ASSETS__.map(name => new URL(name, home).href)];
const pagePaths = [home.pathname, home.pathname + "index.html"];

self.addEventListener("install", event => {
  event.waitUntil(caches.open(cacheKey).then(async cache => {
    await cache.add(home.href);
    await Promise.allSettled([...new Set(assetURLs)].map(url=>cache.add(url)));
    await self.skipWaiting();
  }));
});
self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    const oldKeys = (await caches.keys()).filter(key => /^safelink-kit-v\d+:/.test(key) &&
      key.slice(key.indexOf(":") + 1) === home.pathname && key !== cacheKey);
    await Promise.all(oldKeys.map(key => caches.delete(key)));
    await self.clients.claim();
  })());
});
self.addEventListener("fetch", event => {
  const request = event.request, url = new URL(request.url);
  if (request.method !== "GET" || url.origin !== home.origin) return;
  if (request.mode === "navigate" && pagePaths.includes(url.pathname)) {
    event.respondWith((async () => {
      try {
        return await fetch(request);
      } catch {
        return await (await caches.open(cacheKey)).match(home) || Response.error();
      }
    })());
  } else if (assetURLs.includes(url.href)) {
    event.respondWith(caches.open(cacheKey).then(async cache => (await cache.match(request)) || fetch(request)));
  }
});
"""

def upgrade_atlas_map(atlas):
    start = atlas.index('  function contextFrom(json) {')
    end = atlas.index('  for (const key of ["start","end"])', start)
    context = atlas[start:end]
    left = context.index('  function contextFrom')
    right = context.index('  async function nearby()', left)
    context = context[:left] + r"""
  const nearbyRadius = document.createElement("select");
  nearbyRadius.setAttribute("aria-label", "Nearby radius");
  for (const km of [1.5, 3, 5]) nearbyRadius.add(new Option(km + " km", String(km * 1000), false, km === 3));
  el("state-refresh").before(nearbyRadius);
  const nearbyArea = document.createElement("select");
  nearbyArea.setAttribute("aria-label","Jump to Trichy area");
  nearbyArea.add(new Option("Jump to Trichy area",""));
  const localAreas = [["Central Trichy","trichy-data"],["Woraiyur","offline-data-woraiyur"],["Manapparai","offline-data-manapparai"],["Srirangam","offline-data-srirangam"],["Thillai Nagar","offline-data-thillai"]];
  for (const [label,id] of localAreas) nearbyArea.add(new Option(label,id));
  nearbyRadius.before(nearbyArea);
  nearbyArea.addEventListener("change", () => {
    const node = el(nearbyArea.value);
    if (!node) return;
    const [y,x] = JSON.parse(node.textContent).origin;
    if (streetReady) map.jumpTo({center:[x,y],zoom:14});
    else { lng=x; lat=y; zoom=8; invalidate(); }
    nearby();
  });
  const nearbyPlaces = document.createElement("ol");
  nearbyPlaces.className = "safelink-nearby";
  nearbyPlaces.setAttribute("aria-label", "Nearest mapped places");
  el("state-feature").after(nearbyPlaces);

  function distanceMeters(a,b) {
    const rad = Math.PI / 180;
    const h = Math.sin((b[1]-a[1])*rad/2)**2 +
      Math.cos(a[1]*rad)*Math.cos(b[1]*rad)*Math.sin((b[0]-a[0])*rad/2)**2;
    return 12742000 * Math.asin(Math.sqrt(Math.min(1,h)));
  }

  const search = document.createElement("form");
  search.className = "safelink-landmark-search";
  search.innerHTML = '<label>Search landmarks <input type="search" required minlength="2" maxlength="90" placeholder="Manapparai Railway Station"></label> <button>Search</button> <label><input type="checkbox" name="online"> Include OpenStreetMap online</label><p role="status"></p><ol></ol>';
  el("state-start").before(search);
  const field = search.querySelector('input[type="search"]');
  const status = search.querySelector('[role="status"]');
  const results = search.querySelector("ol");
  const localIndex = new Map();
  for (const [, id] of localAreas) {
    if (!el(id)) continue;
    const {origin:[y0,x0,sx,sy],places} = JSON.parse(el(id).textContent);
    for (const [label,kind,x,y,type,id] of places) {
      const osm="https://www.openstreetmap.org/"+type+"/"+id;
      localIndex.set(osm,{label,kind,point:[x0+x/sx,y0-y/sy],osm});
    }
  }
  const featuredPlaces=[["Rockfort (Rock Fort)","Landmark",78.69718,10.82806,"https://en.wikipedia.org/wiki/List_of_Monuments_of_National_Importance_in_Tiruchirapalli_circle"],["Main Guard Gate","Landmark",78.69338,10.8266,"https://www.wikidata.org/wiki/Q97481134"],["Thillai Nagar Bus Stop · 10th/11th Cross","Transit",78.68356,10.81815,"https://www.openstreetmap.org/node/4701652413"],["Beema Nagar Bus Stop","Transit",78.69044,10.80868,"https://in.near-place.com/beemanagar-bus-stop-heber-rd-beema-nagar-tiruchirappalli"],["KK Nagar Bus Station","Transit",78.69207,10.75734,"https://www.openstreetmap.org/node/4420664522"],["Anna Nagar · Corporation Open Stadium","Landmark",78.68342,10.81275,"https://in.near-place.com/trichy-corporation-open-stadium-sivaprakasam-road-anna-nagar-tiruchirappalli/es"],["Karumandapam Bus Stop","Transit",78.6706,10.7873,"https://www.distancesfrom.com/in/Karumandapam-Bus-Stop-latitude-longitude-Karumandapam-Bus-Stop-latitude-Karumandapam-Bus-Stop-longit/LatLongHistory/14443965.aspx"],["Bishop Heber College","College",78.67336,10.8156,"https://www.openstreetmap.org/way/120688995"],["National College","College",78.67343,10.79101,"https://www.openstreetmap.org/way/455766532"]].map(([label,category,x,y,source])=>({label,kind:category==="Transit"?"transit":"landmark",category,point:[x,y],osm:source,featured:true}));
  for (const place of featuredPlaces) localIndex.set(place.osm,place);
  const featuredPanel=document.createElement("details");
  featuredPanel.className="safelink-featured";
  featuredPanel.open=true;
  featuredPanel.innerHTML="<summary>Popular Trichy landmarks</summary><div></div>";
  search.after(featuredPanel);
  for (const place of featuredPlaces) {
    const button=document.createElement("button");
    button.type="button";button.textContent=place.label;
    button.onclick=()=>{
      if(streetReady)map.easeTo({center:place.point,zoom:Math.max(map.getZoom(),15)});
      else {[lng,lat]=place.point;invalidate();}
      showFeature(place,true);
    };
    featuredPanel.lastElementChild.append(button);
  }
  function renderSearch(items) {
    results.replaceChildren();
    for (const place of items.slice(0,10)) {
      const row = document.createElement("li");
      row.textContent=place.label+" ";
      for (const [role,label] of [["start","Set start"],["stop","Add stop"],["end","Set destination"]]) {
        const button=document.createElement("button");
        button.type="button"; button.textContent=label;
        button.setAttribute("aria-label",label+" "+place.label);
        button.onclick=()=>{
          setPlace(place,role);
          if (streetReady) map.easeTo({center:place.point,zoom:Math.max(14,map.getZoom())});
          else { [lng,lat]=place.point; invalidate(); }
          status.textContent=place.label+" selected.";
        };
        row.append(button);
      }
      results.append(row);
    }
  }
  const geocodes=new Map();
  let lookupAt=0;
  search.addEventListener("submit",async event=>{
    event.preventDefault();
    const query=field.value.normalize("NFKC").trim();
    if (query.length<2) return;
    const key=query.toLocaleLowerCase();
    const words=key.split(/\s+/);
    const pool=new Map([...localIndex,...features.filter(p=>p.osm).map(p=>[p.osm,p])]);
    const local=[...pool.values()].filter(p=>words.every(w=>p.label.normalize("NFKC").toLocaleLowerCase().includes(w)));
    const isOnline=search.elements.online.checked && navigator.onLine;
    renderSearch(local);
    status.textContent=local.length?local.length+" mapped matches.":"No bundled or nearby matches.";
    if (!isOnline) return;
    const submit=search.querySelector("button");
    if (submit.disabled) return;
    submit.disabled=true;
    try {
      let rows=geocodes.get(key);
      if (!rows) {
        if (Date.now()-lookupAt<1100) return;
        lookupAt=Date.now();
        status.textContent="Searching OpenStreetMap…";
        const params = new URLSearchParams({q:query+", Tamil Nadu, India",format:"jsonv2",countrycodes:"in",limit:"10",viewbox:"75.68,14.02,80.88,7.54",bounded:"1"});
        rows=await fetchJson("https://nominatim.openstreetmap.org/search?"+params);
        if (geocodes.size>=25) geocodes.delete(geocodes.keys().next().value);
        geocodes.set(key,rows);
      }
      if (field.value.normalize("NFKC").trim().toLocaleLowerCase()!==key) return;
      const found=new Map(local.map(p=>[p.osm,p]));
      for (const item of rows) {
        const point=[Number(item.lon),Number(item.lat)];
        if (!point.every(Number.isFinite)||!inState(point)||!["node","way","relation"].includes(item.osm_type)||!Number.isSafeInteger(Number(item.osm_id))) continue;
        const osm="https://www.openstreetmap.org/"+item.osm_type+"/"+item.osm_id;
        if (!found.has(osm)) found.set(osm,{point,osm,kind:item.type,label:item.display_name});
      }
      renderSearch([...found.values()]);
      status.textContent=found.size?found.size+" matching places · OpenStreetMap.":"No matches. Try adding the town name.";
    } catch { status.textContent="Online lookup unavailable. Bundled results remain available."; }
    finally { submit.disabled=false; }
  });

  function contextFrom(json, centre, radius) {
    const candidates = (Array.isArray(json?.elements) ? json.elements : []).flatMap(item => {
      const tags = item.tags || {};
      const point = [item.lon ?? item.center?.lon, item.lat ?? item.center?.lat];
      if (!point.every(Number.isFinite)) return [];
      const distance = distanceMeters(centre, point);
      if (distance > radius) return [];
      const kind = tags.highway === "street_lamp" ? "lights" : tags.amenity === "police" ? "police" :
        /^(hospital|clinic|doctors|pharmacy)$/.test(tags.amenity) || tags.healthcare ? "health" : "transit";
      const subtype = tags.amenity || (tags.highway === "bus_stop" ? "bus stop" : tags.healthcare || tags.railway || tags.public_transport);
      const name = tags["name:en"] || tags.name || tags["name:ta"];
      const label = String(name || (kind === "lights" ? nouns[kind] : subtype || nouns[kind])).replaceAll("_"," ").slice(0,120);
      return [{kind, point, label, distance, named: !!name, tags, osm: "https://www.openstreetmap.org/" + item.type + "/" + item.id}];
    }).sort((a,b) => a.distance-b.distance);
    const unique = [];
    for (const place of candidates) {
      if (place.named && unique.some(other => other.kind === place.kind && other.label.toLowerCase() === place.label.toLowerCase() &&
        Math.abs(other.distance-place.distance) < 80 && distanceMeters(other.point,place.point) < 80)) continue;
      unique.push(place);
    }
    return [...unique.filter(place => place.kind !== "lights").slice(0,180), ...unique.filter(place => place.kind === "lights").slice(0,100)];
  }
  function bundledNearby(centre, radius) {
    const known = new Map();
    for (const id of ["trichy-data","offline-data-woraiyur","offline-data-manapparai","offline-data-srirangam","offline-data-thillai"]) {
      const node = el(id);
      if (!node) continue;
      const {origin,places} = JSON.parse(node.textContent);
      const [lat0,lon0,sx,sy] = origin;
      for (const [label,category,x,y,type,id] of places) {
        const point = [lon0+x/sx,lat0-y/sy];
        const distance = distanceMeters(centre,point);
        if (distance > radius) continue;
        const kind = /hospital|clinic|pharmacy|health/i.test(category) ? "health" :
          /police/i.test(category) ? "police" : /station|bus|rail|taxi/i.test(category) ? "transit" : "landmark";
        known.set(type+"/"+id,{kind,point,label,distance,osm:"https://www.openstreetmap.org/"+type+"/"+id});
      }
    }
    for (const place of featuredPlaces) {
      const distance=distanceMeters(centre,place.point);
      if(distance<=radius)known.set(place.osm,{...place,distance});
    }
    return [...known.values()].sort((a,b)=>a.distance-b.distance);
  }
  function renderNearbyCounts() {
    for (const kind of Object.keys(palette)) {
      const counter = el("state-count-"+kind);
      if (counter) counter.textContent = features.length ? features.filter(f=>f.kind===kind).length : "—";
    }
  }
  function contextQuery([x,y], radius) {
    const near = "(around:" + radius + "," + y.toFixed(5) + "," + x.toFixed(5) + ")";
    const lampArea = "(around:" + Math.min(radius,1600) + "," + y.toFixed(5) + "," + x.toFixed(5) + ")";
    return '[out:json][timeout:12];(nwr["amenity"~"^(hospital|clinic|doctors|pharmacy|police|bus_station|taxi)$"]'+near+
      ';nwr["healthcare"~"^(hospital|clinic|doctor|doctors|pharmacy)$"]'+near+
      ';nwr["railway"~"^(station|halt)$"]'+near+';node["highway"="bus_stop"]'+near+
      ';nwr["public_transport"="station"]'+near+';);out center 700;node["highway"="street_lamp"]'+lampArea+';out body 350;';
  }
  async function findNearbyData(point, radius) {
    const query = "?data=" + encodeURIComponent(contextQuery(point,radius));
    try {
      return await fetchJson("https://overpass.private.coffee/api/interpreter"+query,14);
    } catch {
      return fetchJson("https://overpass-api.de/api/interpreter"+query,14);
    }
  }
  function renderNearby() {
    nearbyPlaces.replaceChildren();
    const places = features.filter(place => place.kind !== "lights").slice(0,12);
    for (const place of places) {
      const item = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = place.label + " · " + (place.distance < 1000 ? Math.round(place.distance) + " m" : (place.distance/1000).toFixed(1) + " km");
      button.addEventListener("click", () => {
        if (streetReady) map.easeTo({center:place.point,zoom:Math.max(map.getZoom(),15)});
        else { [lng,lat] = place.point; invalidate(); }
        showFeature(place);
      });
      const source = document.createElement("a");
      source.href = place.osm;
      source.target = "_blank";
      source.rel = "noopener";
      source.textContent = "OSM";
      source.setAttribute("aria-label","Open " + place.label + " on OpenStreetMap");
      item.append(button,source);
      nearbyPlaces.append(item);
    }
  }
""" + context[right:]
    context = context.replace('    contextPending=true;', r"""
    const radius=Number(nearbyRadius.value);
    const bundled=bundledNearby(p,radius);
    features=bundled;
    renderNearby();
    renderNearbyCounts();
    redrawn();
    nearbyRadius.disabled=true;
    nearbyArea.disabled=true;
    contextPending=true;""", 1)
    context = context.replace('p.map(v=>v.toFixed(3)).join(",")', 'p.map(v=>v.toFixed(5)).join(",")+":"+radius', 1)
    request_start = context.index('        const urls=[')
    request_end = context.index('        if (result.values', request_start)
    context = context[:request_start] + r"""
        const weatherUrl="https://api.open-meteo.com/v1/forecast?"+point+"&current=temperature_2m,precipitation,wind_speed_10m&timezone=Asia%2FKolkata";
        result={values:await Promise.allSettled([findNearbyData(p,radius),fetchJson(weatherUrl,13)]),time:Date.now()};
""" + context[request_end:]
    context = context.replace('result.values.every(value=>value.status==="fulfilled")', 'result.values[0].status==="fulfilled"')
    context = context.replace('contextFrom(osm.value):[];', 'contextFrom(osm.value,p,radius):bundled;\n      if (!features.length && bundled.length) features=bundled;\n      renderNearby();')
    context = context.replace('note("state-feature","");redrawn();', 'redrawn();')
    count_start = context.index('      for (const kind of Object.keys(palette))', context.index('const [osm,weather]'))
    count_end = context.index('      const current=', count_start)
    context = context[:count_start] + '      renderNearbyCounts();\n' + context[count_end:]
    context = context.replace('"Mapped feature service unavailable. Try again in a moment."', '(bundled.length ? "Live lookup unavailable. Showing bundled OpenStreetMap places near this centre." : "Live lookup unavailable and no bundled places near this centre.")')
    context = context.replace('"Mapped points within 1.8 km of the selected centre (up to 180). Select a dot for details."', '"OpenStreetMap places within "+radius/1000+" km of the queried centre. Distances are straight-line. Lamp coverage is sampled within 1.6 km."')
    context = context.replace('contextPending=false;refreshControls();','nearbyRadius.disabled=false;nearbyArea.disabled=false;contextPending=false;refreshControls();')
    atlas = atlas[:start] + context + atlas[end:]
    atlas = atlas.replace('  function showFeature(feature) {', r"""
  const stops = [];
  let namedStart = "", namedEnd = "";
  const stopList = document.createElement("div");
  stopList.className = "safelink-stops";
  stopList.setAttribute("aria-label","Route stops");
  el("state-end").after(stopList);
  el("state-clear").addEventListener("click", () => {
    stops.length=0; namedStart=""; namedEnd=""; renderStops(); refreshControls();
  });
  function renderStops() {
    stopList.replaceChildren();
    stops.forEach((stop,index) => {
      const button=document.createElement("button");
      button.type="button"; button.textContent=(index+1)+". "+stop.label+" ×";
      button.setAttribute("aria-label","Remove stop "+stop.label);
      button.onclick=()=>{ stops.splice(index,1); clearRoute(); renderStops(); refreshControls(); redrawn(); };
      stopList.append(button);
    });
  }
  function setPlace(feature, role) {
    if (!inState(feature.point)) return;
    if (role==="stop") {
      if (stops.length>=5 || stops.some(stop=>stop.osm===feature.osm)) return;
      stops.push(feature); renderStops();
    } else {
      setPicking(role); pick(feature.point);
      if (role==="start") namedStart=feature.label;
      else namedEnd=feature.label;
    }
    clearRoute(); refreshControls(); redrawn();
  }
  let placeLabels = [];
  function drawPlaceLabels() {
    placeLabels.forEach(marker=>marker.remove());
    placeLabels=[];
    if (!streetReady || map.getZoom()<12) return;
    const candidates = features.filter(place=>place.kind!=="lights" && place.named!==false);
    for (const place of candidates.slice(0,12)) {
      const button=document.createElement("button");
      button.type="button";
      button.className="safelink-place-label";
      button.textContent=place.label;
      button.onclick=event=>{event.stopPropagation(); if(picking) pick(place.point); else showFeature(place);};
      placeLabels.push(new maplibregl.Marker({element:button,anchor:"bottom",offset:[0,-6]}).setLngLat(place.point).addTo(map));
    }
  }
  function showFeature(feature) {""", 1)
    atlas = atlas.replace('note("state-feature",feature.label+" · "+nouns[feature.kind]+" · OpenStreetMap. Current conditions unverified.");', r"""
    const target=el("state-feature");
    target.hidden=false;
    target.textContent=feature.label+" · "+(nouns[feature.kind]||"Landmark")+" · Mapped place ";
    for (const [role,label] of [["start","Set start"],["stop","Add stop"],["end","Set destination"]]) {
      const button=document.createElement("button");
      button.type="button"; button.textContent=label;
      button.onclick=()=>setPlace(feature,role);
      target.append(button);
    }
    const facts=feature.tags||{};
    for (const [title,value] of [["Hours",facts.opening_hours],["Wheelchair access",facts.wheelchair],["Street",facts["addr:street"]],["Tamil name",facts["name:ta"]]]) {
      if (!value) continue;
      const line=document.createElement("small");
      line.textContent=title+" · "+value;
      target.append(line);
    }
    const link=(label,url)=>{
      const a=document.createElement("a");
      a.textContent=label; a.href=url; a.rel="noopener noreferrer"; a.target="_blank"; target.append(a);
    };
    if (feature.osm) link(feature.osm.includes("openstreetmap.org")?" OpenStreetMap record":" Coordinate source",feature.osm);
    if (/^Q\d+$/.test(facts.wikidata||"")) link(" Wikidata", "https://www.wikidata.org/wiki/"+facts.wikidata);
    if (distanceMeters([78.683,10.8],feature.point)<12000) link(" Trichy visitor guide", "https://en.wikivoyage.org/wiki/Tiruchirappalli");""", 1)
    atlas = atlas.replace('namePoint(start);','namedStart||namePoint(start);',1).replace('namePoint(end);','namedEnd||namePoint(end);',1)
    atlas = atlas.replace('if (picking==="start") start=point;','if (picking==="start") {start=point;namedStart="";}',1).replace('if (picking==="end") end=point;','if (picking==="end") {end=point;namedEnd="";}',1)
    atlas = atlas.replace('[start,end].map(p=>p.map(n=>n.toFixed(5))','[start,...stops.map(stop=>stop.point),end].map(p=>p.map(n=>n.toFixed(5))',1)
    atlas = atlas.replace('km+" km · "+travel','km+" km by "+(mode==="foot"?"walking":"road")+" · "+travel',1)
    atlas = atlas.replace('  function installLayer(target) {','  function installLayer(target) {\n    target.on("zoomend",drawPlaceLabels);',1)
    atlas = atlas.replace('renderNearbyCounts();','renderNearbyCounts();\n    drawPlaceLabels();')
    atlas = atlas.replace('const kind = tags.highway === "street_lamp" ? "lights" :','const kind = tags.highway === "street_lamp" ? "lights" : tags.tourism || tags.historic || tags.amenity==="place_of_worship" ? "landmark" :',1)
    atlas = atlas.replace("';nwr[\"public_transport\"=\"station\"]'+near+", """';nwr["tourism"~"^(attraction|museum)$"]["name"]'+near+';nwr["historic"]["name"]'+near+
      ';nwr["amenity"="place_of_worship"]["name"]'+near+';nwr["public_transport"="station"]'+near+""",1)
    atlas = atlas.replace(' + " m" : (place.distance/1000).toFixed(1) + " km");',' + " m" : (place.distance/1000).toFixed(1) + " km") + " direct from search centre";',1)

    atlas = atlas.replace('palette[feature.kind],', '(palette[feature.kind] || "#7e4775"),', 1)
    atlas = atlas.replace('color:palette[f.kind]', 'color:palette[f.kind] || "#7e4775"', 1)
    anchor = '  function resizeAndLoad() {'
    return atlas.replace(anchor, r"""
  const baseStyle = document.createElement("select");
  baseStyle.setAttribute("aria-label", "Map view");
  for (const [name,label] of [["street","Street"],["satellite","Satellite"],["hybrid","Hybrid"]])
    baseStyle.add(new Option(label,name));
  const imageryCredit = document.createElement("a");
  imageryCredit.href = "https://goto.arcgisonline.com/maps/World_Imagery";
  imageryCredit.target = "_blank";
  imageryCredit.rel = "noopener";
  imageryCredit.textContent = "Imagery © Esri, Vantor, Earthstar Geographics and GIS User Community";
  imageryCredit.hidden = true;
  imageryCredit.className = "safelink-imagery-credit";
  el("state-fit").after(baseStyle);
  el("state-live-source").after(imageryCredit);
  const backdrop = "safelink-imagery";
  let baseLayers = [];
  function prepareImagery(target) {
    baseLayers = target.getStyle().layers.map(layer => [layer.id, layer.type, layer.layout?.visibility || "visible"]);
    target.addSource(backdrop, {
      type:"raster", tileSize:256, maxzoom:19,
      tiles:["https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"]
    });
    const firstLabel = baseLayers.find(([,type]) => type === "symbol")?.[0];
    target.addLayer({id:backdrop,type:"raster",source:backdrop,layout:{visibility:"none"}}, firstLabel);
  }
  function chooseBasemap() {
    const style = baseStyle.value;
    if (!streetReady || !map.getLayer(backdrop)) {
      imageryCredit.hidden = true;
      if (style !== "street") note("state-mapnote","Imagery needs the online map. Start and destination can still be picked on the overview.");
      return;
    }
    for (const [id,type,visibility] of baseLayers) {
      map.setLayoutProperty(id,"visibility",style === "street" || (style === "hybrid" && type === "symbol") ? visibility : "none");
    }
    map.setLayoutProperty(backdrop,"visibility",style === "street" ? "none" : "visible");
    imageryCredit.hidden = style === "street";
    setMode(style === "street" ? "Live street map" : style === "hybrid" ? "Hybrid map" : "Satellite map",true);
  }
  baseStyle.addEventListener("change",chooseBasemap);
  window.addEventListener("offline", () => { imageryCredit.hidden = true; });
""" + anchor, 1).replace('          installLayer(target);','          prepareImagery(target);\n          installLayer(target);',1).replace('          setMode("Live street map",true);','          chooseBasemap();',1)


def upgrade_route_conditions(atlas):
    start = atlas.index("  async function findRoute() {")
    end = atlas.index("  const nearbyRadius", start)
    atlas = atlas[:start] + r"""
  const routeChoices = document.createElement("div");
  routeChoices.className = "safelink-route-choices";
  routeChoices.setAttribute("aria-label","Alternate routes");
  el("state-result").after(routeChoices);
  const conditionLegend = document.createElement("p");
  conditionLegend.textContent = "Green: mapped road surface meets the checks. Lighting is shown separately. Red: a concern was mapped or conditions need checking.";
  routeChoices.after(conditionLegend);

  async function routeConditions(routes) {
    const lines = routes.map(r=>r.line);
    const all = lines.flat();
    const bounds = all.reduce((b,[x,y])=>[Math.min(b[0],x),Math.min(b[1],y),Math.max(b[2],x),Math.max(b[3],y)],[Infinity,Infinity,-Infinity,-Infinity]);
    if (bounds.some(value=>!Number.isFinite(value)) || bounds[2]-bounds[0]>.15 || bounds[3]-bounds[1]>.15) return [];
    const queries = lines.map(line=>{
      const stride=Math.max(1,Math.ceil(line.length/90));
      const sampled=line.filter((_,i)=>i%stride===0);
      if (sampled.at(-1)!==line.at(-1)) sampled.push(line.at(-1));
      return 'way["highway"]["lit"](around:24,'+sampled.map(([x,y])=>y.toFixed(5)+","+x.toFixed(5)).join(",")+');'+
        'way["highway"]["surface"](around:24,'+sampled.map(([x,y])=>y.toFixed(5)+","+x.toFixed(5)).join(",")+');'+
        'way["highway"]["smoothness"](around:24,'+sampled.map(([x,y])=>y.toFixed(5)+","+x.toFixed(5)).join(",")+');';
    });
    const url="https://overpass.private.coffee/api/interpreter?data="+encodeURIComponent("[out:json][timeout:8];("+queries.join("")+");out geom 700;");
    try {
      const data=await fetchJson(url,9);
      return (data.elements||[]).flatMap(way=>(way.geometry||[]).slice(1).map((b,i)=>{
        const a=way.geometry[i];
        return {a:[a.lon,a.lat],b:[b.lon,b.lat],tags:way.tags||{}};
      }));
    } catch { return []; }
  }
  function pointToSegment(point,{a,b}) {
    const mx=111195*Math.cos(point[1]*Math.PI/180), my=111195;
    const x=(a[0]-point[0])*mx,y=(a[1]-point[1])*my;
    const dx=(b[0]-a[0])*mx,dy=(b[1]-a[1])*my;
    const t=Math.max(0,Math.min(1,-(x*dx+y*dy)/((dx*dx+dy*dy)||1)));
    return Math.hypot(x+t*dx,y+t*dy);
  }
  function assessRoute(option,segments) {
    const samples=[];
    let next=15, total=0;
    for (let i=1;i<option.line.length;i++) {
      const a=option.line[i-1],b=option.line[i],length=distanceMeters(a,b);
      while(length>0 && next<=total+length && samples.length<1200) {
        const t=(next-total)/length;
        samples.push([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])]);
        next+=30;
      }
      total+=length;
    }
    let lit=0,paved=0,concerns=0;
    for (const point of samples) {
      let nearest=null, best=10;
      for (const segment of segments) {
        const metres=pointToSegment(point,segment);
        if (metres<best) { nearest=segment.tags;best=metres; }
      }
      if (!nearest) continue;
      if (nearest.lit==="yes") lit++;
      if (/^(asphalt|concrete|paving_stones|paved)$/.test(nearest.surface||"")) paved++;
      if (/^(bad|very_bad|horrible|very_horrible|impassable)$/.test(nearest.smoothness||"") ||
          /^(unpaved|ground|dirt|mud|sand|gravel)$/.test(nearest.surface||"")) concerns++;
    }
    const count=samples.length;
    return {green:count>0 && next>=total && paved/count>=.8 && concerns===0,
      summary:count ? lit+"/"+count+" samples tagged lit · "+paved+"/"+count+" paved · "+concerns+" with mapped concerns" : "Check road surface before travel"};
  }
  function presentRoutes(options,selected) {
    routeChoices.replaceChildren();
    options.forEach((option,index)=>{
      const button=document.createElement("button");
      button.type="button";
      button.dataset.condition=option.condition.green?"green":"red";
      button.setAttribute("aria-pressed",String(index===selected));
      button.textContent=(index===0?"Primary":"Alternative "+index)+" · "+(option.metres/1000).toFixed(1)+" km · "+Math.max(1,Math.round(option.seconds/60))+" min";
      button.onclick=()=>presentRoutes(options,index);
      routeChoices.append(button);
    });
    route=options[selected];
    const mappedPlaces=features.filter(place=>place.kind!=="lights" && place.kind!=="landmark" || place.tags?.shop)
      .filter(place=>route.line.some((point,i)=>i>0 && pointToSegment(place.point,{a:route.line[i-1],b:point})<80)).length;
    const placeNote=mappedPlaces ? " · "+mappedPlaces+" mapped facilities near the route in this map view" : "";
    const more = options.length<4 ? " · "+options.length+" route"+(options.length===1?"":"s")+" returned" : "";
    note("state-result",(route.condition.green?"Green · Mapped conditions pass":"Red · Check conditions")+" · "+route.condition.summary+placeNote+more);
    fitRoute();redrawn();
  }
  async function findRoute() {
    if (!start||!end||!online()||routePending) return;
    const coordinates=[start,...stops.map(stop=>stop.point),end].map(p=>p.map(n=>n.toFixed(5)).join(",")).join(";");
    const token=++routeGeneration;
    if (Date.now()-requestTime<1200) return;
    requestTime=Date.now();
    note("state-route-note","");
    routeChoices.replaceChildren();
    routePending=true;refreshControls();
    try {
      const url="https://routing.openstreetmap.de/routed-"+mode+"/route/v1/driving/"+coordinates+"?alternatives=3&overview=full&geometries=geojson&steps=false";
      const json=await fetchJson(url,15);
      const options=(json.routes||[]).slice(0,6).map(item=>normalRoute({code:json.code,routes:[item]})).filter(Boolean);
      if (!options.length) throw Error("No route");
      if(options.length<4 && token===routeGeneration) {
        const points=[start,...stops.map(stop=>stop.point),end];
        let leg=0;
        for(let i=1;i<points.length-1;i++)if(distanceMeters(points[i],points[i+1])>distanceMeters(points[leg],points[leg+1]))leg=i;
        const a=points[leg],b=points[leg+1],length=distanceMeters(a,b);
        if(length>=400 && length<=25000){
          const latScale=111195,lonScale=latScale*Math.cos((a[1]+b[1])/2*Math.PI/180);
          const dx=(b[0]-a[0])*lonScale,dy=(b[1]-a[1])*latScale;
          const offsets=[.16,-.16,.30,-.30,.42,-.42];
          for(const fraction of offsets) {
            await new Promise(resolve=>setTimeout(resolve,1100));
            if(token!==routeGeneration || options.length>=6)break;
            const side=Math.sign(fraction)*Math.min(1100,Math.max(110,length*Math.abs(fraction)));
            const via=[(a[0]+b[0])/2-dy/length*side/lonScale,(a[1]+b[1])/2+dx/length*side/latScale];
            if(!inState(via))continue;
            const coords=[...points.slice(0,leg+1),via,...points.slice(leg+1)].map(p=>p.map(x=>x.toFixed(5)).join(",")).join(";");
            try {
              const response=await fetchJson("https://routing.openstreetmap.de/routed-"+mode+"/route/v1/driving/"+coords+"?overview=full&geometries=geojson&steps=false&continue_straight=true",3);
              const candidate=normalRoute(response);
              if(!candidate||candidate.metres>options[0].metres*1.8||distanceMeters(response.waypoints?.[leg+1]?.location||via,via)>150)continue;
              const step=Math.max(1,Math.floor(candidate.line.length/24));
              const samples=candidate.line.filter((_,i)=>i%step===0);
              const distinct=options.every(option=>samples.filter(point=>!option.line.some((p,i)=>i&&pointToSegment(point,{a:option.line[i-1],b:p})<30)).length>=Math.max(2,samples.length*.18));
              if(distinct)options.push(candidate);
            } catch { /* Keep other returned routes. */ }
          }
        }
      }
      const segments=await routeConditions(options);
      if (token!==routeGeneration) return;
      options.forEach(option=>{option.condition=assessRoute(option,segments);});
      presentRoutes(options,0);
    } catch {
      if (token===routeGeneration) note("state-route-note","No road route returned. Try a different start, destination, or travel mode.");
    } finally { if (token===routeGeneration) {routePending=false;refreshControls();} }
  }

""" + atlas[end:]
    atlas = atlas.replace('routeGeneration++;routePending=false;route=null;', 'routeGeneration++;routePending=false;route=null;routeChoices.replaceChildren();', 1)
    atlas = atlas.replace('ctx.strokeStyle="#a56d18";', 'ctx.strokeStyle=route.condition?.green?"#188047":"#b72e42";', 1)
    atlas = atlas.replace('"line-color":"#a56d18",', '"line-color":["get","condition"],', 1)
    atlas = atlas.replace('properties:{},geometry:{type:"LineString",coordinates:route.line}', 'properties:{condition:route.condition?.green?"#188047":"#b72e42"},geometry:{type:"LineString",coordinates:route.line}', 1)
    atlas = atlas.replace('nwr["healthcare"~', 'nwr["shop"]\'+near+\';nwr["healthcare"~', 1)
    atlas = atlas.replace('tags.tourism || tags.historic', 'tags.shop || tags.tourism || tags.historic', 1)
    atlas = atlas.replace('const subtype = tags.amenity ||', 'const subtype = tags.shop || tags.amenity ||', 1)
    atlas = atlas.replace('slice(0,12);\n    for (const place of places)', 'slice(0,45);\n    for (const place of places)', 1)
    atlas = atlas.replace('baseStyle.add(new Option(label,name));','baseStyle.add(new Option(label,name,false,name==="hybrid"));',1)
    atlas = atlas.replace('          if (areaInput.value!=="") chooseArea();', '          if (areaInput.value!=="") chooseArea();',1)
    atlas = atlas.replace('          else if (start||end) target.jumpTo({center:start||end,zoom:13});','          else if (start||end) target.jumpTo({center:start||end,zoom:13});\n          else target.jumpTo({center:[78.683,10.8],zoom:14});\n          queueNearby();',1)
    atlas = atlas.replace('  async function nearby() {', r"""
  let nearbyTimer, lastNearby = null, queuedNearby = false;
  function queueNearby() {
    clearTimeout(nearbyTimer);
    if (!streetReady || map.getZoom()<13) return;
    nearbyTimer=setTimeout(()=>{
      const centre=middle();
      if (lastNearby && distanceMeters(centre,lastNearby)<220) return;
      if (contextPending) {queuedNearby=true;return;}
      nearby(true);
    },700);
  }
  async function nearby(automatic=false) {""",1)
    atlas = atlas.replace('    const radius=Number(nearbyRadius.value);', '    lastNearby=p;\n    const radius=automatic?Math.min(1500,Number(nearbyRadius.value)):Number(nearbyRadius.value);',1)
    atlas = atlas.replace('nearbyArea.disabled=false;contextPending=false;refreshControls();','nearbyArea.disabled=false;contextPending=false;refreshControls();if(queuedNearby){queuedNearby=false;queueNearby();}',1)
    atlas = atlas.replace('addEventListener("click",nearby);','addEventListener("click",()=>nearby());',1)
    atlas = atlas.replace('target.on("zoomend",drawPlaceLabels);','target.on("zoomend",drawPlaceLabels);\n    target.on("moveend",queueNearby);',1)
    return atlas


def organize_planner(atlas):
    start = atlas.index('  let nearbyTimer, lastNearby')
    end = atlas.index('  for (const key of ["start","end"])', start)
    atlas = atlas[:start] + r"""
  let nearbyTimer, hoverPoint, tapPoint, lastNearbyKey="", pendingKey="";
  const nearbySnapshots=new Map();
  const nearbyHeading=document.createElement("p");
  nearbyHeading.textContent="Select start or destination. Otherwise tap the map on a phone or pause your pointer over the map.";
  nearbyPlaces.before(nearbyHeading);
  nearbyRadius.value="10000";
  function nearbyCentres() {
    const selected=[];
    if(start) selected.push(["Start",start]);
    if(end) selected.push(["Destination",end]);
    return selected.length?selected:[[tapPoint?"Map tap":hoverPoint?"Pointer":"Map centre",tapPoint||hoverPoint||middle()]];
  }
  function queueNearby() {
    clearTimeout(nearbyTimer);
    nearbyTimer=setTimeout(()=>nearby(false),850);
  }
  function setNearbyPoint(point,tap) {
    if(start||end||picking||!inState(point)) return;
    if(tap){tapPoint=point;hoverPoint=null;nearby(true);return;}
    if(tapPoint || (hoverPoint && distanceMeters(hoverPoint,point)<120)) return;
    hoverPoint=point;queueNearby();
  }
  async function nearby(force=false) {
    const radius=Number(nearbyRadius.value);
    const centres=nearbyCentres().filter(([,p])=>inState(p));
    if(!centres.length) return;
    const key=radius+":"+centres.map(([label,p])=>label+":"+p.map(v=>v.toFixed(3)).join(",")).join(";");
    if(!force && key===lastNearbyKey) return;
    lastNearbyKey=key;
    const local=centres.map(([label,p])=>({label,items:bundledNearby(p,radius),source:"Bundled OpenStreetMap"}));
    nearbyHeading.textContent="Up to "+radius/1000+" km · straight-line distance from each search point.";
    function publish(groups){
      const merged=new Map();
      groups.forEach(group=>group.items.forEach(p=>merged.set(p.osm,p)));
      features=[...merged.values()]; renderNearby(groups); renderNearbyCounts(); drawPlaceLabels(); redrawn();
    }
    publish(local);
    note("state-context-note",online()?"Loading mapped places…":"Showing bundled places.");
    if(!online()) return;
    if(contextPending){pendingKey=key;return;}
    contextPending=true;
    try {
      const groups=await Promise.all(centres.map(async ([label,p],i)=>{
        const cacheKey=radius+":"+p.map(v=>v.toFixed(3)).join(",");
        try {
          let cached=nearbySnapshots.get(cacheKey);
          if(!cached || Date.now()-cached.time>300000){
            const json=await findNearbyData(p,radius);
            cached={time:Date.now(),items:contextFrom(json,p,radius)};
            if(nearbySnapshots.size>=14) nearbySnapshots.delete(nearbySnapshots.keys().next().value);
            nearbySnapshots.set(cacheKey,cached);
          }
          const union=new Map(cached.items.map(x=>[x.osm,x]));
          local[i].items.forEach(x=>{if(!union.has(x.osm))union.set(x.osm,x);});
          return {label,items:[...union.values()].sort((a,b)=>a.distance-b.distance),source:"OpenStreetMap online and bundled places"};
        } catch {return local[i];}
      }));
      if(lastNearbyKey!==key) return;
      publish(groups);
      note("state-context-note",groups.every(g=>g.source.startsWith("Bundled"))?"Showing bundled places. The live lookup did not return data.":"OpenStreetMap coverage varies by area.");
    } finally {
      contextPending=false;
      if(pendingKey){pendingKey="";lastNearbyKey="";queueNearby();}
    }
  }
  nearbyRadius.addEventListener("change",()=>nearby(true));

""" + atlas[end:]
    start = atlas.index('  function renderNearby() {')
    end = atlas.index('  let nearbyTimer',start)
    atlas = atlas[:start] + r"""
  const placeGroups=[["health","Health"],["police","Police"],["transit","Transit"],["shop","Shops"],["landmark","Landmarks"]];
  function renderNearby(groups) {
    nearbyPlaces.replaceChildren();
    for(const {label,items,source} of groups){
      const section=document.createElement("li");
      const title=document.createElement("strong");title.textContent=label+" · "+source;section.append(title);
      for(const [kind,name] of placeGroups){
        const matches=items.filter(p=>(p.tags?.shop?"shop":p.kind)===kind);
        if(!matches.length)continue;
        const details=document.createElement("details"),summary=document.createElement("summary");
        summary.textContent=name+" ("+matches.length+")";details.append(summary);
        details.open=kind==="health"||kind==="landmark";
        for(const place of matches.slice(0,25)){
          const button=document.createElement("button");button.type="button";
          button.textContent=place.label+" · "+(place.distance<1000?Math.round(place.distance)+" m":(place.distance/1000).toFixed(1)+" km");
          button.onclick=()=>showFeature(place,true);
          details.append(button);
        }
        section.append(details);
      }
      if(!items.some(p=>p.kind!=="lights")) section.append(" · No mapped places returned");
      nearbyPlaces.append(section);
    }
  }
""" + atlas[end:]
    atlas=atlas.replace('for (const km of [1.5, 3, 5])','for (const km of [1.5, 3, 5, 10])',1)
    atlas=atlas.replace('el("state-refresh").disabled=!online()||contextPending;', 'el("state-refresh").disabled=false;',1)
    atlas=atlas.replace('if (hit) showFeature(features[Number(hit.properties.index)]);','if (hit) showFeature(features[Number(hit.properties.index)],true);\n      else setNearbyPoint(e.lngLat.toArray(),true);',1)
    atlas=atlas.replace('    target.on("mousemove",e=>{','    target.on("mousemove",e=>{ if(e.originalEvent?.pointerType!=="touch") setNearbyPoint(e.lngLat.toArray(),false);',1)
    atlas=atlas.replace('    clearRoute();setPicking("");refreshControls();redrawn();','    clearRoute();setPicking("");refreshControls();redrawn();queueNearby();',1)
    atlas=atlas.replace('    stops.length=0; namedStart=""; namedEnd=""; renderStops(); refreshControls();','    stops.length=0; namedStart=""; namedEnd=""; tapPoint=null; hoverPoint=null; renderStops(); refreshControls(); queueNearby();',1)
    atlas=atlas.replace('  function showFeature(feature) {','  function showFeature(feature, scroll=false) {',1)
    atlas=atlas.replace('    target.hidden=false;\n    target.textContent=feature.label','    target.hidden=false;\n    if(scroll && matchMedia("(max-width:740px)").matches) target.scrollIntoView({block:"center"});\n    target.textContent=feature.label',1)
    atlas=atlas.replace('    if (!streetReady || map.getZoom()<12) return;\n    const candidates = features.filter(place=>place.kind!=="lights" && place.named!==false);\n    for (const place of candidates.slice(0,12)) {',r"""
    if (!streetReady) return;
    const bounds=map.getBounds(), zoom=map.getZoom();
    const known=[...featuredPlaces,...localIndex.values()].filter(p=>!["Neighbourhood"].includes(p.kind));
    const visible=new Map([...known,...(zoom>=13?features.filter(p=>p.kind!=="lights"&&p.named!==false):[])].filter(p=>bounds.contains(p.point)).map(p=>[p.osm,p]));
    const occupied=[];
    for (const place of visible.values()) {
      if(occupied.length>=24)break;
      const xy=map.project(place.point);
      if(occupied.some(p=>Math.abs(p.x-xy.x)<105&&Math.abs(p.y-xy.y)<32))continue;
      occupied.push(xy);""",1)
    atlas=atlas.replace('else showFeature(place);};','else showFeature(place,true);};',1)
    atlas=atlas.replace('target.on("moveend",queueNearby);','target.on("moveend",()=>{drawPlaceLabels();queueNearby();});',1)
    atlas=atlas.replace('  const routeChoices = document.createElement("div");','  let visibleRoutes=[];\n  const routeChoices = document.createElement("div");',1)
    atlas=atlas.replace('route=null;routeChoices.replaceChildren();','route=null;visibleRoutes=[];routeChoices.replaceChildren();',1)
    atlas=atlas.replace('    route=options[selected];','    visibleRoutes=options;\n    route=options[selected];',1)
    atlas=atlas.replace('features:route?[{type:"Feature",properties:{condition:route.condition?.green?"#188047":"#b72e42"},geometry:{type:"LineString",coordinates:route.line}}]:[]','features:[...visibleRoutes].sort((a,b)=>Number(a===route)-Number(b===route)).map(option=>({type:"Feature",properties:{condition:option.condition?.green?"#188047":"#b72e42",selected:option===route},geometry:{type:"LineString",coordinates:option.line}}))',1)
    atlas=atlas.replace('"line-width":9,"line-color":"#fffdf1"', '"line-width":["case",["get","selected"],8,5],"line-opacity":["case",["get","selected"],1,.5],"line-color":"#fffdf1"',1)
    atlas=atlas.replace('"line-width":4.6,"line-color":["get","condition"]','"line-width":["case",["get","selected"],4.6,3],"line-opacity":["case",["get","selected"],1,.6],"line-color":["get","condition"]',1)
    atlas=atlas.replace('    target.on("click",e=>{','    target.on("click",e=>{',1)
    return atlas


def night_city(atlas):
    assets = Path("night-assets")
    assets.mkdir(exist_ok=True)
    cdn = "https://cdn.jsdelivr.net/npm/"
    packages = {
        "three.module.js": "three@0.170.0/build/three.module.js",
        "three.core.js": "three@0.170.0/build/three.core.js",
        "three-license.txt": "three@0.170.0/LICENSE",
        "gsap.min.js": "gsap@3.13.0/dist/gsap.min.js",
        "ScrollTrigger.min.js": "gsap@3.13.0/dist/ScrollTrigger.min.js",
        "lenis.min.js": "lenis@1.3.11/dist/lenis.min.js",
        "lenis-license.txt": "lenis@1.3.11/LICENSE",
        "opening-hours.js": "opening_hours@3.9.0/build/opening_hours.min.js",
        "opening-hours-license.txt": "opening_hours@3.9.0/LICENSE",
        "qrcode.js": "qrcode-generator@1.4.4/qrcode.js",
        "qrcode-license.txt": "qrcode-generator@1.4.4/LICENSE",
        "jsQR.js": "jsqr@1.4.0/dist/jsQR.js",
        "jsQR-license.txt": "jsqr@1.4.0/LICENSE",
        "suncalc.js": "suncalc@1.9.0/suncalc.js",
        "suncalc-license.txt": "suncalc@1.9.0/LICENSE",
    }

    def fetch(url):
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"})
        with urlopen(req, timeout=8) as response:
            return response.read()

    def save_asset(name, url):
        try:
            (assets / name).write_bytes(fetch(url))
        except (OSError, ValueError) as error:
            print(f"Night City asset {name}: {error}")

    with ThreadPoolExecutor(max_workers=8) as workers:
        list(workers.map(lambda pair: save_asset(pair[0], cdn + pair[1]), packages.items()))
        families = {
            "nunito": "Nunito:wght@400..900",
            "baloo2": "Baloo+2:wght@400..800",
            "baloothambi2": "Baloo+Thambi+2:wght@400..800",
        }

        def fetch_font(pair):
            folder, family = pair
            try:
                style = fetch("https://fonts.googleapis.com/css2?family=" + family + "&display=swap").decode()
                urls = set(re.findall(r"https://fonts\.gstatic\.com/[^)]+", style))
                for number, url in enumerate(sorted(urls)):
                    extension = ".woff2" if ".woff2" in url else ".ttf"
                    name = f"{folder}-{number}" + extension
                    (assets / name).write_bytes(fetch(url))
                    style = style.replace(url, name)
                if not urls:
                    return ""
                save_asset(folder + "-OFL.txt", "https://raw.githubusercontent.com/google/fonts/main/ofl/" + folder + "/OFL.txt")
                return style
            except (OSError, ValueError) as error:
                print(f"Night City font {folder}: {error}")
                return ""

        (assets / "fonts.css").write_text("\n".join(workers.map(fetch_font, families.items())), encoding="utf-8")

    credits = []

    def relocate(match):
        credits.append(match.group(0))
        return '<p><a href="credits.html">Credits and licences</a></p>'

    atlas = re.sub(r'<details\b[^>]*>\s*<summary>\s*(?:Typeface notice|Open-source notices)\s*</summary>.*?</details>', relocate, atlas, flags=re.S | re.I)
    atlas = atlas.replace('if (element.textContent !== text) element.textContent = text;', 'if (element && element.textContent !== text) element.textContent = text;', 1)
    atlas = atlas.replace('badge.classList.toggle("waiting",', 'badge?.classList.toggle("waiting",', 1)
    atlas = atlas.replace('container:liveTarget,style:', 'container:liveTarget,pitch:matchMedia("(prefers-reduced-motion: reduce)").matches?0:35,style:', 1)
    atlas = atlas.replace('    target.addLayer({id:"state-route-border"', '''    try {
      const building=target.getStyle().layers.find(layer=>layer["source-layer"]==="building" && layer.source);
      if(building) target.addLayer({id:"night-buildings",type:"fill-extrusion",source:building.source,"source-layer":"building",minzoom:14,layout:{visibility:"none"},paint:{"fill-extrusion-color":"#786bad","fill-extrusion-height":["min",75,["to-number",["coalesce",["get","render_height"],["get","height"]],8]],"fill-extrusion-opacity":.66}});
    } catch { /* Keep the base map if its building schema changes. */ }
    target.addLayer({id:"state-route-border"''',1)
    atlas = atlas.replace('    imageryCredit.hidden = style === "street";', '''    if(map.getLayer("night-buildings")) map.setLayoutProperty("night-buildings","visibility",style==="satellite"?"none":"visible");
    imageryCredit.hidden = style === "street";''',1)
    atlas = atlas.replace('"line-color":"#fffdf1"', '"line-color":["get","condition"],"line-blur":4',1)
    atlas = atlas.replace('    note("state-result",(route.condition.green?"Green', '    note("state-result",(route.condition.green?"✓ Green',1).replace('":"Red · Check conditions")', '":"! Red · Check conditions")',1)
    atlas = atlas.replace('button.textContent=(index===0?"Primary"', 'button.textContent=(option.condition.green?"✓ ":"! ")+(index===0?"Primary"',1)
    atlas = re.sub(r'<link\b[^>]*href=["\x27]https://fonts\.googleapis\.com/[^>]*>', '', atlas)
    return atlas, credits


def night_city_features(atlas):
    atlas = atlas.replace('  async function findRoute() {', "\n  const insight=document.createElement(\"section\");\n  insight.className=\"safelink-extra\";\n  insight.innerHTML='<h3>Walk conditions</h3><p>Mapped data may be missing. Conditions and forecasts do not establish personal safety.</p><div data-fields></div><p data-insight role=\"status\"></p><ul data-refuges></ul>';\n  routeChoices.after(insight);\n  const routeText=insight.querySelector(\"[data-insight]\");\n  const refugeList=insight.querySelector(\"[data-refuges]\");\n  const viirs=document.createElement(\"label\");\n  viirs.innerHTML='<input type=\"checkbox\"> NASA VIIRS night lights';\n  viirs.title=\"Historical satellite light. This does not show whether an individual streetlight is working.\";\n  el(\"state-fit\").after(viirs);\n  el(\"state-fit\").after(Object.assign(document.createElement(\"a\"),{href:\"https://worldview.earthdata.nasa.gov/\",textContent:\"NASA GIBS\",target:\"_blank\",rel:\"noopener\"}));\n  const rasterId=\"safelink-viirs\";\n  function installViirs() {\n    try {\n      map.addSource(rasterId,{type:\"raster\",tileSize:256,maxzoom:8,attribution:\"NASA EOSDIS GIBS / VIIRS (2012)\",\n        tiles:[\"https://gitc.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_CityLights_2012/default//GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpg\"]});\n      map.addLayer({id:rasterId,type:\"raster\",source:rasterId,layout:{visibility:\"none\"},paint:{\"raster-opacity\":.46}},\"state-route-border\");\n      syncViirs();\n    }catch {viirs.title=\"Historical night-light overlay unavailable\";}\n  }\n  function syncViirs(){\n    if(map?.getLayer(rasterId))map.setLayoutProperty(rasterId,\"visibility\",viirs.firstElementChild.checked?\"visible\":\"none\");\n  }\n  viirs.firstElementChild.addEventListener(\"change\",syncViirs);\n  const roll=document.createElement(\"button\");\n  roll.type=\"button\";roll.textContent=\"Roll a walk\";\n  el(\"state-route\").before(roll);\n  roll.onclick=()=>{\n    const places=[...new Map([...localIndex,...features.filter(p=>p.osm).map(p=>[p.osm,p])]).values()].filter(place=>\n      place.kind!==\"lights\" && distanceMeters(middle(),place.point)<7000 && inState(place.point));\n    const pairs=places.flatMap((a,i)=>places.slice(i+1).filter(b=>{\n      const d=distanceMeters(a.point,b.point);return d>300&&d<4500;\n    }).map(b=>[a,b]));\n    if(!pairs.length){note(\"state-route-note\",\"Choose a Trichy area or load more mapped landmarks first.\");return;}\n    const [a,b]=pairs[Math.floor(Math.random()*pairs.length)];\n    stops.length=0;renderStops();mode=\"foot\";setPlace(a,\"start\");setPlace(b,\"end\");findRoute();\n  };\n  let insightVersion=0, refugePins=[];\n  const istDate=(input)=>new Date(input?input+\":00+05:30\":Date.now());\n  let solarPromise,hoursPromise;\n  function loadUtility(file,globalName){\n    if(window[globalName])return Promise.resolve(window[globalName]);\n    return new Promise((resolve,reject)=>{\n      const script=document.createElement(\"script\");\n      script.src=\"night-assets/\"+file;script.onload=()=>window[globalName]?resolve(window[globalName]):reject(Error(\"Library unavailable\"));script.onerror=reject;\n      document.head.append(script);\n    });\n  }\n  function clearInsights(){\n    ++insightVersion;refugePins.forEach(x=>x.remove());refugePins=[];\n    routeText.textContent=\"\";refugeList.replaceChildren();\n  }\n  async function showInsights(option){\n    clearInsights();\n    const version=insightVersion;\n    const departure=istDate(el(\"night-departure\")?.value);\n    if(!Number.isFinite(departure.getTime()))return;\n    const arrival=new Date(departure.getTime()+option.seconds*1000);\n    const centre=option.line[Math.floor(option.line.length/2)];\n    const [x,y]=centre;\n    routeText.textContent=\"Checking conditions for this route…\";\n    function add(text){if(version!==insightVersion)return;const p=document.createElement(\"li\");p.textContent=text;refugeList.append(p);}\n    solarPromise ||= loadUtility(\"suncalc.js\",\"SunCalc\").catch(()=>null);\n    const solar=solarPromise.then(sun=>{\n      if(!sun)return add(\"Sunset lookup unavailable.\");\n      let dark=0, mins=Math.ceil(option.seconds/60);\n      const formatter=new Intl.DateTimeFormat(\"en-CA\",{timeZone:\"Asia/Kolkata\",year:\"numeric\",month:\"numeric\",day:\"numeric\"});\n      for(let i=0;i<Math.min(mins,4320);i++){\n        const sample=new Date(departure.getTime()+i*60000);\n        const parts=Object.fromEntries(formatter.formatToParts(sample).map(p=>[p.type,p.value]));\n        const anchor=new Date(Date.UTC(+parts.year,+parts.month-1,+parts.day,6,30));\n        const times=sun.getTimes(anchor,y,x);\n        if(sample>=times.sunset || sample<times.sunrise)dark++;\n      }\n      add(mins>4320?\"After-dark estimate exceeds the three-day calculation limit.\":dark+\" minutes of this \"+(mode===\"foot\"?\"walk\":\"trip\")+\" fall after dark (IST estimate).\");\n    });\n    const params=\"latitude=\"+y.toFixed(4)+\"&longitude=\"+x.toFixed(4)+\"&timezone=GMT&forecast_days=7\";\n    const windowRows=(json,key)=>json.hourly?.time?.flatMap((t,i)=>{\n      const ms=Date.parse(t+\"Z\");\n      return ms<=arrival && ms+3600000>departure && Number.isFinite(json.hourly[key]?.[i])?[json.hourly[key][i]]:[];\n    })||[];\n    const weather=Promise.allSettled([\n      fetchJson(\"https://api.open-meteo.com/v1/forecast?\"+params+\"&hourly=temperature_2m,precipitation\",8),\n      fetchJson(\"https://air-quality-api.open-meteo.com/v1/air-quality?\"+params+\"&hourly=us_aqi\",8)\n    ]).then(([w,a])=>{\n      if(w.status===\"fulfilled\"){\n        const heat=windowRows(w.value,\"temperature_2m\"),rain=windowRows(w.value,\"precipitation\");\n        if(heat.length&&rain.length)add(\"Open-Meteo near route midpoint · up to \"+Math.max(...heat)+\" °C and \"+Math.max(...rain)+\" mm/hour rain.\");\n        else add(\"Weather forecast does not cover the selected time.\");\n      }else add(\"Weather forecast unavailable.\");\n      const aq=a.status===\"fulfilled\"?windowRows(a.value,\"us_aqi\"):[];\n      add(aq.length?\"Open-Meteo air quality · peak estimated US AQI \"+Math.max(...aq)+\".\":\"Air-quality forecast unavailable.\");\n    });\n    const refuge=(async()=>{\n      const stride=Math.max(1,Math.ceil(option.line.length/75)), points=option.line.filter((_,i)=>i%stride===0);\n      if(option.metres>25000 || !online())return;\n      if(points.at(-1)!==option.line.at(-1))points.push(option.line.at(-1));\n      const query='[out:json][timeout:7];nwr[\"amenity\"~\"^(pharmacy|hospital|police|fuel)$\"][\"opening_hours\"](around:130,'+points.map(([lon,lat])=>lat.toFixed(5)+\",\"+lon.toFixed(5)).join(\",\")+');out center 70;';\n      hoursPromise ||= loadUtility(\"opening-hours.js\",\"opening_hours\").catch(()=>null);\n      try{\n        const [data,Hours]=await Promise.all([fetchJson(\"https://overpass.private.coffee/api/interpreter?data=\"+encodeURIComponent(query),8),hoursPromise]);\n        if(version!==insightVersion)return;\n        if(!Hours){add(\"Opening-hours parser unavailable.\");return;}\n        // The isolated Date carries IST wall time in the visitor's local calendar.\n        const toWall=date=>{\n          const parts=Object.fromEntries(new Intl.DateTimeFormat(\"en-GB\",{timeZone:\"Asia/Kolkata\",year:\"numeric\",month:\"numeric\",day:\"numeric\",hour:\"numeric\",minute:\"numeric\",hourCycle:\"h23\"}).formatToParts(date).map(p=>[p.type,p.value]));\n          return new Date(+parts.year,+parts.month-1,+parts.day,+parts.hour,+parts.minute);\n        };\n        let count=0;\n        const cumulative=[0];\n        for(let i=1;i<option.line.length;i++)cumulative.push(cumulative.at(-1)+distanceMeters(option.line[i-1],option.line[i]));\n        for(const item of data.elements||[]){\n          if(count>=8)break;\n          const point=[item.lon??item.center?.lon,item.lat??item.center?.lat];\n          if(!point.every(Number.isFinite))continue;\n          let nearest=-1, best=130;\n          for(let i=1;i<option.line.length;i++){const d=pointToSegment(point,{a:option.line[i-1],b:option.line[i]});if(d<best){best=d;nearest=i;}}\n          if(nearest<0)continue;\n          const eta=new Date(departure.getTime()+option.seconds*1000*(cumulative[nearest-1]+cumulative[nearest])/2/(cumulative.at(-1)||1));\n          try{\n            const schedule=item.tags.opening_hours;\n            if(/\\b(?:PH|SH|sunrise|sunset|dawn|dusk)\\b/i.test(schedule))continue;\n            const hours=new Hours(schedule);\n            if(!hours.getState(toWall(eta)))continue;\n          }catch{continue;}\n          const label=item.tags.name||item.tags.amenity;\n          const time=new Intl.DateTimeFormat(\"en-IN\",{timeZone:\"Asia/Kolkata\",hour:\"numeric\",minute:\"2-digit\"}).format(eta);\n          add(label+\" · mapped open around \"+time+\" IST. Confirm locally.\");\n          if(streetReady){const pin=document.createElement(\"span\");pin.className=\"safelink-refuge\";pin.textContent=\"✚\";pin.title=label+\" · mapped open\";refugePins.push(new maplibregl.Marker({element:pin}).setLngLat(point).addTo(map));}\n          count++;\n        }\n        if(!count)add(\"No mapped facilities with confirmed parseable hours on this route.\");\n      }catch{add(\"Mapped opening hours did not load.\");}\n    })();\n    await Promise.allSettled([solar,weather,refuge]);\n    if(version===insightVersion)routeText.textContent=\"Conditions for selected departure · India Standard Time\";\n  }\n  window.addEventListener(\"safelink:departure\",()=>{if(route)showInsights(route);});\n  window.addEventListener(\"safelink:impact\",()=>{\n    const lit=route?.condition?.litCoverage;\n    window.dispatchEvent(new CustomEvent(\"safelink:stats\",{detail:{lit:lit||null, facilities:features.filter(p=>[\"health\",\"police\",\"transit\"].includes(p.kind)).length,area:(typeof nearbyCentres===\"function\"&&nearbyCentres().length===1?Math.PI*(Number(nearbyRadius.value)/1000)**2:0)}}));\n  });\n\n  window.addEventListener(\"safelink:share-request\",()=>{\n    window.dispatchEvent(new CustomEvent(\"safelink:trip\",{detail:start&&end?{points:[start,...stops.map(stop=>stop.point),end].map(point=>point.map(n=>+n.toFixed(5))),mode}:null}));\n  });\n  if(location.hash.startsWith(\"#trip=\")){\n    try {\n      const saved=JSON.parse(decodeURIComponent(location.hash.slice(6)));\n      if([\"car\",\"foot\"].includes(saved.mode)&&Array.isArray(saved.points)&&saved.points.length>=2&&saved.points.length<=7&&\n         saved.points.every(p=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite)&&inState(p))){\n        [start]=saved.points; end=saved.points.at(-1);mode=saved.mode;\n        saved.points.slice(1,-1).forEach((point,i)=>stops.push({point,label:\"Shared stop \"+(i+1),osm:\"shared-\"+i}));\n        renderStops();refreshControls();redrawn();window.addEventListener(\"load\",()=>document.getElementById(\"workspace\").scrollIntoView(),{once:true});\n      }\n    }catch{/* Ignore invalid shared links. */}\n  }\n" + '\n  async function findRoute() {', 1)
    atlas = atlas.replace('    let lit=0,paved=0,concerns=0;', '    let lit=0,unlit=0,paved=0,concerns=0;', 1)
    atlas = atlas.replace('      if (nearest.lit==="yes") lit++;', '      if (nearest.lit==="yes") lit++;\n      if (nearest.lit==="no") unlit++;', 1)
    atlas = atlas.replace('    return {green:count>0', '    const denom=Math.max(1,Math.ceil(total/30));\n    const yes=Math.min(100,Math.round(lit*100/denom)), no=Math.min(100-yes,Math.round(unlit*100/denom));\n    return {litCoverage:{yes,no,unknown:100-yes-no},green:count>0', 1)
    atlas = atlas.replace('lit+"/"+count+" samples tagged lit · "', 'yes+"% lit · "+no+"% unlit · "+(100-yes-no)+"% lighting unknown · "', 1)
    atlas = atlas.replace('    route=options[selected];', '''    route=options[selected];
    const best=(metric)=>options.reduce((index,option,i)=>metric(option)<metric(options[index])?i:index,0);
    const choices=[["Shortest",best(o=>o.metres)],["Brighter mapped route",best(o=>-o.condition.litCoverage.yes)],["Fewer surface concerns",best(o=>o.condition.concernCount)]];
    for(const [label,index] of choices){
      const b=document.createElement("button");b.type="button";
      b.dataset.condition=options[index].condition.green?"green":"red";
      b.textContent=label+" · "+(options[index].metres/1000).toFixed(1)+" km";
      b.onclick=()=>presentRoutes(options,index);routeChoices.append(b);
    }
    showInsights(route);''',1)
    atlas = atlas.replace('return {litCoverage:', 'return {concernCount:concerns,litCoverage:',1)
    atlas = atlas.replace('route=null;visibleRoutes=[];routeChoices.replaceChildren();', 'route=null;visibleRoutes=[];routeChoices.replaceChildren();clearInsights();', 1)
    atlas = atlas.replace('          installLayer(target);','          installLayer(target);\n          installViirs();',1)
    atlas = atlas.replace('  function motionEvent(event) {', "\n  const shakeSensitivity=document.createElement(\"label\");\n  shakeSensitivity.innerHTML='<span>Shake sensitivity </span><select aria-label=\"Shake sensitivity\"><option value=\"15\">Low</option><option value=\"12\" selected>Medium</option><option value=\"9\">High</option></select>';\n  get(\"arm-shake\").before(shakeSensitivity);\n  const shakeGate=document.createElement(\"dialog\");\n  shakeGate.className=\"safelink-extra\";\n  shakeGate.innerHTML='<h2>Shake detected</h2><p role=\"status\"></p><button type=\"button\">Cancel</button>';\n  document.body.append(shakeGate);\n  let shakeTimer=0,shakeWake=null;\n  function clearShake(){\n    clearInterval(shakeTimer);\n    navigator.vibrate?.(0);\n    shakeWake?.release().catch(()=>{});shakeWake=null;\n  }\n  shakeGate.addEventListener(\"close\",clearShake);\n  shakeGate.querySelector(\"button\").onclick=()=>shakeGate.close();\n  async function offerShake(){\n    if(shakeGate.open||sosDialog.open)return;\n    shakeGate.showModal();\n    navigator.vibrate?.([100,80,100]);\n    navigator.wakeLock?.request(\"screen\").then(lock=>{if(shakeGate.open)shakeWake=lock;else lock.release().catch(()=>{});}).catch(()=>{});\n    let left=10;\n    const status=shakeGate.querySelector(\"p\");\n    const tick=()=>{\n      status.textContent=\"Emergency options open in \"+left+\" seconds. Nothing is called automatically.\";\n      if(left--===0){clearShake();shakeGate.close();openSOS(false);}\n    };\n    tick();shakeTimer=setInterval(tick,1000);\n  }\n  document.addEventListener(\"visibilitychange\",()=>{if(document.hidden&&shakeGate.open){clearShake();shakeGate.close();}});\n  window.addEventListener(\"safelink:qr-export\",()=>{\n    window.dispatchEvent(new CustomEvent(\"safelink:qr-data\",{detail:{schema:\"safelink-reports-v1\",map:mapData.snapshot,\n      reports:book.reports.filter(validReport).filter(report=>/^(?:[a-f0-9-]{36}|local-[a-z0-9]{8,30})$/i.test(report.bundle)).filter(report=>Date.now()-Date.parse(report.date)<90*DAY).slice(0,120).map(clean)}}));\n  });\n  window.addEventListener(\"safelink:qr-import\",event=>{\n    const packet=event.detail;\n    const respond=text=>window.dispatchEvent(new CustomEvent(\"safelink:qr-status\",{detail:text}));\n    if(!packet||packet.schema!==\"safelink-reports-v1\"||packet.map!==mapData.snapshot||!Array.isArray(packet.reports)||packet.reports.length>120||!packet.reports.every(validReport)){\n      respond(\"Invalid bundle or different map. Select the matching offline area.\");return;\n    }\n    const eligible=packet.reports.filter(x=>/^(?:[a-f0-9-]{36}|local-[a-z0-9]{8,30})$/i.test(x.bundle)&&x.bundle!==book.id&&Date.now()-Date.parse(x.date)<90*DAY);\n    const merged=new Map(book.reports.map(x=>[reportKey(x),x]));\n    let added=0,conflicts=0;\n    for(const x of eligible){\n      if([...merged.values()].some(old=>old.edge===x.edge&&old.band===x.band&&old.bundle!==x.bundle&&categories[old.kind][1]!==categories[x.kind][1]))conflicts++;\n      const key=reportKey(x),old=merged.get(key);\n      if(!old||old.date<x.date){merged.set(key,clean(x));added++;}\n    }\n    book.reports=[...merged.values()].sort((a,b)=>b.date.localeCompare(a.date)).slice(0,500);\n    if(added)save();\n    respond(added+\" observations imported · \"+conflicts+\" with conflicting reports. Older than 90 days excluded.\");\n    blurb(\"report-status\",\"QR observations imported. Re-select the route to refresh its report summary.\");\n    invalidate();\n  });\n" + '\n  function motionEvent(event) {',1)
    atlas = atlas.replace('magnitude<12 || now-lastAlert<6500','magnitude<Number(shakeSensitivity.querySelector("select").value) || now-lastAlert<6500',1)
    atlas = atlas.replace('peaks=[]; lastAlert=now; openSOS(false);','peaks=[]; lastAlert=now; offerShake();\n    if(window.scrollY<180)window.dispatchEvent(new Event("safelink:hero-shake"));',1)
    return atlas

app = Path("index.html")
atlas = app.read_text(encoding="utf-8")
if "<!doctype html>" not in atlas.lower() or atlas.count("</head>") != 1 or atlas.count("</body>") != 1:
    raise SystemExit("Expected a standalone atlas in index.html")

atlas = organize_planner(upgrade_route_conditions(upgrade_atlas_map(atlas)))
atlas, credits = night_city(night_city_features(atlas))
atlas = atlas.replace("</body>", '<footer class="safelink-contact aa-width"><h2>About SafeLink</h2><p><a href="credits.html">Credits and licences</a></p><p>Founded by Eraiyanbu and Jeswin Samuel.</p><h3>Professional enquiries</h3><p><a href="mailto:jeswinsamuel.la@gmail.com">jeswinsamuel.la@gmail.com</a> · <a href="tel:+919597064942">+91 9597064942</a></p></footer></body>', 1)
atlas = atlas.replace("</body>", '<script>const how=document.createElement("a"); how.href="how-it-works.html"; how.textContent="How SafeLink works"; const credits=document.createElement("a"); credits.href="credits.html"; credits.textContent="Credits and licences"; document.getElementById("ride-open")?.before(credits); document.getElementById("ride-open")?.before(how); document.getElementById("state-end")?.after(how.cloneNode(true));</script></body>', 1)

site_base = 'new URL("./", location.href)'
asset_base = 'new URL("./", document.currentScript.src)'
voice_endpoint = escape(VOICE_ENDPOINT, quote=True)
live = LIVE.replace(asset_base, site_base)
tamil_lines = {
    "hello": "ஹலோ, நான் பேசுறேன். கேட்குதா?",
    "stay": "சரி, நான் லைனிலேயே இருக்கேன்.",
    "wait": "அவசரம் இல்லை. நான் லைனில் இருக்கேன்.",
    "bye": "சரி, அப்புறம் பேசலாம்.",
    "intent-0": "வெளிச்சம் இருக்கும் பிரதான வாசல் பக்கம் சந்திப்போம்.",
    "intent-1": "இன்னும் ஐந்து நிமிஷம். அதுவரை லைனில் இருக்கேன்.",
    "intent-2": "சரி, அவசரம் இல்லை. நான் லைனில் இருக்கேன்.",
    "intent-3": "சரி, அப்புறம் பேசலாம்.",
    "prompt": "கேட்குது. எங்கே சந்திக்கணும், எப்போ வருவேன், அல்லது லைனில் இருக்கணுமான்னு கேளுங்க.",
}
tamil_assets = []
if shutil.which("espeak-ng"):
    for key, line in tamil_lines.items():
        filename = f"safelink-ta-{key}.wav"
        subprocess.run(["espeak-ng", "-v", "ta", "-s", "145", "-w", filename, line], check=True)
        tamil_assets.append(filename)
upgrade = UPGRADE.replace("__TAMIL_CLIPS__", str(bool(tamil_assets)).lower()).replace(asset_base, site_base).replace('new URL("../", base)', 'base')
scripts = f'<script>{CLIPS}</script><script>{live}</script><script data-voice-endpoint="{voice_endpoint}">{upgrade}</script>'
atlas = atlas.replace("</head>", f'<link rel="stylesheet" href="night-assets/fonts.css"><link rel="manifest" href="manifest.webmanifest"><meta name="theme-color" content="#111633"><style>{STYLE}{NIGHT_STYLE}</style>\n</head>', 1)
atlas = atlas.replace("</body>", scripts + '\n<script type="module" src="night-city.js"></script><script type="module" src="walk-toolkit.js"></script></body>', 1)
app.write_text(atlas, encoding="utf-8")
Path("mic-worklet.js").write_text(WORKLET, encoding="utf-8")
Path("safelink-sw.js").write_text(OFFLINE.replace("__TAMIL_ASSETS__", repr(tamil_assets)).replace("__NIGHT_FILES__", repr([str(path) for path in Path("night-assets").iterdir() if path.is_file()])), encoding="utf-8")


Path("how-it-works.html").write_text("<!doctype html><html lang=\"en\"><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width\"><title>How SafeLink works</title><link rel=\"stylesheet\" href=\"night-assets/fonts.css\"><style>body{font:1.1rem Nunito,sans-serif;background:#f6efe4;color:#321d28;margin:auto;max-width:47rem;padding:clamp(1.2rem,5vw,4rem);line-height:1.6}h1,h2{font-weight:900;line-height:1.12;color:#601d36ed;letter-spacing:.02em;text-shadow:1px 1px #d4a2a080,0 0 8px #c7759e4d}section{border-top:1px solid #aa7f75;padding:.75rem 0}a{color:#70243f}</style><main><a href=\"./\">Back to SafeLink</a><h1>How SafeLink works</h1><section><h2>What it helps with</h2><p>SafeLink helps people compare unfamiliar journeys and find public places before travelling. Knowing where a hospital, station or shop is mapped gives users a place to check or a waypoint to plan around.</p></section><section><h2>From landmark to route</h2><ol><li>Choose a starting point, destination and optional stops.</li><li>The routing provider calculates walking or driving paths. SafeLink shows the routes it returns, up to six including the primary route.</li><li>Where the OpenStreetMap lookup returns road data, SafeLink samples the route roughly every 30 metres and checks nearby tags for paving and rough surfaces, with lighting shown separately.</li><li>Green means the mapped road surface met the stated checks. Red means a concern was mapped or there was insufficient coverage to meet those checks.</li></ol><p><a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap data and attribution</a></p></section><section><h2>How it can reduce exposure</h2><p>Users can compare paths, add public landmarks, and prepare a simulated Ride Call. These tools help people plan and make choices. They cannot predict or prevent an incident on their own.</p></section><section><h2>What the map cannot tell you</h2><p>Streetlights may be broken, shops may be closed, and potholes may be unmapped. Mapped shops do not establish whether people are currently present. SafeLink does not judge residents or infer whether people nearby are trustworthy. A green route is not a guarantee of personal safety.</p></section><section><h2>What to build next</h2><p>Pilot in a few Trichy streets with local partners. Ask volunteers to verify lighting and surface conditions at specific times, date each observation, and review reports before publishing them. Compare the results with field observations, then expand to more areas once the data is reliable.</p><p>Use a maintained local map extract for consistent coverage. Work with the municipality on lighting and road-maintenance feeds, and test privacy, accessibility and poor-network behavior before a public rollout.</p></section><footer class=\"safelink-contact aa-width\"><h2>About SafeLink</h2><p>Founded by Eraiyanbu and Jeswin Samuel.</p><h3>Professional enquiries</h3><p><a href=\"mailto:jeswinsamuel.la@gmail.com\">jeswinsamuel.la@gmail.com</a> · <a href=\"tel:+919597064942\">+91 9597064942</a></p></footer></main></html>", encoding="utf-8")

Path("night-city.js").write_text("\n(() => {\n  \"use strict\";\n  const root=document.documentElement;\n  const motion=matchMedia(\"(prefers-reduced-motion: reduce)\");\n  const desktop=matchMedia(\"(hover:hover) and (pointer:fine)\");\n  const hero=document.getElementById(\"intro\");\n  if(!hero)return;\n  const byId=id=>document.getElementById(id);\n  const prefs=document.createElement(\"div\");\n  prefs.className=\"night-preferences\";\n  prefs.innerHTML='<label>City light <select aria-label=\"City light\"><option value=\"auto\">Automatic</option><option value=\"dawn\">Dawn</option><option value=\"day\">Day</option><option value=\"dusk\">Dusk</option><option value=\"night\">Night</option></select></label><button type=\"button\" aria-pressed=\"false\">Sound off</button>';\n  hero.querySelector(\".atlas-copy\").append(prefs);\n  const [select,sound]=[prefs.querySelector(\"select\"),prefs.querySelector(\"button\")];\n  const place=hero.querySelector(\".atlas-graphic\");\n  const stage=document.createElement(\"canvas\");\n  stage.className=\"night-canvas\";\n  stage.hidden=true;\n  stage.setAttribute(\"aria-hidden\",\"true\");\n  place.append(stage);\n  const opts={day:[0xacc3da,1.8],dawn:[0xf0b17f,1.1],dusk:[0xc58cc9,.85],night:[0x647bd5,.45]};\n  let paint=()=>{}, solar=null, context=null, soundOn=false;\n  function setTheme(){\n    const date=new Date();\n    const parts=new Intl.DateTimeFormat(\"en-CA\",{timeZone:\"Asia/Kolkata\",year:\"numeric\",month:\"numeric\",day:\"numeric\"}).formatToParts(date);\n    const p=Object.fromEntries(parts.map(part=>[part.type,part.value]));\n    const noon=new Date(Date.UTC(Number(p.year),Number(p.month)-1,Number(p.day),6,30));\n    const times=solar?.getTimes(noon,10.8,78.683);\n    const minute=Number(new Intl.DateTimeFormat(\"en-GB\",{timeZone:\"Asia/Kolkata\",hour:\"2-digit\",hourCycle:\"h23\"}).format(date));\n    const day=times?(date>=times.dawn&&date<times.sunrise?\"dawn\":date>=times.sunrise&&date<times.sunset?\"day\":date>=times.sunset&&date<times.dusk?\"dusk\":\"night\"):(minute===6?\"dawn\":minute>=7&&minute<18?\"day\":minute===18?\"dusk\":\"night\");\n    root.dataset.nightPhase=select.value===\"auto\"?day:select.value;\n    paint();\n  }\n  select.addEventListener(\"change\",setTheme);\n  setTheme();\n  setInterval(setTheme,60000);\n  function tone(){\n    if(!soundOn||!context||context.state!==\"running\")return;\n    const oscillator=context.createOscillator(), volume=context.createGain(), now=context.currentTime;\n    oscillator.type=\"sine\";oscillator.frequency.setValueAtTime(440,now);\n    oscillator.frequency.exponentialRampToValueAtTime(660,now+.12);\n    volume.gain.setValueAtTime(.0001,now);\n    volume.gain.exponentialRampToValueAtTime(.045,now+.04);\n    volume.gain.exponentialRampToValueAtTime(.0001,now+.26);\n    oscillator.connect(volume).connect(context.destination);\n    oscillator.start();oscillator.stop(now+.27);\n  }\n  sound.addEventListener(\"click\",async()=>{\n    const Audio=window.AudioContext||window.webkitAudioContext;\n    if(!Audio){sound.textContent=\"Sound unavailable\";sound.disabled=true;return;}\n    soundOn=!soundOn;\n    if(soundOn){try{context ||= new Audio();await context.resume();}catch{soundOn=false;}}\n    sound.setAttribute(\"aria-pressed\",String(soundOn));\n    sound.textContent=soundOn?\"Sound on\":\"Sound off\";tone();\n  });\n  hero.querySelector(\".atlas-cta\")?.addEventListener(\"click\",tone);\n\n  function loadScript(file){\n    return new Promise((resolve,reject)=>{\n      const script=document.createElement(\"script\");\n      script.src=\"night-assets/\"+file;script.onload=resolve;script.onerror=reject;\n      document.head.append(script);\n    });\n  }\n  function loadCity(){\n    loadScript(\"suncalc.js\").then(()=>{solar=window.SunCalc;setTheme();}).catch(()=>{});\n    if(motion.matches || navigator.connection?.saveData){place.dataset.city=\"static\";return;}\n    import(\"./night-assets/three.module.js\").then(async THREE=>{\n      const renderer=new THREE.WebGLRenderer({canvas:stage,alpha:true,antialias:devicePixelRatio<2,powerPreference:\"low-power\"});\n      renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.5));\n      const scene=new THREE.Scene(), camera=new THREE.PerspectiveCamera(40,1,.1,150);\n      scene.add(new THREE.HemisphereLight(0xf6edfc,0x171b35,2));\n      const sun=new THREE.DirectionalLight(0x958ae4,1);\n      sun.position.set(5,10,4);scene.add(sun);\n      const material=(color)=>new THREE.MeshStandardMaterial({color,flatShading:true,roughness:.9});\n      const stone=material(0x565078), gold=material(0xc99858), quartz=material(0xa99aaf), ground=material(0x202744);\n      function mesh(geometry,mat,x,y,z){\n        const object=new THREE.Mesh(geometry,mat);\n        object.position.set(x,y,z);scene.add(object);return object;\n      }\n      function box(w,h,d,mat,x,y,z){return mesh(new THREE.BoxGeometry(w,h,d),mat,x,y,z);}\n      box(17,.5,11,ground,0,-.28,0);\n      mesh(new THREE.DodecahedronGeometry(2.25,0),stone,-3.4,1.18,-.7).scale.set(1.25,.76,1);\n      box(1.05,.54,.9,quartz,-3.4,2.72,-.7);box(.7,.28,.75,gold,-3.4,3.12,-.7);\n      for(let i=0;i<7;i++)box(2.6-i*.31,.36,1.75-i*.19,i%2?quartz:gold,3.2,.18+i*.36,-1.7);\n      for(let i=0;i<19;i++){\n        const x=(i%7-3)*1.1,z=(Math.floor(i/7)-2)*1.1-1.9,h=.22+(i*13%15)/24;\n        if(Math.abs(x+3.4)<1.8&&z> -2.9) continue;\n        box(.62,h,.56,i%3?stone:quartz,x,h/2,z);\n      }\n      const pinMaterial=new THREE.MeshStandardMaterial({color:0xffca73,emissive:0xf59a43,emissiveIntensity:.35,roughness:.35});\n      mesh(new THREE.TorusGeometry(.49,.13,8,24),pinMaterial,.1,2.14,.4);\n      mesh(new THREE.ConeGeometry(.23,.62,5),pinMaterial,.1,1.49,.4).rotation.z=Math.PI;\n      const lamp=new THREE.PointLight(0xffae59,4,8);\n      lamp.position.set(.1,2.1,.5);scene.add(lamp);\n      const riverMaterial=new THREE.ShaderMaterial({\n        uniforms:{clock:{value:0}},\n        vertexShader:\"varying vec2 v; void main(){v=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}\",\n        fragmentShader:\"uniform float clock; varying vec2 v; void main(){float edge=smoothstep(.0,.14,v.y)*(1.-smoothstep(.86,1.,v.y)); float wave=sin(v.x*80.+sin(v.y*26.)-clock*2.); gl_FragColor=vec4(mix(vec3(.06,.33,.38),vec3(.25,.75,.72),(.24+.22*wave)*edge),1.);}\"\n      });\n      const river=mesh(new THREE.PlaneGeometry(15,1.38),riverMaterial,0,.02,2.84);\n      river.rotation.x=-Math.PI/2;\n      const particles=new THREE.BufferGeometry();\n      const count=desktop.matches && (navigator.hardwareConcurrency||4)>4?28:10;\n      const points=[];\n      for(let i=0;i<count;i++)points.push(Math.sin(i*13.31)*7,.35+(i%7)*.25,Math.cos(i*18.13)*4.1);\n      particles.setAttribute(\"position\",new THREE.Float32BufferAttribute(points,3));\n      const flies=new THREE.Points(particles,new THREE.PointsMaterial({color:0xffd27c,size:.075,transparent:true,opacity:.75}));\n      scene.add(flies);\n      let progress=0, visible=true, frame=0;\n      const size=()=>{const w=place.clientWidth,h=place.clientHeight;if(!w||!h)return;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();};\n      const render=(tick=0)=>{\n        const [color,power]=opts[root.dataset.nightPhase]||opts.night;\n        sun.color.setHex(color);sun.intensity=power;\n        camera.position.set(10-7*progress,7-3*progress,13-5*progress);\n        camera.lookAt(0,0,0);\n        lamp.intensity=3+progress*27;\n        pinMaterial.emissiveIntensity=.4+progress*1.7;\n        riverMaterial.uniforms.clock.value=tick/1000;\n        flies.rotation.y=tick/40000;\n        renderer.render(scene,camera);\n      };\n      const update=()=>{\n        const rect=hero.getBoundingClientRect();\n        progress=motion.matches?0:Math.max(0,Math.min(1,-rect.top/Math.max(180,rect.height*.55)));\n      };\n      function animate(t){frame=0;if(!visible||document.hidden||motion.matches)return;update();render(t);frame=requestAnimationFrame(animate);}\n      function resume(){\n        cancelAnimationFrame(frame);frame=0;\n        if(motion.matches){update();render();}\n        else if(visible&&!document.hidden)frame=requestAnimationFrame(animate);\n      }\n      stage.addEventListener(\"webglcontextlost\",()=>{stage.hidden=true;place.classList.remove(\"night-rendered\");visible=false;resume();});\n      place.dataset.city=\"webgl\";stage.hidden=false;place.classList.add(\"night-rendered\");size();render();paint=()=>render(performance.now());\n      new ResizeObserver(()=>{size();paint();}).observe(place);\n      new IntersectionObserver(([entry])=>{visible=entry.isIntersecting;resume();}).observe(place);\n      motion.addEventListener(\"change\",resume);\n      document.addEventListener(\"visibilitychange\",resume);\n      resume();\n      if(!desktop.matches||motion.matches)return;\n      try{\n        await loadScript(\"gsap.min.js\");\n        await Promise.all([loadScript(\"ScrollTrigger.min.js\"),loadScript(\"lenis.min.js\")]);\n        if(motion.matches)return;\n        const lenis=new window.Lenis({smoothWheel:true,duration:.8,anchors:false});\n        window.gsap.registerPlugin(window.ScrollTrigger);\n        const updateScroll=t=>lenis.raf(t*1000);\n        window.gsap.ticker.add(updateScroll);\n        lenis.on(\"scroll\",window.ScrollTrigger.update);\n        window.ScrollTrigger.create({trigger:hero,start:\"top top\",end:\"bottom top\",onUpdate:update});\n        motion.addEventListener(\"change\",()=>{if(motion.matches){lenis.destroy();window.gsap.ticker.remove(updateScroll);}},{once:true});\n      }catch{/* Native scrolling stays available. */}\n    }).catch(error=>{stage.hidden=true;place.dataset.city=\"fallback\";place.classList.remove(\"night-rendered\");console.warn(\"Night City WebGL fallback\", error.message);});\n  }\n  if(\"requestIdleCallback\" in window)requestIdleCallback(loadCity,{timeout:1800});\n  else setTimeout(loadCity,500);\n\n  if(desktop.matches&&!motion.matches){\n    const firefly=document.createElement(\"i\");\n    firefly.hidden=true;\n    firefly.className=\"night-firefly\";firefly.setAttribute(\"aria-hidden\",\"true\");\n    hero.append(firefly);\n    hero.addEventListener(\"pointermove\",event=>{\n      if(motion.matches)return;\n      firefly.style.transform=\"translate(\"+event.clientX+\"px,\"+event.clientY+\"px)\";\n      firefly.hidden=false;\n      const r=place.getBoundingClientRect();\n      place.style.setProperty(\"--lean\",Math.max(-2,Math.min(2,(event.clientX-r.left-r.width/2)/r.width*4))+\"deg\");\n    },{passive:true});\n    hero.addEventListener(\"pointerleave\",()=>{firefly.hidden=true;place.style.setProperty(\"--lean\",\"0deg\");});\n  }\n\n  const sheet=document.createElement(\"details\");sheet.className=\"night-sheet\";sheet.open=true;\n  sheet.innerHTML='<summary>Trip controls</summary><nav aria-label=\"Route planner steps\"></nav>';\n  const card=byId(\"state-route\")?.parentElement;\n  if(card){\n    card.before(sheet);sheet.append(card);\n    const controls=[[\"Area\",\"state-area\"],[\"Points\",\"state-start\"],[\"Time\",\"night-departure\"],[\"Routes\",\"state-route\"]];\n    const time=document.createElement(\"label\");\n    time.className=\"night-time\";\n    time.innerHTML='<span>Planned departure</span><input id=\"night-departure\" type=\"datetime-local\"><small>Optional trip note. Phase 1 route calculations use the selected travel mode.</small>';\n    byId(\"state-route\").before(time);\n    for(const [label,id] of controls){\n      const button=document.createElement(\"button\");button.textContent=label;button.type=\"button\";\n      button.onclick=()=>{\n        sheet.open=true;\n        const target=byId(id);\n        target.scrollIntoView({block:\"center\"});\n        if(!target.disabled)target.focus({preventScroll:true});\n      };\n      sheet.querySelector(\"nav\").append(button);\n    }\n  }\n  const emergency=document.createElement(\"a\");\n  emergency.href=\"tel:112\";emergency.className=\"night-sos\";emergency.textContent=\"SOS / 112\";\n  emergency.setAttribute(\"aria-label\",\"Call emergency services 112\");\n  document.body.append(emergency);\n  document.querySelectorAll(\"dialog\").forEach(dialog=>dialog.append(emergency.cloneNode(true)));\n\n})();\n", encoding="utf-8")
Path("credits.html").write_text("<!doctype html><html lang=\"en\"><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>Credits and licences | SafeLink</title><link rel=\"stylesheet\" href=\"night-assets/fonts.css\"><style>body{background:#171c3a;color:#fff9ed;font:1rem Nunito,system-ui,sans-serif;max-width:60rem;margin:auto;padding:1.3rem;line-height:1.6}a{color:#96f0df}details{margin:1rem 0;border:1px solid #8b94bb;padding:.7rem}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style><main><a href=\"./\">Back to SafeLink</a><h1>Credits and licences</h1><details><summary>Night City libraries and fonts</summary><ul><li><a href=\"night-assets/three-license.txt\">Three.js MIT licence</a></li><li><a href=\"https://gsap.com/standard-license/\">GSAP and ScrollTrigger standard licence</a></li><li><a href=\"night-assets/lenis-license.txt\">Lenis MIT licence</a></li><li><a href=\"night-assets/opening-hours-license.txt\">opening_hours.js licence</a></li><li><a href=\"night-assets/qrcode-license.txt\">QR Code Generator licence</a></li><li><a href=\"night-assets/jsQR-license.txt\">jsQR licence</a></li><li><a href=\"night-assets/suncalc-license.txt\">SunCalc BSD licence</a></li><li><a href=\"night-assets/nunito-OFL.txt\">Nunito OFL</a></li><li><a href=\"night-assets/baloo2-OFL.txt\">Baloo 2 OFL</a></li><li><a href=\"night-assets/baloothambi2-OFL.txt\">Baloo Thambi 2 Tamil OFL</a></li></ul></details><details><summary>Map and weather sources</summary><p><a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap contributors</a> · <a href=\"https://openfreemap.org/\">OpenFreeMap</a> · <a href=\"https://www.geoboundaries.org/\">geoBoundaries</a> · <a href=\"https://project-osrm.org/\">OSRM</a> · <a href=\"https://wiki.openstreetmap.org/wiki/Overpass_API\">Overpass</a> · <a href=\"https://open-meteo.com/\">Open-Meteo</a> · <a href=\"https://goto.arcgisonline.com/maps/World_Imagery\">Esri World Imagery</a></p></details>" + "".join(credits) + '<p><a href="tel:112">SOS / 112</a></p></main></html>', encoding="utf-8")

Path("walk-toolkit.js").write_text("\n(() => {\n  \"use strict\";\n  const el=id=>document.getElementById(id);\n  const make=(tag,text,attrs={})=>{\n    const node=document.createElement(tag);\n    node.textContent=text;\n    for(const [k,v] of Object.entries(attrs))node.setAttribute(k,v);\n    return node;\n  };\n  const button=(text,action)=>{const b=make(\"button\",text,{type:\"button\"});b.onclick=action;return b;};\n  const reduced=matchMedia(\"(prefers-reduced-motion:reduce)\");\n  const onMain=!!el(\"workspace\"), loads=new Map();\n  const script=(file,global)=>{\n    if(window[global])return Promise.resolve(window[global]);\n    if(!loads.has(file))loads.set(file,new Promise((resolve,reject)=>{\n      const tag=document.createElement(\"script\");tag.src=\"night-assets/\"+file;\n      tag.onload=()=>window[global]?resolve(window[global]):reject(Error(\"Unavailable\"));\n      tag.onerror=reject;document.head.append(tag);\n    }).catch(error=>{loads.delete(file);throw error;}));\n    return loads.get(file);\n  };\n  async function qr(canvas,text){\n    const create=await script(\"qrcode.js\",\"qrcode\");\n    const code=create(0,\"M\");code.addData(text);code.make();\n    const n=code.getModuleCount(),pixel=Math.floor(320/(n+8));\n    canvas.width=canvas.height=(n+8)*pixel;\n    const c=canvas.getContext(\"2d\");c.fillStyle=\"#fff\";c.fillRect(0,0,canvas.width,canvas.height);c.fillStyle=\"#10152a\";\n    for(let y=0;y<n;y++)for(let x=0;x<n;x++)if(code.isDark(y,x))c.fillRect((x+4)*pixel,(y+4)*pixel,pixel,pixel);\n  }\n  if(!onMain){\n    if(el(\"impact-stats\")){\n      try{\n        const stats=JSON.parse(sessionStorage.getItem(\"safelink-impact\")||\"null\");\n        if(stats){\n          const count=Number(stats.facilities)||0,area=Number(stats.area)||0;\n          el(\"impact-stats\").textContent=\"Selected area · \"+count+\" mapped facilities\"+(area>0?\" · \"+(count/area).toFixed(2)+\" facilities per km²\":\"\")+\n            (stats.lit?\" · route sample \"+stats.lit.yes+\"% lit, \"+stats.lit.no+\"% unlit, \"+stats.lit.unknown+\"% unknown.\":\" · Plan a route to see its lighting coverage.\")+\n            (count===0?\" No facilities were returned in the current sample.\":\"\");\n        }\n      }catch{/* Optional session summary. */}\n    }\n    return;\n  }\n  const tools=make(\"section\",\"\",{class:\"safelink-extra safelink-utilities\",id:\"walk-lab\"});\n  tools.append(make(\"h2\",\"Walk toolkit\"));\n  el(\"workspace\").after(tools);\n  const status=make(\"p\",\"\",{role:\"status\"});tools.append(status);\n  const explain=message=>{status.textContent=message;};\n\n  let desiredLock=false,lock;\n  async function refreshLock(){\n    if(!desiredLock||document.hidden||!navigator.wakeLock||lock&&!lock.released)return;\n    try {lock=await navigator.wakeLock.request(\"screen\");explain(\"Screen stays awake while this tab is visible.\");}\n    catch {explain(\"This device could not keep the screen awake.\");}\n  }\n  async function toggleWake(){\n    if(!navigator.wakeLock){explain(\"Screen Wake Lock is unavailable.\");return;}\n    desiredLock=!desiredLock;\n    wake.setAttribute(\"aria-pressed\",String(desiredLock));\n    if(desiredLock)await refreshLock();\n    else{await lock?.release().catch(()=>{});lock=null;explain(\"Normal screen timeout restored.\");}\n  }\n  const wake=button(\"Keep screen awake\",toggleWake);\n  wake.setAttribute(\"aria-pressed\",\"false\");tools.append(wake);\n  document.addEventListener(\"visibilitychange\",refreshLock);\n  window.addEventListener(\"pagehide\",()=>{desiredLock=false;lock?.release().catch(()=>{});});\n\n  let snapshot=null;\n  window.addEventListener(\"safelink:trip\",event=>{snapshot=event.detail;});\n  const share=button(\"Share trip\",async()=>{\n    window.dispatchEvent(new Event(\"safelink:share-request\"));\n    if(!snapshot){explain(\"Choose a start and destination first.\");return;}\n    const url=new URL(\".\",location.href);\n    url.hash=\"trip=\"+encodeURIComponent(JSON.stringify(snapshot));\n    const text=\"My SafeLink trip · \"+snapshot.mode.toUpperCase()+\". Open the link to review the selected points.\";\n    try{\n      if(navigator.share){await navigator.share({title:\"SafeLink trip\",text,url:url.href});explain(\"Share sheet closed.\");}\n      else if(navigator.clipboard){await navigator.clipboard.writeText(text+\" \"+url.href);explain(\"Trip link copied. Share it with someone you trust.\");}\n      else {const link=make(\"a\",\"Open trip snapshot\",{href:url.href});status.replaceChildren(link);}\n    }catch(error){if(error.name!==\"AbortError\")explain(\"Sharing is unavailable on this device.\");}\n  });\n  share.title=\"Includes your selected map points in the shared link\";\n  tools.append(share);\n\n  const chat=document.createElement(\"dialog\");\n  chat.className=\"safelink-extra\";\n  chat.innerHTML='<h2>Simulated chat</h2><p>This conversation stays on your device.</p><div data-thread aria-live=\"polite\"></div>';\n  const messages={\n    \"Are you close?\":\"I’m close by. I’ll meet you at the entrance.\",\n    \"Stay on chat\":\"I’m here. Take your time.\",\n    \"Where should I wait?\":\"Let’s meet inside near the main entrance.\"\n  };\n  for(const [prompt,reply] of Object.entries(messages))chat.append(button(prompt,()=>{\n    chat.querySelector(\"[data-thread]\").replaceChildren(make(\"p\",prompt),make(\"p\",reply));\n  }));\n  chat.append(button(\"Close\",()=>chat.close()));\n  tools.append(chat,button(\"Simulated chat\",()=>chat.showModal()));\n\n  const guide=button(\"Speak next step\",()=>{\n    const tamil=document.documentElement.lang===\"ta\", synth=window.speechSynthesis;\n    const voice=synth?.getVoices().find(v=>v.localService&&v.lang.toLowerCase().startsWith(tamil?\"ta\":\"en\"));\n    const text=tamil?\"தொடக்கத்தையும் சேருமிடத்தையும் தேர்ந்தெடுக்கவும்.\":\"Choose a start and destination, then find your route.\";\n    if(!voice){explain(text);return;}\n    const speech=new SpeechSynthesisUtterance(text);speech.voice=voice;speech.lang=voice.lang;synth.speak(speech);\n  });\n  tools.append(guide);\n  const lang=make(\"select\",\"\",{\"aria-label\":\"Display language\"});\n  lang.add(new Option(\"English\",\"en\"));lang.add(new Option(\"தமிழ்\",\"ta\"));tools.append(lang);\n  let dictionary={},english=new WeakMap();\n  async function localize(){\n    const isTamil=lang.value===\"ta\";\n    if(isTamil&&!Object.keys(dictionary).length){\n      try{dictionary=await fetch(\"i18n-ta.json\").then(r=>r.json());}catch{explain(\"Tamil labels could not load.\");return;}\n    }\n    document.documentElement.lang=lang.value;\n    const nodes=document.querySelectorAll(\"button,summary,h1,h2,h3,label,nav a,p,option\");\n    for(const node of nodes){\n      if(node.children.length!==0)continue;\n      const original=english.get(node)??node.textContent.trim();\n      if(!Object.hasOwn(dictionary,original))continue;\n      english.set(node,original);node.textContent=isTamil?dictionary[original]:original;\n    }\n    explain(isTamil?\"தமிழ் வழிசெலுத்தல் · சில தரவுகளும் அறிவிப்புகளும் ஆங்கிலத்தில் இருக்கும்.\":\"English display\");\n  }\n  lang.onchange=localize;\n\n  el(\"night-departure\")?.addEventListener(\"change\",()=>window.dispatchEvent(new Event(\"safelink:departure\")));\n  const reportPanel=make(\"details\",\"\",{class:\"safelink-extra\"});\n  reportPanel.append(make(\"summary\",\"Report QR exchange\"));\n  const qrView=make(\"canvas\",\"\",{role:\"img\",\"aria-label\":\"Report QR frame\",hidden:\"\"});\n  const qrStatus=make(\"p\",\"\",{role:\"status\"});\n  let frames=[],frame=0,qrTimer=0,activeSequence=0;\n  async function paintFrame(){\n    if(!frames.length)return;\n    const seq=activeSequence, i=frame%frames.length;\n    frame++;\n    try{\n      await qr(qrView,frames[i]);\n      if(seq!==activeSequence)return;\n      qrView.hidden=false;qrStatus.textContent=\"Frame \"+(i+1)+\" of \"+frames.length;\n    }catch {qrStatus.textContent=\"QR display unavailable. Use the JSON bundle exchange.\";}\n  }\n  const startQR=button(\"Make report QR\",()=>{\n    window.dispatchEvent(new Event(\"safelink:qr-export\"));\n  });\n  reportPanel.append(startQR,button(\"Next QR frame\",paintFrame),qrView,qrStatus);\n  reportPanel.addEventListener(\"toggle\",()=>{if(!reportPanel.open)clearInterval(qrTimer);});\n  document.addEventListener(\"visibilitychange\",()=>{if(document.hidden)clearInterval(qrTimer);});\n  window.addEventListener(\"safelink:qr-data\",event=>{\n    clearInterval(qrTimer);activeSequence++;\n    if(!event.detail?.reports?.length){qrStatus.textContent=\"Save a mapped report first.\";return;}\n    const payload=JSON.stringify(event.detail);\n    const id=crypto.randomUUID().slice(0,8);\n    const chunks=payload.match(/[\\s\\S]{1,600}/g);\n    frames=chunks.map((chunk,index)=>\"SLQ1|\"+id+\"|\"+(index+1)+\"|\"+chunks.length+\"|\"+chunk);\n    frame=0;paintFrame();\n    if(frames.length>1&&!reduced.matches)qrTimer=setInterval(paintFrame,1250);\n  });\n  const scanner=make(\"input\",\"\",{type:\"file\",accept:\"image/*\",multiple:\"\",\"aria-label\":\"Import screenshots of report QR frames\"});\n  const collected=new Map();\n  function acceptFrame(value){\n    const header=/^SLQ1\\|([0-9a-f]{8})\\|(\\d{1,3})\\|(\\d{1,3})\\|/.exec(value);\n    if(!header)return false;\n    const [,id,i,count]=header,index=Number(i),total=Number(count);\n    if(total<1||total>100||index<1||index>total||value.length>700)return false;\n    if(!collected.has(id)){if(collected.size>=4)collected.delete(collected.keys().next().value);collected.set(id,{total,parts:new Map()});}\n    const set=collected.get(id);\n    if(set.total!==total)return false;\n    set.parts.set(index,value.slice(header[0].length));\n    if(set.parts.size!==total){qrStatus.textContent=set.parts.size+\" of \"+total+\" frames read.\";return true;}\n    try{\n      const packet=JSON.parse(Array.from({length:total},(_,j)=>set.parts.get(j+1)).join(\"\"));\n      window.dispatchEvent(new CustomEvent(\"safelink:qr-import\",{detail:packet}));\n      collected.delete(id);\n    }catch{qrStatus.textContent=\"Invalid report bundle.\";}\n    return true;\n  }\n  scanner.onchange=async()=>{\n    try{\n      const read=await script(\"jsQR.js\",\"jsQR\");\n      for(const file of [...scanner.files].slice(0,40)){\n        const bitmap=await createImageBitmap(file);\n        const ratio=Math.min(1,1450/Math.max(bitmap.width,bitmap.height)), canvas=document.createElement(\"canvas\");\n        canvas.width=Math.max(1,Math.round(bitmap.width*ratio));canvas.height=Math.max(1,Math.round(bitmap.height*ratio));\n        const ctx=canvas.getContext(\"2d\",{willReadFrequently:true});\n        ctx.drawImage(bitmap,0,0,canvas.width,canvas.height);bitmap.close();\n        const image=ctx.getImageData(0,0,canvas.width,canvas.height);\n        const result=read(image.data,image.width,image.height);\n        if(!result||!acceptFrame(result.data))qrStatus.textContent=\"Could not read a SafeLink frame from this image.\";\n      }\n    }catch{qrStatus.textContent=\"QR image reading is unavailable.\";}\n    finally{scanner.value=\"\";}\n  };\n  window.addEventListener(\"safelink:qr-status\",event=>{qrStatus.textContent=event.detail;});\n  reportPanel.append(make(\"p\",\"Import one screenshot for each frame. Reports contain map segments, times, and preset observations.\"),scanner);\n  tools.append(reportPanel);\n\n  const practice=make(\"details\",\"\",{class:\"safelink-extra\"});\n  practice.append(make(\"summary\",\"Hazard Spotter · practice\"));\n  const stage=make(\"div\",\"\",{class:\"safelink-hazard-scene\",\"aria-hidden\":\"true\"});\n  stage.innerHTML=\"<i></i><i></i><i></i>\";\n  const rounds=[[\"A lamp is out and the pavement ahead is dark.\",\"lighting\"],[\"A curb leaves a difficult road crossing.\",\"crossing\"],[\"A parked vehicle blocks the footpath.\",\"obstruction\"]];\n  let round=0,correct=0;\n  const quest=make(\"p\",rounds[0][0]), medal=make(\"p\",\"Practice · 0 correct\",{role:\"status\"});\n  const prefill=button(\"Prefill this category\",()=>{\n    const field=el(\"report-kind\");\n    if(!field)return;\n    const option=[...field.options].find(o=>o.value===rounds[round][1]);\n    if(option)field.value=option.value;\n    el(\"journey-tab\")?.click();el(\"report-title\")?.scrollIntoView({block:\"center\"});field.focus({preventScroll:true});\n    explain(\"Practice category selected. Inspect a real segment before saving an observation.\");\n  });\n  practice.append(stage,quest,medal,prefill);\n  for(const [name,key] of [[\"Poor lighting\",\"lighting\"],[\"Difficult crossing\",\"crossing\"],[\"Obstructed pavement\",\"obstruction\"]]){\n    practice.append(button(name,()=>{\n      if(rounds[round][1]!==key){medal.textContent=\"Try another category. Practice only.\";return;}\n      correct++;round=(round+1)%rounds.length;quest.textContent=rounds[round][0];\n      medal.textContent=correct>=3?\"Practice badge · Hazard Spotter\":\"Practice · \"+correct+\" correct\";\n    }));\n  }\n  tools.append(practice);\n\n  const tips=[\"Check which public premises are open before leaving.\",\"Use a named landmark when describing a meeting point.\",\"Charge your phone and save the Trichy offline map before setting off.\",\"Check crossings and pavement on the map, then confirm them in person.\"];\n  tools.append(make(\"p\",\"Daily tip · \"+tips[Math.floor((Date.now()+19800000)/86400000)%tips.length]));\n  const exhibit=make(\"dialog\",\"\",{class:\"safelink-extra safelink-exhibit\"});\n  const slides=[[\"Plan a journey\",\"Select a mapped landmark for either endpoint.\"],[\"Compare routes\",\"Check distances and mapped conditions before travelling.\"],[\"Explore offline Trichy\",\"Try GPS replay and the practice report flow.\"],[\"Try the station\",\"Use the 3D model and its simulation controls.\"]];\n  const headline=make(\"h2\",\"\"),copy=make(\"p\",\"\"),launchQR=make(\"canvas\",\"\",{role:\"img\",\"aria-label\":\"QR code to open SafeLink\"});\n  let index=0,exhibitTimer=0;\n  const show=()=>{const [title,text]=slides[index++%slides.length];headline.textContent=title;copy.textContent=text;};\n  function exhibition(){\n    index=0;show();exhibit.showModal();qr(launchQR,new URL(\".\",location.href).href).catch(()=>{});\n    if(!reduced.matches)exhibitTimer=setInterval(show,6500);\n  }\n  exhibit.append(headline,copy,launchQR,button(\"Next\",show),button(\"Pause cycling\",()=>clearInterval(exhibitTimer)),button(\"Close\",()=>exhibit.close()));\n  exhibit.addEventListener(\"close\",()=>clearInterval(exhibitTimer));\n  tools.append(exhibit,button(\"Exhibition mode\",exhibition));\n  const sequence=[\"ArrowUp\",\"ArrowUp\",\"ArrowDown\",\"ArrowDown\",\"ArrowLeft\",\"ArrowRight\",\"ArrowLeft\",\"ArrowRight\",\"b\",\"a\"];\n  let keys=0;\n  window.addEventListener(\"keydown\",e=>{\n    if(e.target.closest?.(\"input,select,textarea,[contenteditable]\")||exhibit.open)return;\n    keys=e.key.toLowerCase()===sequence[keys].toLowerCase()?keys+1:0;\n    if(keys===sequence.length){keys=0;exhibition();}\n  });\n  window.addEventListener(\"safelink:hero-shake\",()=>{explain(\"Practice badge · Lantern keeper\");});\n  const impact=make(\"a\",\"Impact and coverage\",{href:\"impact.html\"});\n  impact.addEventListener(\"click\",()=>window.dispatchEvent(new Event(\"safelink:impact\")));\n  window.addEventListener(\"safelink:stats\",event=>{try{sessionStorage.setItem(\"safelink-impact\",JSON.stringify(event.detail));}catch{}});\n  tools.append(impact);\n  for(const dialog of tools.querySelectorAll(\"dialog\")) {const sos=make(\"a\",\"SOS / 112\",{class:\"night-sos\",href:\"tel:112\"});dialog.append(sos); }\n})();\n", encoding="utf-8")
Path("i18n-ta.json").write_text("{\"Walk toolkit\":\"நடைப் பயணக் கருவிகள்\",\"Open planner\":\"பயணத் திட்டத்தைத் திற\",\"Start\":\"தொடக்கம்\",\"Destination\":\"சேருமிடம்\",\"Trip controls\":\"பயணக் கட்டுப்பாடுகள்\",\"Area\":\"பகுதி\",\"Points\":\"இடங்கள்\",\"Time\":\"நேரம்\",\"Routes\":\"பாதைகள்\",\"Find route\":\"பாதையைக் கண்டறி\",\"Walk\":\"நடை\",\"Drive\":\"வாகனம்\",\"Clear pins\":\"குறிகளை நீக்கு\",\"Use my location\":\"என் இருப்பிடத்தைப் பயன்படுத்து\",\"Search\":\"தேடு\",\"Set start\":\"தொடக்கமாக அமை\",\"Set destination\":\"சேருமிடமாக அமை\",\"Add stop\":\"இடைநிறுத்தம் சேர்\",\"Ride call\":\"பயண அழைப்பு\",\"Trichy offline\":\"திருச்சி இணையமின்றி\",\"Close\":\"மூடு\",\"Next\":\"அடுத்து\",\"Credits and licences\":\"நன்றியும் உரிமங்களும்\",\"Simulated chat\":\"மாதிரி உரையாடல்\",\"Share trip\":\"பயணத்தைப் பகிர்\",\"Roll a walk\":\"ஒரு நடைப்பாதையைத் தேர்வு செய்\",\"Exhibition mode\":\"கண்காட்சி முறை\",\"Keep screen awake\":\"திரையை இயக்கத்தில் வை\",\"Walk conditions\":\"நடைப்பாதை நிலை\",\"Tamil Nadu\":\"தமிழ்நாடு\",\"Search landmarks\":\"அடையாள இடங்களைத் தேடு\",\"Popular Trichy landmarks\":\"திருச்சியின் பிரபல இடங்கள்\",\"Impact and coverage\":\"தாக்கமும் தரவுப் பரப்பும்\",\"Shortest\":\"குறுகிய பாதை\",\"Sound off\":\"ஒலி அணைப்பு\",\"Sound on\":\"ஒலி இயக்கம்\",\"Simulation\":\"மாதிரி\",\"Connect Arduino\":\"Arduino இணை\",\"Guide\":\"வழிகாட்டு\",\"Report QR exchange\":\"QR வழி அறிக்கை பகிர்வு\"}", encoding="utf-8")
Path("manifest.webmanifest").write_text("{\"id\":\"./\",\"name\":\"SafeLink Night City\",\"short_name\":\"SafeLink\",\"start_url\":\"./\",\"scope\":\"./\",\"display\":\"standalone\",\"background_color\":\"#111633\",\"theme_color\":\"#111633\",\"icons\":[{\"src\":\"safelink-icon.svg\",\"sizes\":\"any\",\"type\":\"image/svg+xml\",\"purpose\":\"any\"}]}", encoding="utf-8")
Path("safelink-icon.svg").write_text("<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 192 192\"><rect width=\"192\" height=\"192\" rx=\"34\" fill=\"#151b3b\"/><path d=\"M96 152A52 52 0 1 1 138 112Z\" fill=\"#ffca72\"/><circle cx=\"96\" cy=\"80\" r=\"19\" fill=\"#151b3b\"/></svg>", encoding="utf-8")
Path("impact.html").write_text("<!doctype html><html lang=\"en\"><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>SafeLink impact</title><link rel=\"stylesheet\" href=\"night-assets/fonts.css\"><style>body{font:1.1rem Nunito,system-ui;color:#fff9ed;background:#1b2143;max-width:54rem;margin:2rem auto;padding:1rem}a{color:#98eadc}section{border:1px solid #858fb9;border-radius:.8rem;padding:1rem}</style><main><a href=\"./\">Back to SafeLink</a><h1>Impact and map coverage</h1><section><h2>Your latest map sample</h2><p id=\"impact-stats\">Use Open data nearby or plan a route, then open this page from Walk toolkit.</p><p>Mapped data may be missing. Facilities per km² is shown only for a single search circle. Sparse coverage may reflect incomplete mapping.</p></section><h2>Improve the map</h2><p>Check streetlights, crossing details and public facility entrances in person. Add verifiable details to OpenStreetMap.</p><p><a href=\"https://www.openstreetmap.org/edit#map=15/10.8/78.683\">Fix the map on OpenStreetMap</a></p><a href=\"tel:112\">SOS / 112</a></main><script type=\"module\" src=\"walk-toolkit.js\"></script></html>", encoding="utf-8")
