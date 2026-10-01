#!/usr/bin/env python3
# Move the header menu (hamburger) button from the LEFT to the RIGHT side,
# in both index.html and app.html. Only reorders; no CSS changes.
import re

def move(path, id_attr):
    s = open(path, encoding='utf-8').read()
    if 'data-menu-moved' in s:
        print('SKIP already moved:', path); return
    pat = r'[ \t]*<button[^>]*' + re.escape(id_attr) + r'[^>]*>[^<]*\u2630[^<]*</button>\n'
    m = re.search(pat, s)
    if not m:
        print('WARN button not found:', path); return
    btn = m.group(0)
    s2 = s[:m.start()] + s[m.end():]
    mc = re.search(r'[ \t]*</header>', s2)
    if not mc:
        print('WARN </header> not found:', path); return
    s2 = s2[:mc.start()] + btn + s2[mc.start():]
    open(path, 'w', encoding='utf-8').write(s2)
    print('MOVED', path)

move('index.html', 'id="siteMenuBtn"')
move('app.html', 'id="menuBtn"')
print('DONE')
