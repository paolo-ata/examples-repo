import csv
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


INDEX_URL = "https://search.bger.ch/ext/eurospider/live/de/php/clir/http/index_atf.php?year=151&volume=III&lang=de&zoom=&system=clir"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "de-CH,de;q=0.9,en;q=0.6",
}


def fetch_html(session: requests.Session, url: str) -> str:
    r = session.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
    r.raise_for_status()
    # robustes Encoding
    if not r.encoding:
        r.encoding = r.apparent_encoding or "utf-8"
    return r.text


def normalize_ws(s: str) -> str:
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def extract_decision_links(index_html: str, base_url: str) -> list[str]:
    """
    Extrahiert Links zu Einzelentscheiden aus der Index-Seite.
    Typischerweise sind das URLs mit type=show_document & highlight_docid=...
    """
    soup = BeautifulSoup(index_html, "lxml")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        abs_url = urljoin(base_url, href)
        if "type=show_document" in abs_url and "highlight_docid=" in abs_url:
            links.append(abs_url)

    # Deduplizieren (Reihenfolge behalten)
    seen = set()
    out = []
    for u in links:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def parse_regeste(soup: BeautifulSoup) -> str:
    """
    Extrahiert alle Regesten aus der Seite.

    Die HTML-Struktur ist:
    <div id="regeste" lang="de">
      <div class="big bold">Regeste</div>  oder "Regeste a", "Regeste b" etc.
      <div class="paraatf">
        <span class="artref">Art. XY</span>; Titel...
        <div class="paratf">Eigentlicher Text...</div>
      </div>
    </div>

    Bei mehreren Regesten wird "Regeste a:", "Regeste b:" etc. vorangestellt.
    Bei nur einer Regeste wird kein Label verwendet.
    """
    regeste_divs = soup.find_all("div", id="regeste")

    if not regeste_divs:
        return ""

    regesten = []

    for div in regeste_divs:
        # Label extrahieren (z.B. "Regeste" oder "Regeste a")
        label_div = div.find("div", class_="big bold")
        label = label_div.get_text(strip=True) if label_div else ""

        # Inhalt extrahieren aus paraatf
        content_div = div.find("div", class_="paraatf")
        if not content_div:
            continue

        # Text sauber extrahieren (behält Artikel-Referenzen)
        content = content_div.get_text(" ", strip=True)
        content = normalize_ws(content)

        if content:
            regesten.append((label, content))

    if not regesten:
        return ""

    # Bei nur einer Regeste: kein Label
    if len(regesten) == 1:
        return regesten[0][1]

    # Bei mehreren Regesten: mit Label
    parts = []
    for label, content in regesten:
        # Label normalisieren (nbsp entfernen) und Doppelpunkt hinzufügen
        label_clean = label.replace("\u00a0", " ").strip()
        parts.append(f"{label_clean}:\n{content}")

    return "\n\n".join(parts)


def parse_urteilsnummer(soup: BeautifulSoup) -> str:
    full_text = soup.get_text("\n", strip=True)
    full_text = normalize_ws(full_text)

    m = re.search(r"\b(?:BGE\s*)?(1[0-9]{2})\s+([IVX]+)\s+([0-9]{1,4})\b", full_text)
    if not m:
        return ""
    return f"{m.group(1)} {m.group(2)} {m.group(3)}"


def main():
    out_csv = "bge_151_iii_regesten.csv"

    with requests.Session() as session:
        index_html = fetch_html(session, INDEX_URL)
        decision_links = extract_decision_links(index_html, INDEX_URL)

        if not decision_links:
            raise RuntimeError(
                "Keine Entscheid-Links im Index gefunden. Dann müssen wir die Link-Erkennung anpassen."
            )

        rows = []
        for i, url in enumerate(decision_links, start=1):
            time.sleep(0.5)  # höflich: nicht zu schnell
            html = fetch_html(session, url)
            soup = BeautifulSoup(html, "lxml")

            urteilsnummer = parse_urteilsnummer(soup)
            regeste = parse_regeste(soup)

            if not urteilsnummer:
                print(f"[WARN] Urteilsnummer nicht gefunden: {url}")
            if not regeste:
                print(f"[WARN] Regeste nicht gefunden: {url}")

            rows.append((urteilsnummer, regeste))
            print(f"[{i}/{len(decision_links)}] {urteilsnummer} extrahiert")

    # CSV schreiben (DE/CH-Excel: Semikolon ist meist angenehm)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["urteilsnummer", "regeste"])
        writer.writerows(rows)

    print(f"Fertig: {out_csv}")


if __name__ == "__main__":
    main()