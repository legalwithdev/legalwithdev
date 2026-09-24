#!/usr/bin/env python3
# fix-tg.py - Telegram/Messenger fixes: (A) brain.js fallback se developer README-text hatao,
# (C) /start aur greeting se purana 3-language claim hatao. Exact-match, fail-loud.
import sys

def rep(path, old, new, what):
    src = open(path, encoding="utf-8").read()
    if src.count(old) != 1:
        print("FAIL:", what, "count =", src.count(old)); sys.exit(1)
    open(path, "w", encoding="utf-8").write(src.replace(old, new))
    print("OK:", what)

CLAIM_OLD
