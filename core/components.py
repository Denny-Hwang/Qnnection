"""core/components.py – JS 컴포넌트: 키보드 단축키, 효과음, JS 카운트다운.

Streamlit의 server-side rerun 부담을 줄이기 위해, 시각적 카운트다운과
키보드/오디오는 모두 클라이언트 측에서 처리한다. 서버는 액션과 시간 만료만 관리.
"""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components


# ─────────────────────────────────────────────────────────
#  키보드 단축키
# ─────────────────────────────────────────────────────────
# 페이지의 button 텍스트와 키를 매칭. 부모 document 상의 버튼을 클릭.
# 중복 설치 방지를 위해 window.parent에 플래그.
_KEYBOARD_JS = """
<script>
(function() {
    const parentWin = window.parent;
    const parentDoc = parentWin.document;
    if (parentWin._qnnection_kbd_installed) return;
    parentWin._qnnection_kbd_installed = true;

    // 핸들러 본체는 parent 컨텍스트의 <script>로 주입해야
    // 본 iframe이 destroy되어도 closure가 살아남는다.
    const script = parentDoc.createElement('script');
    script.textContent = `
    (function() {
        function matches(btnText, candidates) {
            const t = (btnText || '').toLowerCase();
            return candidates.some(c => t.includes(String(c).toLowerCase()));
        }
        function clickByCandidates(candidates) {
            const buttons = document.querySelectorAll('button');
            for (const btn of buttons) {
                const text = (btn.textContent || '').trim();
                if (!text) continue;
                if (btn.disabled) continue;
                if (matches(text, candidates)) {
                    btn.click();
                    return true;
                }
            }
            return false;
        }
        function handler(e) {
            const tag = (e.target.tagName || '').toLowerCase();
            if (tag === 'input' || tag === 'textarea' || tag === 'select') return;
            if (e.metaKey || e.ctrlKey || e.altKey) return;
            let candidates = null;
            switch (e.code) {
                case 'Space':
                    candidates = ['Correct', '정답', 'Next', '다음', 'Start', 'Resume'];
                    break;
                case 'ArrowRight':
                    candidates = ['Next', '다음'];
                    break;
                case 'ArrowLeft':
                    candidates = ['Prev', '이전'];
                    break;
                case 'KeyY':
                    candidates = ['Correct', '정답'];
                    break;
                case 'KeyN':
                    candidates = ['Pass', '패스'];
                    break;
                case 'KeyP':
                    candidates = ['Pause', '일시정지', 'Resume'];
                    break;
                case 'KeyZ':
                    candidates = ['Undo'];
                    break;
                case 'KeyS':
                    candidates = ['Shuffle', '셔플'];
                    break;
                default:
                    return;
            }
            if (clickByCandidates(candidates)) {
                e.preventDefault();
            }
        }
        document.addEventListener('keydown', handler, { capture: true });
    })();
    `;
    parentDoc.head.appendChild(script);
})();
</script>
"""


def install_keyboard_shortcuts() -> None:
    """페이지에 단축키 핸들러 한 번만 설치. height=0으로 레이아웃 무영향."""
    components.html(_KEYBOARD_JS, height=0)


# ─────────────────────────────────────────────────────────
#  효과음 (Web Audio API, 외부 자원 불필요)
# ─────────────────────────────────────────────────────────
_SOUND_JS_TEMPLATE = """
<script>
(function() {{
    const parentWin = window.parent;
    function ensureCtx() {{
        if (!parentWin._qnnection_audio) {{
            const AC = parentWin.AudioContext || parentWin.webkitAudioContext;
            if (!AC) return null;
            parentWin._qnnection_audio = new AC();
        }}
        return parentWin._qnnection_audio;
    }}
    function tone(freq, duration, type, gain) {{
        const ctx = ensureCtx();
        if (!ctx) return;
        if (ctx.state === 'suspended') ctx.resume();
        const o = ctx.createOscillator();
        const g = ctx.createGain();
        o.type = type || 'sine';
        o.frequency.value = freq;
        g.gain.value = gain || 0.15;
        o.connect(g); g.connect(ctx.destination);
        const t = ctx.currentTime;
        g.gain.setValueAtTime(gain || 0.15, t);
        g.gain.exponentialRampToValueAtTime(0.0001, t + duration);
        o.start(t);
        o.stop(t + duration);
    }}
    const KIND = "{kind}";
    if (KIND === 'correct') {{
        tone(880, 0.10, 'sine', 0.18);
        setTimeout(() => tone(1320, 0.15, 'sine', 0.18), 90);
    }} else if (KIND === 'pass') {{
        tone(196, 0.20, 'sawtooth', 0.10);
    }} else if (KIND === 'start') {{
        tone(523, 0.10, 'square', 0.10);
        setTimeout(() => tone(784, 0.18, 'square', 0.10), 90);
    }} else if (KIND === 'finish') {{
        tone(659, 0.12, 'triangle', 0.14);
        setTimeout(() => tone(784, 0.12, 'triangle', 0.14), 110);
        setTimeout(() => tone(988, 0.18, 'triangle', 0.14), 220);
    }} else if (KIND === 'tick') {{
        tone(1200, 0.06, 'square', 0.08);
    }}
}})();
</script>
"""


def play_sound(kind: str) -> None:
    """효과음 재생. kind ∈ {correct, pass, start, finish, tick}."""
    if not st.session_state.get("sound_on", True):
        return
    components.html(_SOUND_JS_TEMPLATE.format(kind=kind), height=0)


# ─────────────────────────────────────────────────────────
#  클라이언트 사이드 카운트다운 (시각용)
# ─────────────────────────────────────────────────────────
_TIMER_JS_TEMPLATE = """
<div id="qn-timer-{uid}" class="timer-display timer-green" aria-live="off">{initial}s</div>
<div class="timer-bar" role="progressbar" aria-valuemax="{total}">
  <div id="qn-bar-{uid}" class="timer-bar-fill" style="width:100%;background:#4ECDC4;"></div>
</div>
<script>
(function() {{
    const display = document.getElementById('qn-timer-{uid}');
    const bar = document.getElementById('qn-bar-{uid}');
    if (!display) return;
    const total = {total};
    const startEpoch = {start_epoch};
    const initial = {initial};
    let last = -1;
    function tick() {{
        const now = Date.now() / 1000;
        const elapsed = Math.max(0, now - startEpoch);
        const rem = Math.max(0, initial - elapsed);
        const shown = Math.ceil(rem);
        if (shown !== last) {{
            display.textContent = shown + 's';
            last = shown;
        }}
        const pct = total > 0 ? Math.max(0, Math.min(1, rem / total)) * 100 : 0;
        bar.style.width = pct + '%';
        if (rem > total * 0.5) {{
            display.className = 'timer-display timer-green';
            bar.style.background = '#4ECDC4';
        }} else if (rem > total * 0.2) {{
            display.className = 'timer-display timer-yellow';
            bar.style.background = '#FFE66D';
        }} else {{
            display.className = 'timer-display timer-red';
            bar.style.background = '#FF6B6B';
        }}
        if (rem > 0) requestAnimationFrame(tick);
    }}
    tick();
}})();
</script>
"""


def render_running_timer(start_epoch: float, initial_remaining: float, total: float, uid: str) -> None:
    """JS 카운트다운 + 진행바를 클라이언트에서 직접 갱신한다.

    start_epoch: 카운트다운 기준 시각(Unix epoch, 초 단위).
    initial_remaining: 그 시점에서 남은 초.
    total: 전체 시간(초).
    uid: 중복 ID 방지 식별자.
    """
    html = _TIMER_JS_TEMPLATE.format(
        uid=uid,
        initial=int(initial_remaining),
        total=int(total),
        start_epoch=f"{start_epoch:.3f}",
    )
    # 타이머 + 진행바 합쳐 약 90px
    components.html(html, height=110)
