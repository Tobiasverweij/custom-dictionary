import json
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import TypedDict

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from romaji_to_kana import romaji_to_kana

console = Console()

### ======== Paths =========== ###
DATA_DIR = Path.home() / "Library" / "Application Support" / "custom-dictionary"
DATA_DIR.mkdir(parents=True, exist_ok=True)
SOURCE = DATA_DIR / "jmdict-eng.json"
RELEASES_API = "https://api.github.com/repos/scriptin/jmdict-simplified/releases/latest"

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


def download_source() -> None:
    print("Downloading JMdict (first run only)...")
    request = urllib.request.Request(RELEASES_API, headers={"User-Agent": "custom-dictionary"})
    with urllib.request.urlopen(request) as response:
        release = json.load(response)

    asset = next(
        a for a in release["assets"]
        if a["name"].startswith("jmdict-eng-") and "common" not in a["name"] and a["name"].endswith(".json.zip")
    )
    zip_path = DATA_DIR / asset["name"]
    urllib.request.urlretrieve(asset["browser_download_url"], zip_path)

    with zipfile.ZipFile(zip_path) as z:
        member = next(n for n in z.namelist() if n.endswith(".json"))
        z.extract(member, DATA_DIR)
    (DATA_DIR / member).replace(SOURCE)
    zip_path.unlink()


def build_index(words: list[Word], key: str) -> defaultdict[str, list[Word]]:
    index: defaultdict[str, list[Word]] = defaultdict(list)
    for word in words:
        seen: set[str] = set()
        for form in word[key]:
            if form["text"] not in seen:
                seen.add(form["text"])
                index[form["text"]].append(word)
    return index


def ensure_data() -> None:
    if (DATA_DIR / "Kana.json").exists() and (DATA_DIR / "Kanji.json").exists():
        return
    if not SOURCE.exists():
        download_source()

    print("Building lookup files (first run only)...")
    with open(SOURCE, encoding="utf-8") as f:
        data = JMDict(json.load(f))

    for key in ("kana", "kanji"):
        index = build_index(data["words"], key)
        with open(DATA_DIR / f"{key.capitalize()}.json", "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False)
    print("Done.")


### =========== main =========
def main():
    ensure_data()

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

        with open(DATA_DIR / f"{kind}.json", encoding="utf-8") as f:
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