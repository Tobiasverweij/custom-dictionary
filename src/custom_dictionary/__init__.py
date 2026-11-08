import json
from typing import TypedDict
import typer
from romaji_to_kana import romaji_to_kana
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

### ======== Typeddicts =========== ###
class Gloss(TypedDict):
    lang: str
    text: str

class Sense(TypedDict):
    partOfSpeech: list[str]
    appliesToKanji: list[str]
    appliesToKana: list[str]
    related: list[str]
    antonym: list[str]
    field: list[str]
    dialect: list[str]
    misc: list[str]
    info: list[str]
    languageSource: list[str]
    gloss: list[Gloss]

class Kanji(TypedDict):
    common: bool
    text: str
    tags: list[str]

class Kana(Kanji):
    appliesToKanji: list[str]

class Word(TypedDict):
    id: str
    kanji: list[Kanji]
    kana: list[Kana]
    sense: list[Sense]


class JMDict(TypedDict):
    version: str
    languages: list[str]
    commonOnly: bool
    dictDate: str
    dictRevisions: list[str]
    tags: dict[str, str]
    words: list[Word]

### ======= functions =========
def check_type(ch: str) -> str:
    code = ord(ch)
    if 0x3040 <= code <= 0x309F or 0x30A0 <= code <= 0x30FF:
        return "Kana"
    if 0x4E00 <= code <= 0x9FFF:
        return "Kanji"
    if ch.isascii() and ch.isalpha():
        return "Romaji"

### =========== main =========
def main():
    while True:
        word = input("> ").strip()
        if not word:
            break

        kind = check_type(word[0])
        if kind is None:
            print("Unknown input")
            continue
        if kind == "Romaji":
            word = romaji_to_kana(word)
            kind = "Kana"

        with open(f"/Users/tobiasverweij/Developer/custom-dictionary/src/custom_dictionary/{kind}.json", encoding="utf-8") as f:
            data = json.load(f)

        entry = data.get(word) or []
        if not entry:
            print("Not found")
            continue

        for item in entry:
            if item["kanji"] and item["kanji"][0]["common"]:
                kanji = ", ".join(k["text"] for k in item["kanji"])
                kana = ", ".join(k["text"] for k in item["kana"])

                body = Text()
                body.append(kanji, style="bold cyan")
                body.append("  ")
                body.append(kana, style="green")
                body.append("\n")
                for i, sense in enumerate(item["sense"], 1):
                    gloss = "; ".join(g["text"] for g in sense["gloss"])
                    body.append(f"\n{i}. ", style="bold yellow")
                    body.append(gloss)

                console.print(Panel(body, border_style="blue"))

                

if __name__ == "__main__":
    typer.run(main)