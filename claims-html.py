#!/usr/bin/env python3
# claims-html.py - Unverified/purane claims fix: 3-language claim hatao, WhatsApp Coming Soon.
# index.html + app.html + about.html. Exact-match - na mile to FAIL.
import sys

def rep(path, old, new, what):
    src = open(path, encoding="utf-8").read()
    if old not in src:
        print("FAIL: not found ->", what); sys.exit(1)
    if src.count(old) != 1:
        print("FAIL: not unique ->", what); sys.exit(1)
    open(path, "w", encoding="utf-8").write(src.replace(old, new))
    print("OK:", what)

META_OLD = 'LegalWithDev \u2014 Bharat ka apna legal AI assistant. Free legal information in your native language + Hindi + English. Website, Telegram aur WhatsApp pe.'
META_NEW = 'LegalWithDev \u2014 Bharat ka apna legal AI assistant. Free legal information in your own language \u2014 jo bhasha me poochho, usi me jawab. Website aur Telegram pe live \u2014 WhatsApp coming soon.'
OG_OLD = 'Free legal information in your native language + Hindi + English. Consumer, rent, family, criminal, student ya business law \u2014 24/7, bina login.'
OG_NEW = 'Free legal information in your own language \u2014 answers in whatever language you ask. Consumer, rent, family, criminal, student ya business law \u2014 24/7, bina login.'

for f in ["index.html", "app.html"]:
    rep(f, META_OLD, META_NEW, f + " meta description")
    rep(f, OG_OLD, OG_NEW, f + " og:description")

rep("app.html",
 'Apna koi bhi legal sawal poochhiye \u2014 consumer rights, rent, family, criminal, student ya business law. Main aapki bhasha + \u0939\u093f\u0902\u0926\u0940 + English me jawab deta hoon.',
 'Apna koi bhi legal sawal poochhiye \u2014 consumer rights, rent, family, criminal, student ya business law. Main usi bhasha me jawab deta hoon jisme aapne sawaal poocha.',
 "app.html welcome-sub")

rep("about.html",
 'Online \u00b7 Answers in your native language + \u0939\u093f\u0902\u0926\u0940 + English',
 'Online \u00b7 Answers in your own language \u2014 jo bhasha me poochho, usi me jawab',
 "about.html status sub")

rep("about.html",
 '<h3>3 Bhasha, Ek Jawab</h3><p>Har jawab aapki native language + \u0939\u093f\u0902\u0926\u0940 + English me. Tamil, Telugu, Bengali \u2014 jaise aap likho, waise.</p>',
 '<h3>Aapki Bhasha, Aapka Jawab</h3><p>Har jawab usi bhasha me jisme aapne sawaal poocha. Tamil, Telugu, Bengali, Hindi, English \u2014 jaise aap likho, waise hi jawab.</p>',
 "about.html feature card")

rep("about.html",
 '<div><b>WhatsApp</b><small>Setup jald hi complete</small></div>',
 '<div><b>WhatsApp</b><small>Coming Soon \u2014 setup in progress</small></div>',
 "about.html WhatsApp coming soon")

print("ALL HTML CLAIM PATCHES APPLIED")
