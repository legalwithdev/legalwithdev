#!/usr/bin/env python3
# Add a link to /master (My Creation hub) in the current site.
import sys

def rep(path, old, new):
    s = open(path, encoding='utf-8').read()
    if new in s:
        print('SKIP already done:', path); return
    if old not in s:
        print('WARN anchor not found in', path, '->', old[:60]); sys.exit(1)
    open(path, 'w', encoding='utf-8').write(s.replace(old, new, 1))
    print('PATCHED', path)

GAME_MENU = '    <a href="/game">\U0001F3AE Know Your Rights (game)</a>'
rep('index.html', GAME_MENU, GAME_MENU + '\n    <a href="/master">\U0001F5C2\uFE0F My Creation</a>')

FOOT = '\u00B7 <a href="/game">Know Your Rights game</a><br />'
rep('index.html', FOOT, '\u00B7 <a href="/game">Know Your Rights game</a> \u00B7 <a href="/master">My Creation</a><br />')

GAME_SIDE = '          <a href="/game">\U0001F3AE Know Your Rights (game)</a>'
rep('app.html', GAME_SIDE, GAME_SIDE + '\n          <a href="/master">\U0001F5C2\uFE0F My Creation</a>')

print('DONE')
