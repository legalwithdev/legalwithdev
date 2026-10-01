#!/usr/bin/env python3
# Make chat message text bigger and bolder (index.html + app.html).
import sys

def rep(path, old, new):
    s = open(path, encoding='utf-8').read()
    if new in s:
        print('SKIP already done:', path); return
    if old not in s:
        print('WARN anchor not found in', path, '->', old[:60]); sys.exit(1)
    s = s.replace(old, new, 1)
    open(path, 'w', encoding='utf-8').write(s)
    print('PATCHED', path)

# ---- index.html ----
rep('index.html',
    '.msg { border-radius: 20px; padding: 13px 17px; line-height: 1.65; font-size: 14.5px; word-wrap: break-word; max-width: 86%; }',
    '.msg { border-radius: 20px; padding: 13px 17px; line-height: 1.65; font-size: 16.5px; font-weight: 600; word-wrap: break-word; max-width: 86%; }')
rep('index.html', '.msg .sec { font-size: 13px;', '.msg .sec { font-size: 14px;')
rep('index.html',
    'background: rgba(66,133,244,.07); border-radius: 0 10px 10px 0; font-size: 13px;',
    'background: rgba(66,133,244,.07); border-radius: 0 10px 10px 0; font-size: 14px;')

# ---- app.html ----
rep('app.html',
    '.msg { max-width: 86%; padding: 13px 16px; border-radius: 18px; line-height: 1.65; font-size: 14.5px; word-wrap: break-word; }',
    '.msg { max-width: 86%; padding: 13px 16px; border-radius: 18px; line-height: 1.65; font-size: 16.5px; font-weight: 600; word-wrap: break-word; }')
rep('app.html', '.msg .sec { font-size: 13px;', '.msg .sec { font-size: 14px;')
rep('app.html',
    'background: rgba(79,124,255,.07); border-radius: 0 10px 10px 0; font-size: 13px;',
    'background: rgba(79,124,255,.07); border-radius: 0 10px 10px 0; font-size: 14px;')

print('DONE')
