#!/usr/bin/env python3
# site-css.py - Website-view CSS: app-style full-screen chat ko homepage EMBEDDED box banao.
# Exact-match replacements - koi string na mile to FAIL (koi guess nahi).
import sys

PATH = "index.html"
src = open(PATH, encoding="utf-8").read()

def rep(old, new, what):
    global src
    if old not in src:
        print("FAIL: not found ->", what)
        sys.exit(1)
    if src.count(old) != 1:
        print("FAIL: not unique ->", what)
        sys.exit(1)
    src = src.replace(old, new)
    print("OK:", what)

# A. body: app-mode (height 100%, overflow hidden) -> website page scroll
rep(
'''  html, body { min-height: 100%; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans", "Noto Sans Devanagari", sans-serif;
    background: var(--bg); color: var(--ink);
    display: flex; flex-direction: column; overflow-x: hidden;
  }''',
'''  html, body { height: 100%; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans", "Noto Sans Devanagari", sans-serif;
    background: var(--bg); color: var(--ink);
    display: flex; flex-direction: column; overflow: hidden;
  }''',
"body website scroll",
)

# B. main: internal scroller hatao (page scroll karega)
rep(
'''  main { flex: 1; display: flex; flex-direction: column; }''',
'''  main { flex: 1; overflow-y: auto; display: flex; flex-direction: column; min-height: 0; }''',
"main no internal scroll",
)

# C. #home: hero section - hamesha visible, natural height
rep(
'''  #home { display: flex; flex-direction: column; align-items: center; justify-content: flex-start; padding: 26px 16px 6px; text-align: center; }''',
'''  #home { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 24px 16px 150px; text-align: center; }''',
"home always visible",
)

# D. chat rules: full-screen takeover -> homepage EMBEDDED box
rep(
'''  /* WEBSITE VIEW: chat box homepage pe hi rehta hai, home kabhi gayab nahi hota */
  #chatwrap { display: flex; flex-direction: column; width: calc(100% - 24px); max-width: 760px; margin: 14px auto 8px; height: 68vh; min-height: 400px; max-height: 660px; border: 1px solid var(--glass-line); border-radius: 22px; background: var(--glass-bg); box-shadow: 0 18px 48px rgba(0,0,0,.22); overflow: hidden; -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(1.5); backdrop-filter: blur(var(--glass-blur)) saturate(1.5); }
  .chat-head { display: flex; align-items: center; gap: 7px; padding: 11px 16px; border-bottom: 1px solid var(--glass-line); font-size: 13.5px; color: var(--ink); background: var(--surface2); flex-shrink: 0; }
  .chat-head b { font-weight: 650; }''',
'''  body.chatting #home { display: none; }
  #chatwrap { display: none; flex: 1; flex-direction: column; min-height: 0; }
  body.chatting #chatwrap { display: flex; }''',
"chatwrap embedded box",
)

# E. #chat padding: dock ab box ke andar hai, 150px bottom zaroori nahi
rep(
'''  #chat { flex: 1; overflow-y: auto; padding: 14px 12px 4px; display: flex; flex-direction: column; gap: 16px; }''',
'''  #chat { flex: 1; overflow-y: auto; padding: 14px 12px 150px; display: flex; flex-direction: column; gap: 16px; }''',
"chat padding",
)

# F. .dock: fixed bottom overlay -> chat box ke andar static
rep(
'''  .dock {
    position: static; flex-shrink: 0; z-index: 40;
    padding: 8px 10px calc(10px + env(safe-area-inset-bottom, 0px));
    background: transparent;
    border-top: 1px solid var(--glass-line);
  }''',
'''  .dock {
    position: fixed; bottom: 0; left: 0; right: 0; z-index: 40;
    padding: 8px 12px calc(12px + env(safe-area-inset-bottom, 0px));
    background: transparent;
  }''',
"dock inside box",
)

open(PATH, "w", encoding="utf-8").write(src)
print("ALL CSS PATCHES APPLIED")
