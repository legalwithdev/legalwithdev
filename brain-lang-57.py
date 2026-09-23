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

# 5. buildMessages: site-language forcing POORI tarah hatao (chat = sawaal ki bhasha)
rep(
"""  let langNote = "";
  const lang = String(language || "").toLowerCase();
  if (language && lang !== "auto" && lang !== "english") {
    if (lang === "hindi") {
      langNote =
        "\\n\\nWEBSITE LANGUAGE SELECTION: the user picked HINDI from the language menu. " +
        "Answer with only TWO sections: (1) \u0939\u093f\u0902\u0926\u0940 \u092e\u0947\u0902 (Hindi, Devanagari), (2) In English, " +
        "then the engagement question and duty footer as usual.";
    } else {
      langNote =
        `\\n\\nWEBSITE LANGUAGE SELECTION: the user picked ${language} from the language menu. ` +
        `Section (1) must be written in ${language} (its native script), with the heading ` +
        "in that language - regardless of which language the user typed in. " +
        "Then continue with (2) \u0939\u093f\u0902\u0926\u0940 \u092e\u0947\u0902 and (3) In English as usual.";
    }
  } else if (language && lang === "english") {
    langNote =
      "\\n\\nWEBSITE LANGUAGE SELECTION: the user picked ENGLISH. " +
      "Answer with only TWO sections: (1) In English, (2) \u0939\u093f\u0902\u0926\u0940 \u092e\u0947\u0902, " +
      "then the engagement question and duty footer as usual.";
  }""",
"""  // Naya rule: chat ki bhasha = user ke SAWAAL ki bhasha (site language se koi lena-dena nahi)
  const langNote = "";""",
"langNote removed",
)

# 6. INJECTION_REPLY: English only
rep(
"""const INJECTION_REPLY =
  "Main LegalWithDev hoon - ek legal information assistant. Main apne internal setup ke baare me nahi baat karta.\\n" +
  "\u092e\u0948\u0902 LegalWithDev \u0939\u0942\u0901 - \u0915\u093e\u0928\u0942\u0928\u0940 \u091c\u093e\u0928\u0915\u093e\u0930\u0940 \u0938\u0939\u093e\u092f\u0915\u0964 \u092e\u0948\u0902 \u0905\u092a\u0928\u0940 \u0906\u0902\u0924\u0930\u093f\u0915 \u0938\u0947\u091f\u093f\u0902\u0917\u094d\u0938 \u0915\u0947 \u092c\u093e\u0930\u0947 \u092e\u0947\u0902 \u0928\u0939\u0940\u0902 \u092c\u093e\u0924 \u0915\u0930\u0924\u093e\u0964\\n" +
  "I am LegalWithDev - a legal information assistant. I do not discuss my internal setup.\\n\\n" +
  "Aap koi legal sawal poochhiye - consumer, rent, family, criminal, student ya business law - main zaroor madad karunga!\\n" +
  "Kanooni salah ke liye qualified Advocate/Lawyer se milein. NALSA: nalsa.gov.in / 15100.";""",
"""const INJECTION_REPLY =
  "I am LegalWithDev - a legal information assistant. I do not discuss my internal setup.\\n\\n" +
  "Please ask me a legal question - consumer, rent, family, criminal, student or business law - I will be glad to help!\\n" +
  "For legal advice please consult a qualified Advocate/Lawyer. NALSA: nalsa.gov.in / 15100.";""",
"injection reply english",
)

# 7. Greeting: English only + naya tip
rep(
"""        return (
          "Namaste!\\n\\n" +
          "I am LegalWithDev, your Indian legal information assistant.\\n" +
          "\u092e\u0948\u0902 \u0939\u0942\u0901 LegalWithDev \u2014 \u0906\u092a\u0915\u093e \u092d\u093e\u0930\u0924\u0940\u092f \u0915\u093e\u0928\u0942\u0928\u0940 \u0938\u0939\u093e\u092f\u0915\u0964\\n\\n" +
          "You can ask me about: consumer rights, tenant/rent issues, divorce & maintenance, " +
          "salary/employer disputes, FIR & police matters, cheque bounce, RTI, property purchase, " +
          "online fraud (UPI scams), and free legal aid.\\n\\n" +
          "Tip: once AI mode is switched on, I answer in your own language, plus Hindi and English.\\n\\n" +
          DISCLAIMER
        );""",
"""        return (
          "Namaste! I am LegalWithDev, your Indian legal information assistant.\\n\\n" +
          "You can ask me about: consumer rights, tenant/rent issues, divorce & maintenance, " +
          "salary/employer disputes, FIR & police matters, cheque bounce, RTI, property purchase, " +
          "online fraud (UPI scams), and free legal aid.\\n\\n" +
          "Tip: I answer in whatever language you ask your question in.\\n\\n" +
          DISCLAIMER
        );""",
"greeting english",
)

open(PATH, "w", encoding="utf-8").write(src)
print("BRAIN PATCHES 5-7 APPLIED")
