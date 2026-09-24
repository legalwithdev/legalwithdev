#!/usr/bin/env python3
# claims-trans.py - translations.js: 12 languages me purana 3-language claim ->
# naya rule (question ki bhasha me jawab). f1t/f1d (unused dead keys) permanently delete.
# OLD claim sentence FILE SE KHUD extract hota hai (no manual typing), NEW phrase literal.
import re, sys

PATH = "translations.js"
src = open(PATH, encoding="utf-8").read()

NEW = {
 "hi": "मैं उसी भाषा में जवाब देता हूँ जिसमें आपने सवाल पूछा।",
 "ta": "நீங்கள் கேட்கும் மொழியில் நான் பதிலளிப்பேன்.",
 "te": "మీరు అడిగే భాషలోనే నేను సమాధానం ఇస్తాను.",
 "bn": "আপনি যে ভাষায় প্রশ্ন করেন, সেই ভাষাতেই আমি উত্তর দিই।",
 "mr": "तुम्ही ज्या भाषेत प्रश्न विचारता, त्याच भाषेत मी उत्तर देतो.",
 "gu": "તમે જે ભાષામાં પ્રશ્ન પૂછો, એ જ ભાષામાં હું જવાબ આપું છું.",
 "kn": "ನೀವು ಕೇಳುವ ಭಾಷೆಯಲ್ಲಿಯೇ ನಾನು ಉತ್ತರಿಸುತ್ತೇನೆ.",
 "ml": "നിങ്ങൾ ചോദിക്കുന്ന ഭാഷയിൽ തന്നെ ഞാൻ ഉത്തരം നൽകുന്നു.",
 "pa": "ਮੈਂ ਉਸੇ ਬੋਲੀ ਵਿੱਚ ਜਵਾਬ ਦਿੰਦਾ ਹਾਂ ਜਿਸ ਵਿੱਚ ਤੁਸੀਂ ਸਵਾਲ ਪੁੱਛਦੇ ਹੋ।",
 "or": "ମୁଁ ସେହି ଭାଷାରେ ଉତ୍ତର ଦିଏଁ ଯେଉଁ ଭାଷାରେ ଆପଣ ପ୍ରଶ୍ନ ପଚାରନ୍ତି।",
 "as": "মই সেই ভাষাতে উত্তৰ দিওঁ যিটো ভাষাত আপুনি প্ৰশ্ন সোধে।",
 "ur": "میں اسی زبان میں جواب دیتا ہوں جس میں آپ سوال پوچھتے ہیں۔",
}

TERMS = ["\u0964", "\u0965", ".", "?", "!", "\u06d4"]  # danda, double-danda, dot, Urdu full stop

def fix_lang(src, lang, newph):
    m = re.search(re.escape(lang) + r": \{(.*?)welcome: `(.*?)`", src, re.S)
    if not m:
        print("FAIL: welcome not found for", lang); sys.exit(1)
    w = m.group(2)
    i = w.find(" + ")
    j = w.find(" + ", i + 1) if i >= 0 else -1
    if i < 0 or j < 0:
        print("FAIL: claim (+ +) not found in", lang); sys.exit(1)
    left = -1
    for ch in TERMS:
        p = w.rfind(ch, 0, i)
        if p > left: left = p
    start = left + 1 if left >= 0 else 0
    right = len(w)
    for ch in TERMS:
        p = w.find(ch, j)
        if 0 <= p < right: right = p + 1
    old_claim = w[start:right].strip()
    if not old_claim or " + " not in old_claim:
        print("FAIL: bad claim extraction for", lang); sys.exit(1)
    new_w = w.replace(old_claim, newph, 1)
    if new_w == w:
        print("FAIL: replacement failed for", lang); sys.exit(1)
    print("OK:", lang, "-> claim replaced |", old_claim[:40])
    return src.replace(w, new_w, 1)

for lang, newph in NEW.items():
    src = fix_lang(src, lang, newph)

# f1t/f1d unused dead keys (same line me hote hain) - poori line permanently remove
n1 = len(re.findall(r"^ *f1t: ", src, re.M))
src = re.sub(r"^ *f1t: .*\n", "", src, flags=re.M)
print("OK: f1t+f1d lines removed:", n1)
if n1 != 12 or "f1t:" in src or "f1d:" in src:
    print("FAIL: f1t/f1d cleanup incomplete"); sys.exit(1)

# final check - kisi bhi welcome me "+ Hindi + English" pattern na bache
leftover = re.findall(r"welcome: `[^`]*\+[^`]*\+[^`]*`", src)
if leftover:
    print("FAIL: leftover claims:", len(leftover)); sys.exit(1)

open(PATH, "w", encoding="utf-8").write(src)
print("ALL 12 LANGUAGES FIXED - CLAIMS GONE")
