#!/usr/bin/env python3
# wa-lang-12.py - RATE_LIMIT_REPLY ko English single-language se replace (regex - robust)
import re, sys

PATH = "functions/_lib/wa.js"
src = open(PATH, encoding="utf-8").read()

NEW = '''export const RATE_LIMIT_REPLY =
  "You are sending too many messages. Please wait a while and try again (only a limited number of questions per hour are allowed).\\n\\n" +
  "This is a free service - the limit keeps it available for everyone. NALSA: nalsa.gov.in / 15100.";'''

out, n = re.subn(r"export const RATE_LIMIT_REPLY =.*?;", lambda m: NEW, src, count=1, flags=re.S)
if n != 1:
    print("FAIL: RATE_LIMIT_REPLY not found")
    sys.exit(1)
print("OK: rate limit english")
open(PATH, "w", encoding="utf-8").write(out)
print("WA PATCHES 1-2 APPLIED")
