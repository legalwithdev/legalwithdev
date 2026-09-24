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
rep(F, "Nayi Evidence Act \u2014 evidence law ka modern avatar, court practice ke liye important.",
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
print("SHOP PART A DONE")
