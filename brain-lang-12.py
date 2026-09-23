#!/usr/bin/env python3
# brain-lang.py - Naya language rule: chat ki bhasha = user ke SAWAAL ki bhasha.
# 3-language concept PERMANENTLY removed. Default language: English.
# Ye script EXACT string replacements karti hai - agar koi string na mile to FAIL (koi guess nahi).
import sys

PATH = "functions/_lib/brain.js"
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

# 1. Rule 2: 3-language answer format -> single language (question ki bhasha)
rep(
"""2. ANSWER FORMAT - reply in THREE languages, in this order, each with a clear heading:
   (1) "\u0906\u092a\u0915\u0940 \u092d\u093e\u0937\u093e \u092e\u0947\u0902" - EXACTLY the same language and script the user used.
       If they wrote Hinglish (Roman-script Hindi), reply in Hinglish. If Bengali, reply in Bengali.
       NEVER pick a different language than the user's. If you truly cannot tell, use Hindi in Devanagari.
   (2) "\u0939\u093f\u0902\u0926\u0940 \u092e\u0947\u0902" - Hindi in Devanagari script.
   (3) "In English" - simple indian English.
   If the user already wrote in Hindi (Devanagari), give only TWO sections (Hindi, then English).
   Keep EACH language version concise (about 60-90 words).
   ANSWER SKELETON (follow exactly): (1) \u0906\u092a\u0915\u0940 \u092d\u093e\u0937\u093e \u092e\u0947\u0902 section, (2) \u0939\u093f\u0902\u0926\u0940 \u092e\u0947\u0902 section,
   (3) In English section, (4) ONE engagement question line, (5) duty footer lines.
   NEVER end the answer after the English section - items (4) and (5) are required.""",
"""2. ANSWER LANGUAGE - reply in EXACTLY the same language and script the user's question is
   written in - EVERY message, auto-detected. If they wrote Hinglish (Roman-script Hindi),
   reply in Hinglish. If Tamil, reply in Tamil. If English, reply in English.
   NEVER pick a different language than the user's question. If you truly cannot tell, use English.
   Ignore any website/app language setting for the chat language - ONLY the question's own
   language decides. Do NOT add translations or extra language sections: ONE answer, ONE
   language. Keep it concise (about 80-140 words).""",
"rule2 single-language",
)

# 2. VISUAL FORMAT: language headings hatao
rep(
"""- Every language section heading must stand ALONE on its own line, bolded exactly like this:
  **\u0906\u092a\u0915\u0940 \u092d\u093e\u0937\u093e \u092e\u0947\u0902**  /  **\u0939\u093f\u0902\u0926\u0940 \u092e\u0947\u0902**  /  **In English**
  NEVER prefix headings with "(1)" or "(2)" numbers, and NEVER merge a heading into a paragraph -
  the heading is always its own separate line.""",
"""- NO language section headings - there is onle ONE language (the user's question language).
  Do NOT write headings like "In English" or "\u0906\u092a\u0915\u0940 \u092d\u093e\u0937\u093e \u092e\u0947\u0902" - just answer directly in the
  user's question language, no heading line for the language.""",
"visual format headings",
)

open(PATH, "w", encoding="utf-8").write(src)
print("BRAIN PATCHES 1-2 APPLIED")
