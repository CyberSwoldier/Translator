# Polish (pl) — Translation & Grammar Reference

## Overview
Polish is a West Slavic (Indo-European) language spoken by ~45 million people in Poland. It is highly inflected with 7 grammatical cases, 3 grammatical genders (plus 2 plural sub-genders), complex verb aspect system, and rich consonant clusters. Polish is widely regarded as one of the most grammatically complex languages for English speakers.

---

## 1. REGISTER & TONE (Critical for phishing simulations)

- Polish has a clear, important distinction between formal and informal address.
- **Formal address**: Use **Pan** (Mr/sir, masculine), **Pani** (Ms/ma'am, feminine), **Państwo** (mixed group/couple), or **Panowie** (all-male group), **Panie** (all-female group). These replace "you" in formal contexts and govern verb/adjective gender agreement.
- When gender is unknown: use the **"Proszę" + verb infinitive** structure — this is gender-neutral and appropriate for formal writing: "Proszę kliknąć" (Please click).
- **Informal "ty"**: used among friends, colleagues in informal settings.
- For phishing simulations mimicking institutions: use **Pan/Pani + verb** forms. If gender is unknown, use "Proszę" + infinitive.
- **GENDER AGREEMENT IS MANDATORY**: All verbs (past tense), adjectives, and participles must agree with the gender of the subject. Failure to do so makes the text immediately unnatural.
- Greeting: "Szanowny Panie [Name]," / "Szanowna Pani [Name]," (formal) or "Dzień dobry, [Name]," (standard).
- Closing: "Z poważaniem," (Yours sincerely/formal) or "Z wyrazami szacunku," (With expressions of respect).

---

## 2. NOUNS & GENDER

Polish has **3 singular genders** and **2 plural categories**:
- **Masculine**: further divided into: personal (male people), animate (male animals), inanimate (objects).
- **Feminine**: nouns ending in -a or -ość, -ść etc.
- **Neuter**: typically ending in -o, -e, -ę, -um.
- **Plural masculine personal** (virile): groups containing at least one male person.
- **Plural non-masculine personal**: all others (women, children, animals, objects).

Typical endings (nominative singular):
- Masculine: consonant ending (dom, kot, stół), or -arz, -acz, -ek, -ość (some feminine-looking exceptions).
- Feminine: -a (mama, szkoła), -ość (miłość), -ć (noc), or -ia.
- Neuter: -o (okno), -e (pole), -ę (imię), -um (muzeum).

**NO articles** in Polish.

---

## 3. SEVEN CASES

| Case | Question | Primary Use |
|------|----------|-------------|
| Nominative (mianownik) | kto? co? | Subject |
| Genitive (dopełniacz) | kogo? czego? | Possession, after negation, after numbers 5+ |
| Dative (celownik) | komu? czemu? | Indirect object |
| Accusative (biernik) | kogo? co? | Direct object |
| Instrumental (narzędnik) | kim? czym? | With/by means of, predicate complement |
| Locative (miejscownik) | o kim? o czym? | After certain prepositions (w, na, przy, o, po) |
| Vocative (wołacz) | — | Direct address |

**Critical rule — Negation changes case**: After negation, the direct object shifts from ACCUSATIVE to GENITIVE:
- "Kupiłem samochód." (I bought a car — accusative)
- "Nie kupiłem samochodu." (I didn't buy a car — genitive)

---

## 4. PRONOUNS & FORMAL ADDRESS

- Formal singular: **Pan** (sir/he), **Pani** (ma'am/she) — these behave as 3rd person singular nouns, requiring 3rd person singular verb forms.
- "Proszę Pana/Panią..." = formal request construction.
- When gender unknown: "Proszę" + infinitive avoids gendered forms entirely.
- Past tense verbs AGREE with gender of subject:
  - Masculine: "Pan wysłał" (you [sir] sent)
  - Feminine: "Pani wysłała" (you [ma'am] sent)

---

## 5. VERBS — ASPECT SYSTEM

Every Polish verb comes in **two aspects**:
- **Imperfective** (niedokonany): ongoing, repeated, habitual → "pisać" (to write, ongoing)
- **Perfective** (dokonany): completed, one-time, result → "napisać" (to write, and complete it)

This distinction is fundamental and must be maintained in translation:
- "Please send the email" → perfective "Proszę wysłać" (complete the action).
- "I was writing the email" → imperfective "Pisałem email" (ongoing past).

Present tense: only IMPERFECTIVE verbs exist in present tense.
Future: imperfective → "będę pisać" (I will be writing); perfective → "napiszę" (I will write/complete).

Past tense endings by gender (3rd person singular):
- Masculine: -ł (pisał — he wrote)
- Feminine: -ła (pisała — she wrote)
- Neuter: -ło (pisało)

---

## 6. ADJECTIVES

- Agree in gender, number, and case with the noun.
- Typically precede the noun (exceptions in official/set phrases: "język polski").
- Masculine adjective endings: -y/-i (indefinite), e.g., "duży dom" (big house).
- Feminine: -a, e.g., "duża szkoła".
- Neuter: -e, e.g., "duże okno".
- Comparative: add -szy or -iejszy | Superlative: prefix naj-.

---

## 7. SENTENCE STRUCTURE

- Basic **SVO**, but highly flexible due to case system — word order changes emphasis.
- Subjects are often omitted (pro-drop) as verb endings encode person and number.
- Negation: "nie" before the verb. Object case shifts from accusative to genitive after negation.
- Questions: "czy" + statement creates yes/no question: "Czy wysłałeś email?" (Did you send the email?).

---

## 8. PUNCTUATION & FORMATTING

- **Decimal separator**: comma (2,5). **Thousands separator**: space (1 000) or period (1.000).
- Quotation marks: „Polish style" (bottom opening, top closing) — preferred.
- Long scale numbers: "miliard" = 10^9 (billion in English). NOT "bilion" for 10^9 — false friend.
- Percentages: "50%" (no space before %).
- Capitalisation: Only proper nouns and sentence starts. Days, months, nationalities LOWERCASE: "poniedziałek", "polski".

---

## 9. KEY TRANSLATION PITFALLS

- "Please" → "Proszę" + infinitive (gender-neutral, formal) or restructure.
- "Click here" → "Kliknij tutaj" (informal) or "Proszę kliknąć tutaj" (formal).
- "Your account" → "Pana/Pani konto" (formal) or "twoje konto" (informal).
- "Verify" → "zweryfikuj" (informal) or "Proszę zweryfikować" (formal).
- "Urgent" → "Pilne" or "Ważne".
- "Log in" → "Zaloguj się".
- "Password" → "hasło".
- "Username" → "nazwa użytkownika".
- Negation MUST change object case from accusative to genitive — machine translation often fails this.
- Aspect selection (perfective vs imperfective) is critical for naturalness.
- Gender agreement in all past tenses is mandatory.
- Formal address: using "ty" form in formal contexts is a serious error.

---

## 10. SPECIAL CHARACTERS

Must use: **ą, ć, ę, ł, ń, ó, ś, ź, ż** (and uppercase **Ą, Ć, Ę, Ł, Ń, Ó, Ś, Ź, Ż**). These are all phonemically distinct — omitting them produces misspellings. Note: "ł" is NOT the same as "l" — it sounds like English "w". "ó" sounds like "u". These must never be substituted with unaccented equivalents.
