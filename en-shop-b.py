#!/usr/bin/env python3
# en-shop-b.py - shop part 2 (CLAT se aage)
import sys

def rep(path, old, new, what, expect=1):
    src = open(path, encoding="utf-8").read()
    n = src.count(old)
    if n != expect:
        print("FAIL:", what, "count =", n); sys.exit(1)
    open(path, "w", encoding="utf-8").write(src.replace(old, new))
    print("OK:", what)

F = "shop.html"
rep(F, "CLAT, AILET aur law entrance exams ki taiyari ke best books & mock tests.",
       "The best books & mock tests for CLAT, AILET and other law entrance exams.",
       "CLAT desc")
rep(F, "Previous year question papers + solved answers \u2014 exam pattern samajhne ka best tarika.",
       "Previous year question papers + solved answers \u2014 the best way to understand the exam pattern.",
       "PYQ\ØÈŠBœ™\
‹“YØ[™X\ÛÛš[™ËÙÚXØ[\]YHLŒM[˜[˜ÙH^[\È]\ˆ[Ûİ[™ÈÙH^YH˜XİXÙHX]\šX[ˆ‹ˆ“YØ[™X\ÛÛš[™È[™ÙÚXØ[\]YHLŒM˜XİXÙHX]\šX[›Üˆ[˜[˜ÙH^[\È[™[Ûİ[™Ëˆ‹ˆœ™X\ÛÛš[™È\ØÈŠBœ™\
‹“YØ[\›\ÈÚHXİ[Û˜\HLŒM][ˆX^[\ÈÙHZØ\ˆ[™X[ˆYØ[›ØØX[\HZËˆ‹ˆHXİ[Û˜\HÙˆYØ[\›\ÈLŒMœ›ÛH][ˆX^[\ÈÈ[™X[ˆYØ[›ØØX[\Kˆ‹ˆ™Xİ[Û˜\H\ØÈŠBœ™\
‹“]Ë][YY\Ú\Ë]YÜÈ]\ˆ\ÚÈXØÙ\ÜÛÜšY\È‹ˆ“]Ë][YY\Ú\Ë]YÜÈ[™\ÚÈXØÙ\ÜÛÜšY\È‹ˆœÙXİ[ÛˆÈİXˆŠBœ™\
‹‘[›H]\ˆÛ\ÜŞH]ŞY\‹][YY\Ú\ÈLŒM]ÈİY[ÈÙH^YH\™™XİÛÛYÙHÙX\‹ˆ‹ˆ‘[›H[™Û\ÜŞH]ŞY\‹][YY\Ú\ÈLŒM\™™XİÛÛYÙHÙX\ˆ›Üˆ]ÈİY[Ëˆ‹ˆÚ\È\ØÈŠBœ™\
‹	È“Øš™Xİ[ÛˆHˆ]\ˆ’]\[™ÈˆØ[H]YÜÈLŒMÛİ\ÙH[X™H[›ÛˆÙH^YHÛÙ™™YHÛÛ\[š[Û‹‰Ëˆ	È“Øš™Xİ[ÛˆHˆ[™’]\[™Èˆ]YÜÈLŒMHÛÙ™™YHÛÛ\[š[Ûˆ›ÜˆÛ™È^\È[ˆÛİ\‰Ëˆ›]YÜÈ\ØÈŠBœ™\
‹•X›KÙ\ÚÈÙH^YHYH\İXÙHİ]Y\È]\ˆØØ[\ÈÙˆ\İXÙHLŒMÙ™šXÙHXHİYH›ÛÛHÙH^YKˆ‹ˆ“YH\İXÙHİ]Y\È[™ØØ[\ÈÙˆ\İXÙH›Üˆ[İ\ˆX›HÜˆ\ÚÈLŒM›ÜˆÙ™šXÙHÜˆİYH›ÛÛKˆ‹ˆ™XÛÜˆ\ØÈŠBœ™\
‹“YØ[YËY›ØØ]H›İX›ÛÚÜÈ]\ˆØ\ÙKYš[\Èİ[Hİ][Û™\HLŒM›İ\ÈÙH^YKˆ‹ˆ“YØ[YËY›ØØ]H›İX›ÛÚÜÈ[™Ø\ÙKYš[Hİ[Hİ][Û™\HLŒM›Üˆ[İ\ˆ›İ\Ëˆ‹ˆœYÈ\ØÈŠBœ™\
‹—LŒNLYØ[Ú]]ˆHØ\\È˜[ÈLŒM”‘QHYØ[Ø]Ø[ÛØÚÈ‹ˆ—LŒNL˜XÚÈÈYØ[Ú]]ˆLŒM\ÚÈH”‘QHYØ[]Y\İ[Ûˆ‹ˆ˜˜XÚÈ[šÈŠBœ™\
‹—L˜LY™LˆYØ[Ú]]ˆ›ÙXİÈ™XÚH˜ZHLŒMYZİ\˜]YY™š[X]H[šÜÈZ[ˆ
[X^›Û‹š[ŠKˆ\˜Ú\ÙK^[Y[[]™\HØXˆ[X^›Ûˆ[™HØ\HZKˆ‹ˆ—L˜LY™LˆYØ[Ú]]ˆÙ\È›İÙ[›ÙXİÈLŒM\ÙH\™Hİ\˜]YY™š[X]H[šÜÈ
[X^›Û‹š[ŠKˆ\˜Ú\ÙK^[Y[[™[]™\H\™H[[™YH[X^›Û‹ˆ‹ˆ™›Ûİ\ˆ›İHŠBœ™\
‹[X^›ÛˆHZÚZ[ˆLŒNLˆ‹•šY]ÈÛˆ[X^›ÛˆLŒNLˆ‹˜[X^›ÛˆİH‹^XİLMŠBœš[
”ÒÔ’SÓ‘HŠB