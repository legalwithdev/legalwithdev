#!/usr/bin/env python3
# en-about.py - about.html: poora Hinglish -> English. Exact-match, fail-loud.
import sys

def rep(path, old, new, what, expect=1):
    src = open(path, encoding="utf-8").read()
    n = src.count(old)
    if n != expect:
        print("FAIL:", what, "count =", n); sys.exit(1)
    open(path, "w", encoding="utf-8").write(src.replace(old, new))
    print("OK:", what)

F = "about.html"
rep(F, "Kyun LegalWithDev? Kanoon sabki bhasha me hona chahiye \u2014 free legal AI assistant for Bharat, 24/7, bina login.",
       "Why LegalWithDev? The law should be in everyone's language \u2014 a free legal AI assistant for India, 24/7, no login.",
       "meta description")
rep(F, "Kyun LegalWithDev? \u2014 Free Legal AI Assistant for Bharat",
       "Why LegalWithDev? \u2014 Free Legal AI Assistant for India",
       "title")
rep(F, "Online \u00b7 Answers in your own language \u2014 jo bhasha me poochho, usi me jawab",
       "Online \u00b7 Answers in your own language \u2014 ask in any language",
       "status sub")
rep(F, "Bharat ka apna <span class=\"grad\">Legal AI Assistant</span>",
       "India's own <span class=\"grad\">Legal AI Assistant</span>",
       "hero h2")
rep(F, "Kanooni sawaal poochho \u2014 apni bhasha me. Consumer, rent, family, criminal, student ya business law \u2014 free, 24/7, bina login.",
       "Ask your legal questions \u2014 in your own language. Consumer, rent, family, criminal, student or business law \u2014 free, 24/7, no login.",
       "hero tagline")
rep(F, "\u2696\ufe0f Chat shuru karo \u2014 FREE",
       "\u2696\ufe0f Start chatting \u2014 FREE",
       "cta")
rep(F, "<h2 class=\"section-title\">Kyun LegalWithDev?</h2>",
       "<h2 class=\"section-title\">Why LegalWithDev?</h2>",
       "section title")
rep(F, "Ek simple idea: kanoon sabki bhasha me hona chahiye.",
       "One simple idea: the law should be in everyone's language.",
       "section sub")
rep(F, "<h3>Aapki Bhasha, Aapka Jawab</h3><p>Har jawab usi bhasha me jisme aapne sawaal poocha. Tamil, Telugu, Bengali, Hindi, English \u2014 jaise aap likho, waise hi jawab.</p>",
       "<h3>Your Language, Your Answer</h3><p>Every answer comes in the language you asked your question in. Tamil, Telugu, Bengali, Hindi, English \u2014 write however you like, the answer follows.</p>",
       "card 1")
rep(F, "<h3>Poori Conversation Yaad</h3><p>Follow-up poochho \u2014 \"uske baad kya karu?\" \u2014 bot context samajh ke jawab deta hai.</p>",
       "<h3>Full Conversation Memory</h3><p>Ask follow-ups \u2014 \"what should I do next?\" \u2014 the bot understands the context and answers.</p>",
       "card 2")
rep(F, "<h3>Sarkari Helplines</h3><p>NALSA 15100, Anti-Ragging 1800-180-5522, Consumer 1915 \u2014 verified government sources ke saath.</p>",
       "<h3>Government Helplines</h3><p>NALSA 15100, Anti-Ragging 1800-180-5522, Consumer 1915 \u2014 backed by verified government sources.</p>",
       "card 3")
rep(F, "Chat history server pe store nahi hoti \u2014 sirf aapke browser me. Sensitive personal info share na karne ka clear guidance.",
       "Chat history is never stored on our servers \u2014 it stays in your browser only. Clear guidance to never share sensitive personal info.",
       "card 4")
rep(F, "Bina login, bina paisa. Har citizen ke liye \u2014 kyunki kanooni jaankari adhikar hai, luxury nahi.",
       "No login, no payment. For every citizen \u2014 because legal information is a right, not a luxury.",
       "card 5")
rep(F, "<h3>Duty Ka Reminder</h3><p>Har jawab ke saath Article 51A \u2014 rights ke saath duties bhi. Responsible citizen banna.</p>",
       "<h3>A Reminder of Duties</h3><p>Article 51A with every answer \u2014 duties along with rights. Helping you be a responsible citizen.</p>",
       "card 6")
rep(F, "Namaste! Main hoon Dev \u2014 LegalWithDev ka mascot. Kanoon ki baat aapki bhasha me \u2014 simple, free, 24/7. Sawal poochho, main hazir hoon.",
       "Namaste! I am Dev \u2014 the LegalWithDev mascot. The law, in your own language \u2014 simple, free, 24/7. Ask away, I am here.",
       "founder text")
rep(F, "Abhi poochho \u2014 app kholo",
       "Ask right now \u2014 just open the app",
       "channel small")
rep(F, "\U0001f512 Chat me apna sensitive/personal info (naam, case number, documents) share na karein.",
       "\U0001f512 Do not share sensitive/personal info (name, case numbers, documents) in the chat.",
       "privacy line")
rep(F, "\u26a0\ufe0f LegalWithDev ek AI legal-information assistant hai \u2014 advocate nahi. General information only; qualified Advocate/Lawyer se salah lein.",
       "\u26a0\ufe0f LegalWithDev is an AI legal-information assistant \u2014 not an advocate. General information only; please consult a qualified Advocate/Lawyer.",
       "disclaimer line")
print("ABOUT.HTML DONE")
