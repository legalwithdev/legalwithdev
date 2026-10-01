#!/usr/bin/env python3
# Add "Watch legal videos" button (above chat box, right) + video overlay to
# index.html and app.html in place. Additive only; idempotent.
import sys

CSS_INDEX = """
  /* ---- WATCH VIDEOS (play button above chat box, right) ---- */
  .dock .vidsrow { max-width: 740px; margin: 0 auto 8px; padding: 0 4px; display: flex; justify-content: flex-end; }
  .vidbtn {
    display: inline-flex; align-items: center; gap: 7px; cursor: pointer;
    border: 1px solid var(--glass-line); background: var(--glass-bg); color: var(--ink);
    border-radius: 999px; padding: 8px 14px; font-size: 13px; font-family: inherit;
    -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(1.5); backdrop-filter: blur(var(--glass-blur)) saturate(1.5);
    box-shadow: 0 1px 6px rgba(0,0,0,.15);
  }
  .vidbtn svg { width: 15px; height: 15px; }
  .vidbtn:active { background: var(--surface2); }
  .vidover { position: fixed; inset: 0; z-index: 90; display: none; align-items: center; justify-content: center; padding: 18px; background: rgba(6,12,22,.72); -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px); }
  .vidover.on { display: flex; }
  .vidpanel { width: 100%; max-width: 560px; max-height: 86vh; overflow: auto; background: var(--surface); color: var(--ink); border: 1px solid var(--glass-line); border-radius: 18px; padding: 16px; }
  .vidhead { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
  .vidhead b { font-size: 16px; }
  .vidclose { border: 1px solid var(--glass-line); background: transparent; color: var(--ink); width: 34px; height: 34px; border-radius: 10px; cursor: pointer; font-size: 15px; }
  .vidempty { font-size: 13.5px; color: var(--muted); line-height: 1.6; }
</style>"""

CSS_APP = """
  /* ---- WATCH VIDEOS (play button above chat box, right) ---- */
  .vidsrow { max-width: 820px; margin: 0 auto 8px; padding: 0 2px; display: flex; justify-content: flex-end; }
  .vidbtn { display: inline-flex; align-items: center; gap: 7px; cursor: pointer; border: 1px solid var(--line); background: var(--card); color: var(--ink); border-radius: 999px; padding: 8px 14px; font-size: 13px; font-family: inherit; }
  .vidbtn svg { width: 15px; height: 15px; color: var(--brand2); }
  .vidbtn:active { background: var(--chip-bg); }
  .vidover { position: fixed; inset: 0; z-index: 90; display: none; align-items: center; justify-content: center; padding: 18px; background: rgba(6,12,22,.72); }
  .vidover.on { display: flex; }
  .vidpanel { width: 100%; max-width: 560px; max-height: 86vh; overflow: auto; background: var(--card); color: var(--ink); border: 1px solid var(--line); border-radius: 18px; padding: 16px; }
  .vidhead { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
  .vidhead b { font-size: 16px; }
  .vidclose { border: 1px solid var(--line); background: transparent; color: var(--ink); width: 34px; height: 34px; border-radius: 10px; cursor: pointer; font-size: 15px; }
  .vidempty { font-size: 13.5px; color: var(--muted); line-height: 1.6; }
</style>"""

BTN_INDEX = """    <div class="vidsrow">
      <button id="vidBtn" class="vidbtn" type="button" title="Watch legal videos" aria-label="Watch legal videos">
        <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg><span>Watch legal videos</span>
      </button>
    </div>
    <div class="pill">"""

BTN_APP = """          <div class="vidsrow">
            <button id="vidBtn" class="vidbtn" type="button" title="Watch legal videos" aria-label="Watch legal videos">
              <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg><span>Watch legal videos</span>
            </button>
          </div>
          <div class="ibwrap">"""

OVERLAY = """
  <div id="vidOver" class="vidover" role="dialog" aria-modal="true" aria-label="Legal videos">
    <div class="vidpanel">
      <div class="vidhead"><b>Watch &middot; Legal videos</b><button id="vidClose" class="vidclose" type="button" aria-label="Close">&#10005;</button></div>
      <p class="vidempty">Legal explainer videos will appear here &mdash; short, simple walkthroughs of common situations. This is general information, not legal advice.</p>
    </div>
  </div>
"""

SCRIPT = """  <script>
  (function(){
    var b=document.getElementById('vidBtn'), o=document.getElementById('vidOver'), c=document.getElementById('vidClose');
    if(b&&o) b.addEventListener('click',function(){ o.classList.add('on'); });
    if(c&&o) c.addEventListener('click',function(){ o.classList.remove('on'); });
    if(o) o.addEventListener('click',function(e){ if(e.target===o) o.classList.remove('on'); });
  })();
  </script>
</body>"""


def patch_index(s):
    assert s.count('</style>') == 1
    s = s.replace('</style>', CSS_INDEX, 1)
    assert s.count('<div class="pill">') == 1
    s = s.replace('<div class="pill">', BTN_INDEX, 1)
    assert s.count('<div id="toast"') == 1
    s = s.replace('<div id="toast"', OVERLAY + '\n  <div id="toast"', 1)
    assert s.count('</body>') == 1
    s = s.replace('</body>', SCRIPT, 1)
    return s


def patch_app(s):
    assert s.count('</style>') == 1
    s = s.replace('</style>', CSS_APP, 1)
    assert s.count('<div class="ibwrap">') == 1
    s = s.replace('<div class="ibwrap">', BTN_APP, 1)
    assert s.count('</body>') == 1
    s = s.replace('</body>', OVERLAY + SCRIPT, 1)
    return s


changed = []
for p, fn in [('index.html', patch_index), ('app.html', patch_app)]:
    s = open(p, encoding='utf-8').read()
    if 'id="vidBtn"' in s:
        print('SKIP already patched:', p)
        continue
    out = fn(s)
    open(p, 'w', encoding='utf-8').write(out)
    print('PATCHED', p, len(s), '->', len(out))
    changed.append(p)

print('DONE changed=', changed)
