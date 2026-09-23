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

# 3. Footer: 3-language footer -> single language
rep(
"""Place this footer ONCE, at the very end of the whole reply (after the English section) - not inside each section.
Format: one line in the user's own language, one line in Hindi, one line in English.""",
"""Place this footer ONCE, at the very end of the whole reply, in the SAME language as your answer.""",
"footer single language",
)

# 4. Sensitive-details reminder example -> English
rep(
"""   home address), gently remind them ONCE in one line: "Aap sensitive personal details chat me share
   na karein - sawal aam bhasha me poochhiye." Then answer normally.""",
"""   home address), gently remind them ONCE in one line (in their question's language): "Please
   do not share sensitive personal details in chat - ask in general terms." Then answer normally.""",
"privacy reminder english",
)

open(PATH, "w", encoding="utf-8").write(src)
print("BRAIN PATCHES 3-4 APPLIED")
