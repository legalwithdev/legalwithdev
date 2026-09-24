#!/usr/bin/env python3
# site-html.py - Chat box ko homepage section ke andar embed karo (HTML nesting + JS scroll).
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

# G1. chatwrap section: header add + section open rakho (close dock ke baad aayega)
rep(
'''    <!-- CHAT: chat start hone pe yahi screen bhar jata hai -->
    <section id="chatwrap">
      <div id="chat"></div>
    </section>
  </main>''',
'''    <!-- WEBSITE VIEW: AI assistant box homepage pe embedded -->
    <section id="chatwrap">
      <div class="chat-head">⚖️ <b>Ask Dev</b> — AI Legal Assistant</div>
      <div id="chat"></div>''',
"chatwrap open + head",
)

# G2. dock ke baad section + main close karo (dock ab section ke andar)
rep(
'''    <div class="hint">AI legal information — not advice. Consult a qualified Advocate for your case. Do not share sensitive personal info in chat.</div>
  </div>''',
'''    <div class="hint">AI legal information — not advice. Consult a qualified Advocate for your case. Do not share sensitive personal info in chat.</div>
  </div>
    </section>
  </main>''',
"section close after dock",
)

# H. JS: chat start hone pe poora page nahi, bas chat box pe smooth scroll
rep(
'''  document.body.classList.add('chatting'); // CHAT MODE: home gayab, sirf chat''',
'''  document.getElementById('chatwrap').scrollIntoView({ behavior: 'smooth' }); // WEBSITE VIEW: chat box pe scroll''',
"js scroll to box",
)

open(PATH, "w", encoding="utf-8").write(src)
print("ALL HTML PATCHES APPLIED")
