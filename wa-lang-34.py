#!/usr/bin/env python3
# wa-lang-34.py - BOT_DISCLOSURE aur ATTACHMENT_REPLY English single-language (regex - robust)
import re, sys

PATH = "functions/_lib/wa.js"
src = open(PATH, encoding="utf-8").read()

NEW_D = '''export const BOT_DISCLOSURE =
  "🤖 This is an automated legal-information assistant (LegalWithDev).\\n\\n";'''

NEW_A = '''export const ATTACHMENT_REPLY =
  "I can only understand TEXT messages for now - please type your question.";'''

out, n = re.subn(r"export const BOT_DISCLOSURE =.*?;", lambda m: NEW_D, src, count=1, flags=re.S)
if n != 1:
    print("FAIL: BOT_DISCLOSURE not found")
    sys.exit(1)
src = out

out, n = re.subn(r"export const ATTACHMENT_REPLY =.*?;", lambda m: NEW_A, src, count=1, flags=re.S)
if n != 1:
    print("FAIL: ATTACHMENT_REPLY not found")
    sys.exit(1)
src = out

print("OK: disclosure english")
print("OK: attachment english")
open(PATH, "w", encoding="utf-8").write(src)
print("WA PATCHES 3-4 APPLIED")
