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

rep(
'''export const BOT_DISCLOSURE =
  "\ULQLMˆYHZÈ]]ÛX]YYØ[Z[™›Ü›X][Ûˆ\ÜÚ\İ[ZH
YØ[Ú]]ŠK—ˆˆ
Âˆ—LQLMˆLL™—LLÎHLL—LLMHLLÎLMLLÍWLLXWLLÙWLLÌ—LLÙ—LLLLMWLLÙWLLLM—LLLMLLX×LLÙWLLLLMWLLÙWLLÌLMLLÎLLÎWLLÙWLL™—LLMHLLÎWLM
YØ[Ú]]ŠWLMˆˆ
Âˆ—LQLMˆ\È\È[ˆ]]ÛX]YYØ[Z[™›Ü›X][Ûˆ\ÜÚ\İ[
YØ[Ú]]ŠK——ˆÉÉÉË‰ÉÉÙ^ÜÛÛœİ“ÕÑTĞÓÔÕT‘HBˆ—LQLMˆ\È\È[ˆ]]ÛX]YYØ[Z[™›Ü›X][Ûˆ\ÜÚ\İ[
YØ[Ú]]ŠK——ˆÉÉÉËˆ™\ØÛÜİ\™H[™Û\Ú‹ŠB‚œ™\
‰ÉÉÙ^ÜÛÛœİUPÒQS•Ô‘THBˆ“XZ[ˆXšHÚ\™ˆVY\ÜØYÙ\ÈØ[XZšØZİHÛÛˆH\˜HØ]Ø[ZÚØ\ˆšZ™Z[‹—ˆˆ
Âˆ—LL™WLMLLˆLLWLL™LMLLMWLM×LLÍWLLÌˆLNYLM×LLMWLMLLÎLMLLYˆLLÎLL—LL—LM×LLÍˆLLÎL™—LLX×LLÙˆLLÙWLLHLLÎLLMWLLLLÙHLLÎWLM—LLHHLLWLL˜WLLLLÙHLL˜WLMLLÌLLÍ—LMLLLLÌ—LLÙ—LLM—LLMWLLÌLL™LM×LLX×LM×LL—LMˆˆ
Âˆ’HØ[ˆÛ›H[™\œİ[™VY\ÜØYÙ\È›Üˆ›İÈHX\ÙH\H[İ\ˆ]Y\İ[ÛˆÉÉÉË‰ÉÉÙ^ÜÛÛœİUPÒQS•Ô‘THBˆ’HØ[ˆÛ›H[™\œİ[™VY\ÜØYÙ\È›Üˆ›İÈHX\ÙH\H[İ\ˆ]Y\İ[Û‹ˆÉÉÉËˆ˜]XÚY[[™Û\Ú‹ŠB‚›Ü[ŠUÈ‹[˜ÛÙ[™ÏH]‹NŠKÜš]JÜ˜ÊBœš[
SĞHUÒTÈTQQŠB