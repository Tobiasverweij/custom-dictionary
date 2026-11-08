TABLE = {
    # Vowels
    "a": "あ", "i": "い", "u": "う", "e": "え", "o": "お",

    # Seion (clear sounds)
    "ka": "か", "ki": "き", "ku": "く", "ke": "け", "ko": "こ",
    "sa": "さ", "shi": "し", "su": "す", "se": "せ", "so": "そ",
    "ta": "た", "chi": "ち", "tsu": "つ", "te": "て", "to": "と",
    "na": "な", "ni": "に", "nu": "ぬ", "ne": "ね", "no": "の",
    "ha": "は", "hi": "ひ", "fu": "ふ", "he": "へ", "ho": "ほ",
    "ma": "ま", "mi": "み", "mu": "む", "me": "め", "mo": "も",
    "ya": "や", "yu": "ゆ", "yo": "よ",
    "ra": "ら", "ri": "り", "ru": "る", "re": "れ", "ro": "ろ",
    "wa": "わ", "wo": "を", "n": "ん",

    # Dakuon (voiced sounds)
    "ga": "が", "gi": "ぎ", "gu": "ぐ", "ge": "げ", "go": "ご",
    "za": "ざ", "ji": "じ", "zu": "ず", "ze": "ぜ", "zo": "ぞ",
    "da": "だ", "di": "ぢ", "du": "づ", "de": "で", "do": "ど",
    "ba": "ば", "bi": "び", "bu": "ぶ", "be": "べ", "bo": "ぼ",

    # Handakuon (half-voiced sounds)
    "pa": "ぱ", "pi": "ぴ", "pu": "ぷ", "pe": "ぺ", "po": "ぽ",

    # Combinations (yoon)
    "kya": "きゃ", "kyu": "きゅ", "kyo": "きょ",
    "gya": "ぎゃ", "gyu": "ぎゅ", "gyo": "ぎょ",
    "sha": "しゃ", "shu": "しゅ", "sho": "しょ",
    "ja": "じゃ", "ju": "じゅ", "jo": "じょ",
    "jya": "じゃ", "jyu": "じゅ", "jyo": "じょ",
    "cha": "ちゃ", "chu": "ちゅ", "cho": "ちょ",
    "nya": "にゃ", "nyu": "にゅ", "nyo": "にょ",
    "hya": "ひゃ", "hyu": "ひゅ", "hyo": "ひょ",
    "bya": "びゃ", "byu": "びゅ", "byo": "びょ",
    "pya": "ぴゃ", "pyu": "ぴゅ", "pyo": "ぴょ",
    "mya": "みゃ", "myu": "みゅ", "myo": "みょ",
    "rya": "りゃ", "ryu": "りゅ", "ryo": "りょ",

    # Alternative spellings
    "si": "し", "ti": "ち", "tu": "つ", "hu": "ふ",
    "zi": "じ", "cu": "く",
    "sya": "しゃ", "syu": "しゅ", "syo": "しょ",
    "zya": "じゃ", "zyu": "じゅ", "zyo": "じょ",
    "dya": "ぢゃ", "dyu": "ぢゅ", "dyo": "ぢょ",
    "tya": "ちゃ", "tyu": "ちゅ", "tyo": "ちょ",
}

VOWELS = set("aiueo")


def romaji_to_kana(word: str) -> str:
    text = word.lower()
    out = []
    i = 0
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""

        # Sokuon: a doubled consonant (not n or a vowel) becomes small っ
        if nxt == ch and ch.isalpha() and ch not in "aiueon":
            out.append("っ")
            i += 1
            continue

        # ん: "n" before a consonant or at the end, and "nn" before a consonant or the end
        if ch == "n" and nxt == "n" and (i + 2 == len(text) or text[i + 2] not in VOWELS | {"y"}):
            out.append("ん")
            i += 2
            continue
        if ch == "n" and (nxt == "" or nxt not in VOWELS | {"y", "n"}):
            out.append("ん")
            i += 1
            continue

        # Longest match first: 3 letters, then 2, then 1
        for size in (3, 2, 1):
            chunk = text[i:i + size]
            if chunk in TABLE:
                out.append(TABLE[chunk])
                i += size
                break
        else:
            out.append(ch)  # unknown character, keep it
            i += 1

    return "".join(out)


if __name__ == "__main__":
    for test in ["taberu", "shinjuku", "nihongo", "kitte", "gakkou", "tokyo", "kanji", "jyoushi"]:
        print(test, "->", romaji_to_kana(test))
