#!/usr/bin/env python3
# wa-lang.py - WhatsApp bot ke static messages ab English me (default language).
# 3-language concept permanently removed. (old-strings repo ke EXACT bytes se match karte hain)
import sys

PATH = "functions/_lib/wa.js"
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

rep(
'''export const RATE_LIMIT_REPLY =
  "Aap bahut zyada messages bhej rahe hain. Thoda ruk kar phir try karein (1 ghante me limited sawal allowed hain).\\n" +
  "\u0906\u092a \u092c\u0939\u0941\u0924 \u091c\u093c\u094d\u092f\u093e\u0926\u093e \u0938\u0902\u0926\u0947\u0936 \u092d\u0947\u091c \u0930\u0939\u0947 \u0939\u0948\u0902\u0964 \u0925\u094b\u0921\u093c\u093e \u0930\u0941\u0915\u0915\u0930 \u092b\u093f\u0930 \u092a\u094d\u0930\u092f\u093e\u0938 \u0915\u0930\u0947\u0902\u0964\\n\n" +
  "You are sending too many messages. Please wait a while and try again.\n\n\n" +
  "Yeh free service hai - sab users ke liye available rakhne ke liye limit hai. NALSA: nalsa.gov.in / 15100.";''',
'''export const RATE_LIMIT_REPLY =
  "You are sending too many messages. Please wait a while and try again (only a limited number of questions per hour are allowed).\\n\\n" +
  "This is a free service - the limit keeps it available for everyone. NALSA: nalsa.gov.in / 15100.";''',
"rate limit english",
)


open(PATH, "w", encoding="utf-8").write(src)
print("WA PATCHES 1-2 APPLIED")
