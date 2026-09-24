#!/usr/bin/env python3
# en-ui.py - app.html + index.html ke Hinglish strings -> English. Exact-match, fail-loud.
import sys

def rep(path, old, new, what, expect=1):
    src = open(path, encoding="utf-8").read()
    n = src.count(old)
    if n != expect:
        print("FAIL:", what, "count =", n); sys.exit(1)
    open(path, "w", encoding="utf-8").write(src.replace(old, new))
    print("OK:", what)

META_OLD = "LegalWithDev \u2014 Bharat ka apna legal AI assistant. Free legal information in your own language \u2014 jo bhasha me poochho, usi me jawab. Website aur Telegram pe live \u2014 WhatsApp coming soon."
META_NEW = "LegalWithDev \u2014 India's own legal AI assistant. Free legal information in your own language \u2014 ask in any language, get the answer in that language. Live on Website and Telegram \u2014 WhatsApp coming soon."

A = "app.html"
rep(A, META_OLD, META_NEW, "app meta")
rep(A, "Bharat ka Legal AI Assistant \u2014 apni bhasha me",
       "India's Legal AI Assistant \u2014 in your language",
       "app ssub")
rep(A, "Namaste! Main LegalWithDev hoon \U0001f64f",
       "Namaste! I am LegalWithDev \U0001f64f",
       "app welcome title")
rep(A, "Apna koi bhi legal sawal poochhiye \u2014 consumer rights, rent, family, criminal, student ya business law. Main usi bhasha me jawab deta hoon jisme aapne sawaal poocha.",
       "Ask any legal question \u2014 consumer rights, rent, family, criminal, student or business law. I answer in the same language you ask your question in.",
       "app welcome sub")
rep(A, "placeholder=\"Apna legal sawal poochhiye\u2026\"",
       "placeholder=\"Ask your legal question\u2026\"",
       "app placeholder")
rep(A, "\U0001f9e0 Sawal samaj  raha hoon\u2026", "\U0001f9e0 Understanding your question\u2026", "app typing 1")
rep(A, "\U0001f4da Legal knowledge base check kar raha hoon\u2026", "\U0001f4da Checking the legal knowledge base\u2026", "app typing 2")
rep(A, "\u2696\ufe0f Relevant kanoon aur sections dhundh raha hoon\u2026", "\u2696\ufe0f Finding relevant laws and sections\u2026", "app typing 3")
rep(A, "\U0001f3db\ufe0f Sarkari helplines verify kar raha hoon\u2026", "\U0001f3db\ufe0f Verifying government helplines\u2026", "app typing 4")
rep(A, "\u270d\ufe0f Aapki bhasha me jawab likh raha hoon\u2026", "\u270d\ufe0f Writing your answer\u2026", "app typing 5")
rep(A, "LegalWithDev kaam kar raha hai", "LegalWithDev is working", "app running label")
rep(A, " \u2014 ab main isi bhasha me jawab dunga!", " \u2014 I will now answer in this language!", "app lang switch")

OG_OLD = "Free legal information in your own language \u2014 answers in whatever language you ask. Consumer, rent, family, criminal, student ya business law \u2014 24/7, bina login."
OG_NEW = "Free legal information in your own language \u2014 answers in whatever language you ask. Consumer, rent, family, criminal, student or business law \u2014 24/7, no login."
rep(A, OG_OLD, OG_NEW, "app og:description")

I = "index.html"
rep(I, META_OLD, META_NEW, "index meta")
rep(I, OG_OLD, OG_NEW, "index og:description")
rep(I, "// AI kaam kar raha hai - user ko dikhta rahe (engagement)",
       "// AI is working - keep it visible to the user (engagement)",
       "index comment")
rep(I, "Sawal samaj  raha hoon...", "Understanding your question...", "index typing 1")
rep(I, "Kanoon aur sections check kar raha hoon...", "Checking laws and sections...", "index typing 2")
rep(I, "Aapke case ke hisaab se jawab bana raha hoon...", "Preparing an answer for your situation...", "index typing 3")
rep(I, "Thodi gehraai me verify kar raha hoon...", "Verifying in a little more depth...", "index typing 4")
rep(I, "Jawab polish kar raha hoon, bas aa gaya...", "Polishing the answer, almost ready...", "index typing 5")
print("APP + INDEX DONE")
