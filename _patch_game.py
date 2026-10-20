#!/usr/bin/env python3
# Add the "Know Your Rights" game link to the menu (index) and sidebar (app).
import sys

def rep(path, old, new):
    s = open(path, encoding='utf-8').read()
    if new in s:
        print('SKIP already done:', path); return
    if old not in s:
        print('WARN anchor not found in', path, '->', old[:50]); sys.exit(1)
    open(path, 'w', encoding='utf-8').write(s.replace(old, new, 1))
    print('PATCHED', path)

# index.html: menu drawer link (after Shop)
rep('index.html',
    '    <a href="/shop">\U0001F6CD\uFE0F Shop</a>',
    '    <a href="/shop">\U0001F6CD\uFE0F Shop</a>\n    <a href="/game">\U0001F3AE Know Your Rights (game)</a>')

# index.html: footer link
rep('index.html',
    '\u00B7 <a href="/shop">Shop</a> \u00B7 <a href="/about">About</a><br />',
    '\u00B7 <a href="/shop">Shop</a> \u00B7 <a href="/about">About</a> \u00B7 <a href="/game">Know Your Rights game</a><br />')

# app.html: sidebar link
rep('app.html',
    '          <a href="/shop">\U0001F6CD\uFE0F Shop \u2014 Legal Books & Merch</a>',
    '          <a href="/shop">\U0001F6CD\uFE0F Shop \u2014 Legal Books & Merch</a>\n          <a href="/game">\U0001F3AE Know Your Rights (game)</a>')

print('DONE')
