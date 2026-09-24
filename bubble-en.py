#!/usr/bin/env python3
# bubble-en.py - Mascot bubble ke saare default texts English me (default language English).
# Sirf ye fix - aur kuch nahi. Exact-match - na mile to FAIL.
import sys

PATH = "index.html"
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

# 1. Default bubble text (line ~240)
rep(
'<div class="bubble"><span id="bubtxt">Namaste! Main hoon <b>Dev</b> \u2014 aapka legal saathi.</span></div>',
'<div class="bubble"><span id="bubtxt">Namaste! I am <b>Dev</b> \u2014 your legal companion.</span></div>',
"bubble default english",
)

# 2. BUBS rotation array - sab English
rep(
"""var BUBS = [
  'Namaste! Main hoon <b>Dev</b> \u2014 aapka legal saathi.',
  'Kanoon ka koi bhi sawal puchiye \u2014 consumer, rent, family, criminal...',
  '100% free hai, no login, 24/7 \u2014 jab mann kare puchho!',
  'Telegram pe bhi milta hoon: <b>t.me/legalwithdev_bot</b>',
  'Main advocate <b>nahi</b> hoon \u2014 legal <b>information</b> deta hoon, sahi advice ke liye Advocate se milein.'
];""",
"""var BUBS = [
  'Namaste! I am <b>Dev</b> \u2014 your legal companion.',
  'Ask me any legal question \u2014 consumer, rent, family, criminal...',
  '100% free, no login, 24/7 \u2014 ask whenever you want!',
  'Also available on Telegram: <b>t.me/legalwithdev_bot</b>',
  'I am <b>not</b> an advocate \u2014 I give legal <b>information</b>; for advice please consult an Advocate.'
];""",
"bubs array english",
)

open(PATH, "w", encoding="utf-8").write(src)
print("ALL BUBBLE PATCHES APPLIED")
