#!/usr/bin/env python3
# Open the menu drawer/sidebar from the RIGHT (matches the right-side menu button).
import sys

def rep(path, old, new):
    s = open(path, encoding='utf-8').read()
    if new in s:
        print('SKIP already done:', path); return
    if old not in s:
        print('WARN anchor not found in', path); sys.exit(1)
    s = s.replace(old, new, 1)
    open(path, 'w', encoding='utf-8').write(s)
    print('PATCHED', path)

# ---- index.html: #siteMenu (left -> right) ----
OLD_I = """  #siteMenu {
    position: fixed; z-index: 300; top: 0; left: 0; bottom: 0; width: 275px;
    background: var(--glass-bg); border-right: 1px solid var(--glass-line); border-radius: 0 20px 20px 0; transform: translateX(-105%);"""
NEW_I = """  #siteMenu {
    position: fixed; z-index: 300; top: 0; right: 0; bottom: 0; width: 275px;
    background: var(--glass-bg); border-left: 1px solid var(--glass-line); border-radius: 20px 0 0 20px; transform: translateX(105%);"""
rep('index.html', OLD_I, NEW_I)

# ---- app.html: #sidebar (left -> right), desktop + mobile ----
OLD_A1 = """  #sidebar {
    width: 262px; flex-shrink: 0; background: rgba(13,19,38,.6); border-right: 1px solid var(--line);
    display: flex; flex-direction: column; transition: margin-left .25s ease;
  }
  #sidebar.closed { margin-left: -262px; }"""
NEW_A1 = """  #sidebar {
    width: 262px; flex-shrink: 0; background: rgba(13,19,38,.6); border-left: 1px solid var(--line);
    display: flex; flex-direction: column; transition: margin-right .25s ease; order: 2;
  }
  #sidebar.closed { margin-right: -262px; }"""
rep('app.html', OLD_A1, NEW_A1)

OLD_A2 = """    #sidebar { position: fixed; z-index: 200; top: 57px; bottom: 0; background: rgba(13,19,38,.97); }
    #sidebar.closed { margin-left: -280px; }"""
NEW_A2 = """    #sidebar { position: fixed; z-index: 200; top: 57px; right: 0; bottom: 0; background: rgba(13,19,38,.97); }
    #sidebar.closed { margin-right: -280px; }"""
rep('app.html', OLD_A2, NEW_A2)

print('DONE')
