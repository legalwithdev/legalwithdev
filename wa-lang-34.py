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
'''export const BOT_DISCLOSURE =
  "\U0001F916 Ye ek automated legal-information assistant hai (LegalWithDev).\\n" +
  "\U0001F916 \u092f\u0939 \u090f\u0915 \u0938\u094d\u0935\u091a\u093e\u0932\u093f\u0924 \u0915\u093e\u0928\u0942\u0928\u0940 \u091c\u093e\u0928\u0915\u093e\u0930\u0940 \u0938\u0939\u093e\u092f\u0915 \u0939\u0948 (LegalWithDev)\u0964\\n" +
  "\U0001F916 This is an automated legal-information assistant (LegalWithDev).\\n\\n";''',
'''export const BOT_DISCLOSURE =
  "\U0001F916 This is an automated legal-information assistant (LegalWithDev).\\n\\n";''',
"disclosure english",
)

rep(
'''export const ATTACHMENT_REPLY =
  "Main abhi sirf TEXT messages samajh sakta hoon - apna sawal likh kar bhejein.\\n" +
  "\u092e\u0948\u0902 \u0905\u092d\u0940 \u0915\u0947\u0935\u0932 \u091f\u0947\u0915\u094d\u0938\u094d\u091f \u0938\u0902\u0926\u0947\u0936 \u0938\u092e\u091d \u0938\u0915\u0924\u093e \u0939\u942\u0901 - \u0905\u092a\u0928a\u093e \u092a\u094d\u0930\u0936\u094d\u0928 \u0932\u093f\u0916\u0915\u0930 \u092d\u0947\u091c\u0947\u0902\u0964\\n" +
  "I can only understand TEXT messages for now - please type your question";''',
'''export const ATTACHMENT_REPLY =
  "I can only understand TEXT messages for now - please type your question.";''',
"attachment english",
)


open(PATH, "w", encoding="utf-8").write(src)
print("WA PATCHES 3-4 APPLIED")
