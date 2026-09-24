#!/usr/bin/env python3
# fix-tg.py - Telegram/Messenger fixes: (A) brain.js fallback se developer README-text hatao,
# (C) /start aur greeting se purana 3-language claim hatao. Exact-match, fail-loud.
import sys

def rep(path, old, new, what):
    src = open(path, encoding="utf-8").read()
    if src.count(old) != 1:
        print("FAIL:", what, "count =", src.count(old)); sys.exit(1)
    open(path, "w", encoding="utf-8").write(src.replace(old, new))
    print("OK:", what)

CLAIM_OLD = '"Answers in your native language + Hindi + English.\\n\\n" +'
CLAIM_NEW = '"I answer in whatever language you ask your question in.\\n\\n" +'
rep("functions/webhook/telegram.js", CLAIM_OLD, CLAIM_NEW, "telegram /start 3-language claim")
rep("functions/webhook/messenger.js", CLAIM_OLD, CLAIM_NEW, "messenger greeting 3-language claim")

FB_OLDH	ÉÉÈ™]\›ˆ
ˆ’IÛH›İİ\™HX›İ]]Û™HY]H^HZ[Z[ˆÛ›İÛYÙHÛİ™\œÈ\ÙH\™X\Î——ˆˆ
Âˆ	İ]\ßW—˜
Âˆ•È[˜X›Hœ™YKY›Ü›H[œİÙ\œÈÛˆS–HYØ[]Y\İ[Û‹ÛÛ›™Xİ[ˆRH[Ù[ˆ
ÂˆŠÙYHH‘PQQKÙXİ[Ûˆ	ĞÛÛ›™Xİ[™È[ˆRHœ˜Z[‰ÊK——ˆˆ
ÂˆTĞÓRSQT‚ˆ
NÉÉÉÂ‘—Ó‘UÈH	ÉÉÈ™]\›ˆ
ˆ’IÛHÛÜœKHÛİ[‰İ[œİÙ\ˆ]Û™H\İ›İÈHX\ÙHHYØZ[ˆ[ˆH[ÛY[——ˆˆ
Âˆ“^HZ[Z[ˆ]ZXÚÈ[œİÙ\œÈÛİ™\ˆ\ÙHÛÛ[[ÛˆÜXÜÎ——ˆˆ
Âˆ	İ]\ßW—˜
Âˆ–[İHØ[ˆ[ÛÈH™\˜\Ú[™ÈÚ]Ù^]ÛÜ™ÈZÙH	Ù\ÜÚ]	Ë	ØÚ\]YIË	Ñ’T‰Ë	Ô•IË	ÜØØ[IÈÜˆ	ÜØ[\IË——ˆˆ
ÂˆTĞÓRSQT‚ˆ
NÉÉÉÂœ™\
™[˜İ[ÛœË×ÛX‹Øœ˜Z[‹šœÈ‹—ÓÓ—Ó‘UË˜œ˜Z[‹šœÈ˜[˜XÚÈY\ÜØYÙH
]ˆ^İ]
HŠB‚œš[
SÈ’STÈUÒQŠB