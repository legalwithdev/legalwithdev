#!/usr/bin/env python3
# en-shop.py - shop.html: poora Hinglish -> English. Exact-match, fail-loud.
import sys

def rep(path, old, new, what, expect=1):
    src = open(path, encoding="utf-8").read()
    n = src.count(old)
    if n != expect:
        print("FAIL:", what, "count =", n); sys.exit(1)
    open(path, "w", encoding="utf-8").write(src.replace(old, new))
    print("OK:", what)

F = "shop.html"
rep(F, "LegalWithDev Shop \u2014 Bharat ke best legal books, bare acts, LLB study material aur legal merchandise. Constitution, Nyaya Sanhita, CLAT books, advocate t-shirts aur bahut kuch.",
       "LegalWithDev Shop \u2014 India's best legal books, bare acts, LLB study material and legal merchandise. Constitution, Nyaya Sanhita, CLAT books, advocate t-shirts and more.",
       "meta description")
rep(F, "Law Students & Law Lovers ke liye", "For Law Students & Law Lovers", "hero part 1")
rep(F, "Legal books, bare acts, LLB study material aur legal merchandise \u2014 sab kuch ek jagah, curated with love for Bharat ke future lawyers. \U0001f1ee\U0001f1f3",
       "Legal books, bare acts, LLB study material and legal merchandise \u2014 everything in one place, curated with love for Bharat's future lawyers. \U0001f1ee\U0001f1f3",
       "hero desc")
rep(F, "Yeh links Amazon.in ke hain \u2014 purchase tum directly Amazon se karte ho (payment, delivery, warranty sab Amazon ka). Kisi product pe \"dekhein\" dabane se humein kuch commission mil sakta hai, bina tumhare kisi extra kharch ke. LegalWithDev kuch bhi bechta ya deliver nahi karta.",
       "These are Amazon.in links \u2014 you purchase directly from Amazon (payment, delivery, warranty \u2014 all handled by Amazon). If you click \"View on Amazon\" we may earn a small commission, at no extra cost to you. LegalWithDev does not sell or deliver anything.",
       "affiliate disclosure")
rep(F, "India ke core kanoon \u2014 har law student aur practitioner ke liye must-have",
       "India's core laws \u2014 a must-have for every law student and practitioner",
       "section 1 sub")
rep(F, "Bharat ki soul \u2014 poori Constitution, latest amendments ke saath. Har Indian ke liye must-read.",
       "The soul of Bharat \u2014 the complete Constitution with the latest amendments. A must-read for every Indian.",
       "constitution desc")
rep(F, "Naya IPC 1860 replacement \u2014 India ka naya criminal code. LLB exams ke liye zaroori.",
       "The new replacement for the IPC 1860 \u2014 India's new criminal code. Essential for LLB exams.",
       "BNS desc")
rep(F, "Nayi CrPC \u2014 criminal procedure ka naya framework, procedural law ke liye essential.",
       "The new CrPC \u2014 a new framework for criminal procedure, essential for procedural law.",
       "BNSS desc")
rep(F, "Nayi Evidence Act \u2014 evidence law ka modern avatar, court practice ke liye important",
       "The new Evidence Act \u2014 a modern take on the law of evidence, important for court practice.",
       "BSA desc")
rep(F, "Constitution samajhne ki classic book \u2014 judiciary exams aur deep understanding ke liye.",
       "The classic book for understanding the Constitution \u2014 for judiciary exams and deep understanding.",
       "DD Basu desc")
rep(F, "Polity ki sabse popular book \u2014 UPSC, state exams aur law students ke favourite.",
       "The most popular book on Indian polity \u2014 a favourite for UPSC, state exams and law students.",
       "Laxmikanth desc")
rep(F, "Contracts ka foundation law \u2014 agreement, consideration, breach sab kuch.",
       "The foundational law of contracts \u2014 agreements, consideration, breach and more.",
       "Contract Act desc")
rep(F, "Exams ki taiyari, previous papers aur reference books",
       "Exam preparation, previous papers and reference books",
       "section 2 sub")
rep(F, "Semester-wise LLB guides \u2014 har subject ke liye exam-focused material.",
       "Semester-wise LLB guides \u2014 exam-focused material for every subject.",
       "LLB guides desc")
rep(F, "CLAT, AILET aur law entrance exams ki taiyari ke best books & mock tests.",
       "The best books & mock tests for CLAT, AILET and other law entrance exams.",
       "C1\ØÈŠBœ™\
‹”™]š[İ\ÈYX\ˆ]Y\İ[Ûˆ\\œÈ
ÈÛÛ™Y[œİÙ\œÈLŒM^[H]\›ˆØ[XZš™HØH™\İ\šZØKˆ‹ˆ”™]š[İ\ÈYX\ˆ]Y\İ[Ûˆ\\œÈ
ÈÛÛ™Y[œİÙ\œÈLŒMH™\İØ^HÈ[™\œİ[™H^[H]\›‹ˆ‹ˆ”TH\ØÈŠBœ™\
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