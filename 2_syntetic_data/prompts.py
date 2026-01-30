from __future__ import annotations

import json
from typing import Any

SYSTEM_PROMPTS = {
    "DE": (
        "Du bist ein erfahrener Experte für Schweizer Versicherungs- und Baurecht, "
        "spezialisiert auf Haftpflichtfälle im Bauwesen (Bauhaftpflicht, Berufshaftpflicht, "
        "Garantien/Bürgschaften). Du erstellst realistische, synthetische Dokumente für "
        "Versicherungsdossiers.\n\n"
        "Strikte Regeln:\n"
        "- Verwende NUR Fakten aus der bereitgestellten Case-Bible. Erfinde KEINE neuen "
        "Parteien, Orte, Beträge oder Ereignisse.\n"
        "- Schweizer Datumsformat: TT.MM.JJJJ (z.B. 15.03.2024)\n"
        "- Beträge in CHF mit Apostroph als Tausendertrennzeichen (z.B. CHF 95'000.00)\n"
        "- Verwende die korrekten Normen aus der Case-Bible (SIA, OR, ZPO etc.)\n"
        "- Halte die Sprache strikt auf Deutsch\n"
        "- Schreibe in professionellem, branchenüblichem Stil\n"
        "- Simuliere einen realistischen Briefkopf/Header wo angemessen"
    ),
    "FR": (
        "Vous êtes un expert expérimenté en droit suisse des assurances et de la construction, "
        "spécialisé dans les cas de responsabilité civile dans le domaine de la construction "
        "(RC entreprise, RC professionnelle, garanties/cautionnements). Vous créez des documents "
        "synthétiques réalistes pour des dossiers d'assurance.\n\n"
        "Règles strictes :\n"
        "- Utilisez UNIQUEMENT les faits fournis dans le Case-Bible. N'inventez PAS de nouvelles "
        "parties, lieux, montants ou événements.\n"
        "- Format de date suisse : JJ.MM.AAAA (p. ex. 15.03.2024)\n"
        "- Montants en CHF avec apostrophe comme séparateur de milliers (p. ex. CHF 95'000.00)\n"
        "- Utilisez les normes correctes du Case-Bible (SIA, CO, CPC etc.)\n"
        "- Maintenez la langue strictement en français\n"
        "- Rédigez dans un style professionnel conforme aux usages de la branche\n"
        "- Simulez un en-tête réaliste lorsque c'est approprié"
    ),
}

DOCUMENT_TEMPLATES: dict[str, dict[str, Any]] = {
    "schadenanmeldung": {
        "verfasser": "VN oder Anwalt VN",
        "empfaenger": "Haftpflichtversicherung",
        "ton": "formal_brief",
        "woerter": (300, 500),
        "struktur": [
            "Betreff/Referenz",
            "Sachverhaltsdarstellung",
            "Schadenbeschreibung",
            "Forderung/Ansprüche",
            "Beilagen",
        ],
        "beschreibung_de": "Erstmeldung des Schadens an die Haftpflichtversicherung durch den VN oder dessen Anwalt.",
        "beschreibung_fr": "Déclaration initiale du sinistre à l'assureur RC par le preneur ou son avocat.",
    },
    "akteneinholung_vn": {
        "verfasser": "Haftpflichtversicherung (Claims Handler)",
        "empfaenger": "VN",
        "ton": "formal_brief",
        "woerter": (200, 400),
        "struktur": [
            "Bezugnahme auf Schadenmeldung",
            "Auflistung benötigter Unterlagen",
            "Frist",
            "Deckungsvorbehalt",
        ],
        "beschreibung_de": "Schreiben der Haftpflichtversicherung an den VN mit Aufforderung zur Akteneinreichung.",
        "beschreibung_fr": "Courrier de l'assureur RC au preneur demandant la remise des pièces.",
    },
    "stellungnahme_vn": {
        "verfasser": "VN oder Anwalt VN",
        "empfaenger": "Haftpflichtversicherung",
        "ton": "sachlich_argumentativ",
        "woerter": (400, 700),
        "struktur": [
            "Bezugnahme",
            "Sachverhaltsdarstellung aus VN-Sicht",
            "Rechtliche Einschätzung",
            "Antrag/Empfehlung",
        ],
        "beschreibung_de": "Stellungnahme des VN zu den Vorwürfen der Gegenpartei.",
        "beschreibung_fr": "Prise de position du preneur sur les reproches de la partie adverse.",
    },
    "Haftpflichtversicherungschreiben_an_g01": {
        "verfasser": "Haftpflichtversicherung (Claims Handler oder RA)",
        "empfaenger": "Gegenpartei oder deren Anwalt",
        "ton": "formal_brief",
        "woerter": (300, 600),
        "struktur": [
            "Bezugnahme",
            "Stellungnahme zur Forderung",
            "Substantiierungsaufforderung oder Gegenposition",
            "Vorbehalt",
        ],
        "beschreibung_de": "Schreiben der Haftpflichtversicherung an die Gegenpartei.",
        "beschreibung_fr": "Courrier de l'assureur RC à la partie adverse.",
    },
    "parteigutachten_g01": {
        "verfasser": "Privatexperte der Gegenpartei",
        "empfaenger": "Gegenpartei / Gericht",
        "ton": "neutral_technisch",
        "woerter": (500, 800),
        "struktur": [
            "Auftrag und Fragestellung",
            "Befund / Feststellungen",
            "Technische Beurteilung",
            "Schlussfolgerungen",
        ],
        "beschreibung_de": "Technisches Parteigutachten im Auftrag der Gegenpartei.",
        "beschreibung_fr": "Expertise technique de partie mandatée par la partie adverse.",
    },
    "gemeinsame_expertise_auftrag": {
        "verfasser": "Beide Parteien / Gericht",
        "empfaenger": "Gerichtsexperte",
        "ton": "formal_neutral",
        "woerter": (200, 400),
        "struktur": [
            "Bezeichnung der Parteien",
            "Gegenstand der Expertise",
            "Fragenkatalog",
            "Fristen und Modalitäten",
        ],
        "beschreibung_de": "Auftrag an einen gemeinsamen oder gerichtlichen Experten.",
        "beschreibung_fr": "Mandat confié à un expert commun ou judiciaire.",
    },
    "expertenbericht": {
        "verfasser": "Gerichtsexperte oder gemeinsamer Experte",
        "empfaenger": "Gericht / Parteien",
        "ton": "neutral_technisch",
        "woerter": (600, 1000),
        "struktur": [
            "Auftrag",
            "Untersuchungen und Befunde",
            "Beantwortung der Fragen",
            "Empfehlungen / Massnahmen",
            "Kosteneinschätzung",
        ],
        "beschreibung_de": "Technischer Expertenbericht mit Befunden und Empfehlungen.",
        "beschreibung_fr": "Rapport d'expertise technique avec constatations et recommandations.",
    },
    "gerichtsexpertise": {
        "verfasser": "Gerichtsexperte",
        "empfaenger": "Gericht",
        "ton": "neutral_technisch",
        "woerter": (600, 1000),
        "struktur": [
            "Mandat und Fragestellung",
            "Methodik",
            "Feststellungen",
            "Beantwortung des Fragenkatalogs",
            "Schlussfolgerungen",
        ],
        "beschreibung_de": "Gerichtlich angeordnete Expertise mit Beantwortung des Fragenkatalogs.",
        "beschreibung_fr": "Expertise judiciaire avec réponses au questionnaire.",
    },
    "vergleichsangebot": {
        "verfasser": "Haftpflichtversicherung oder Anwalt VN",
        "empfaenger": "Gegenpartei oder deren Anwalt",
        "ton": "formal_verhandlung",
        "woerter": (300, 500),
        "struktur": [
            "Bezugnahme auf Verhandlungen",
            "Vergleichsvorschlag mit Betrag",
            "Bedingungen (Saldoklausel, Fristen)",
            "Vorbehalt",
        ],
        "beschreibung_de": "Vergleichsangebot der Haftpflichtversicherung an die Gegenpartei.",
        "beschreibung_fr": "Proposition transactionnelle de l'assureur RC à la partie adverse.",
    },
    "ev_saldo": {
        "verfasser": "Haftpflichtversicherung",
        "empfaenger": "Gegenpartei",
        "ton": "formal_vertrag",
        "woerter": (300, 500),
        "struktur": [
            "Bezugnahme auf Vergleich",
            "Bestätigung der Zahlung",
            "Saldoklausel (per Saldo aller Ansprüche)",
            "Unterschriften",
        ],
        "beschreibung_de": "Erledigung per Saldo aller gegenseitigen Ansprüche.",
        "beschreibung_fr": "Règlement pour solde de tout compte.",
    },
    "prozessmeldung_intern": {
        "verfasser": "Claims Handler",
        "empfaenger": "Intern (Vorgesetzte, Aktuariat)",
        "ton": "intern_sachlich",
        "woerter": (400, 700),
        "struktur": [
            "Fallübersicht",
            "Aktueller Stand",
            "Rechtliche Einschätzung",
            "Reserveempfehlung",
            "Nächste Schritte",
        ],
        "beschreibung_de": "Interne Prozessmeldung mit Falleinschätzung und Reserveempfehlung.",
        "beschreibung_fr": "Rapport interne de procès avec évaluation et recommandation de réserve.",
    },
    "klage": {
        "verfasser": "Anwalt der Gegenpartei",
        "empfaenger": "Gericht",
        "ton": "gerichtlich_formal",
        "woerter": (500, 800),
        "struktur": [
            "Rubrum (Parteien, Gericht)",
            "Rechtsbegehren",
            "Sachverhalt",
            "Rechtliche Begründung",
            "Beweismittel",
        ],
        "beschreibung_de": "Klageschrift der Gegenpartei vor Gericht.",
        "beschreibung_fr": "Demande en justice déposée par la partie adverse.",
    },
    "klageantwort": {
        "verfasser": "Anwalt VN",
        "empfaenger": "Gericht",
        "ton": "gerichtlich_formal",
        "woerter": (500, 800),
        "struktur": [
            "Rubrum",
            "Anträge (Abweisung)",
            "Sachverhaltsdarstellung VN",
            "Rechtliche Gegenargumente",
            "Beweismittel",
        ],
        "beschreibung_de": "Klageantwort des VN auf die Klage der Gegenpartei.",
        "beschreibung_fr": "Réponse du preneur à la demande de la partie adverse.",
    },
    "gesuch_vbo": {
        "verfasser": "Anwalt (G01 oder VN)",
        "empfaenger": "Gericht",
        "ton": "gerichtlich_formal",
        "woerter": (400, 600),
        "struktur": [
            "Rubrum",
            "Rechtsbegehren (Beweissicherung)",
            "Begründung der Dringlichkeit",
            "Fragenkatalog",
            "Expertenvorschlag",
        ],
        "beschreibung_de": "Gesuch um vorsorgliche Beweisaufnahme nach ZPO 158.",
        "beschreibung_fr": "Requête de preuve à futur selon CPC 158.",
    },
    "expertenauftrag": {
        "verfasser": "Gericht",
        "empfaenger": "Ernannter Experte",
        "ton": "formal_neutral",
        "woerter": (300, 500),
        "struktur": [
            "Ernennungsverfügung",
            "Fragenkatalog",
            "Frist und Modalitäten",
            "Kostenvorschuss",
        ],
        "beschreibung_de": "Gerichtlicher Auftrag an den ernannten Experten.",
        "beschreibung_fr": "Mandat judiciaire à l'expert désigné.",
    },
    "urteilsauszug": {
        "verfasser": "Gericht",
        "empfaenger": "Parteien",
        "ton": "gerichtlich_formal",
        "woerter": (400, 700),
        "struktur": [
            "Rubrum",
            "Dispositiv (Urteilsspruch)",
            "Zusammenfassung der Erwägungen",
            "Kostenfolgen",
            "Rechtsmittelbelehrung",
        ],
        "beschreibung_de": "Auszug aus dem Gerichtsurteil mit Dispositiv und Kostenfolgen.",
        "beschreibung_fr": "Extrait du jugement avec dispositif et frais.",
    },
    "regressschreiben": {
        "verfasser": "Haftpflichtversicherung oder deren RA",
        "empfaenger": "Mithaftender / Dritter",
        "ton": "formal_brief",
        "woerter": (300, 500),
        "struktur": [
            "Bezugnahme auf Urteil/Vergleich",
            "Regressforderung",
            "Rechtsgrundlage",
            "Frist",
        ],
        "beschreibung_de": "Regressschreiben an mithaftende Dritte nach Leistung.",
        "beschreibung_fr": "Courrier de recours contre des tiers coresponsables après prestation.",
    },
    "schlichtungsgesuch": {
        "verfasser": "Anwalt (G01 oder VN)",
        "empfaenger": "Schlichtungsbehörde",
        "ton": "gerichtlich_formal",
        "woerter": (300, 500),
        "struktur": [
            "Parteien und Zuständigkeit",
            "Streitgegenstand",
            "Kurze Sachverhaltsdarstellung",
            "Begehren",
        ],
        "beschreibung_de": "Schlichtungsgesuch an die zuständige Behörde.",
        "beschreibung_fr": "Requête de conciliation à l'autorité compétente.",
    },
    "schlichtungsprotokoll": {
        "verfasser": "Schlichtungsbehörde",
        "empfaenger": "Parteien",
        "ton": "formal_neutral",
        "woerter": (200, 400),
        "struktur": [
            "Anwesende",
            "Verhandlungsverlauf",
            "Ergebnis (Einigung/Klagebewilligung)",
            "Unterschriften",
        ],
        "beschreibung_de": "Protokoll der Schlichtungsverhandlung.",
        "beschreibung_fr": "Procès-verbal de l'audience de conciliation.",
    },
    "abschlussnotiz": {
        "verfasser": "Claims Handler",
        "empfaenger": "Intern (Dossier)",
        "ton": "intern_sachlich",
        "woerter": (200, 400),
        "struktur": [
            "Fallzusammenfassung",
            "Ergebnis und Zahlung",
            "Lehren / Bemerkungen",
            "Dossierabschluss",
        ],
        "beschreibung_de": "Interne Abschlussnotiz mit Zusammenfassung und Lehren.",
        "beschreibung_fr": "Note interne de clôture avec résumé et enseignements.",
    },
    "Haftpflichtversicherungbesichtigung_protokoll": {
        "verfasser": "Claims Handler / Techniker",
        "empfaenger": "Intern (Dossier)",
        "ton": "intern_sachlich",
        "woerter": (300, 500),
        "struktur": [
            "Datum und Teilnehmer",
            "Befunde vor Ort",
            "Fotos / Skizzen (Beschreibung)",
            "Einschätzung und nächste Schritte",
        ],
        "beschreibung_de": "Protokoll der Besichtigung durch die Haftpflichtversicherung.",
        "beschreibung_fr": "Procès-verbal de la visite par l'assureur RC.",
    },
    "sanierungskonzept": {
        "verfasser": "VN oder externer Fachplaner",
        "empfaenger": "Haftpflichtversicherung / Bauherrschaft",
        "ton": "neutral_technisch",
        "woerter": (400, 700),
        "struktur": [
            "Ausgangslage",
            "Vorgeschlagene Massnahmen",
            "Kostenschätzung",
            "Zeitplan",
        ],
        "beschreibung_de": "Technisches Konzept für die Sanierung des Schadens.",
        "beschreibung_fr": "Concept technique pour la réparation du dommage.",
    },
    "streitverkuendung": {
        "verfasser": "Anwalt VN",
        "empfaenger": "Gericht / Drittpartei",
        "ton": "gerichtlich_formal",
        "woerter": (300, 500),
        "struktur": [
            "Bezugnahme auf Hauptverfahren",
            "Bezeichnung des Streitberufenen",
            "Begründung der Streitverkündung",
            "Antrag",
        ],
        "beschreibung_de": "Streitverkündung an einen potenziell mithaftenden Dritten.",
        "beschreibung_fr": "Dénonciation d'instance à un tiers potentiellement coresponsable.",
    },
    "widerrufsschreiben": {
        "verfasser": "Haftpflichtversicherung",
        "empfaenger": "Schlichtungsbehörde / Gegenpartei",
        "ton": "formal_brief",
        "woerter": (200, 300),
        "struktur": [
            "Bezugnahme auf Vergleich",
            "Erklärung des Widerrufs",
            "Neuer Vorschlag oder Verweis auf Verhandlung",
        ],
        "beschreibung_de": "Widerruf eines unter Vorbehalt geschlossenen Vergleichs.",
        "beschreibung_fr": "Révocation d'une transaction conclue sous réserve.",
    },
    "verbotsgesuch": {
        "verfasser": "Anwalt VN / Garantienehmer",
        "empfaenger": "Gericht",
        "ton": "gerichtlich_formal",
        "woerter": (400, 600),
        "struktur": [
            "Rubrum",
            "Superprovisorisches / Provisorisches Begehren",
            "Sachverhalt Garantieabruf",
            "Rechtliche Begründung (Missbrauch)",
        ],
        "beschreibung_de": "Gesuch um Verbot der Auszahlung einer Garantie.",
        "beschreibung_fr": "Requête d'interdiction de paiement d'une garantie.",
    },
    "gericht_verfuegung": {
        "verfasser": "Gericht",
        "empfaenger": "Parteien",
        "ton": "gerichtlich_formal",
        "woerter": (200, 400),
        "struktur": [
            "Rubrum",
            "Dispositiv",
            "Kurze Begründung",
            "Rechtsmittelbelehrung",
        ],
        "beschreibung_de": "Gerichtliche Verfügung (z.B. Ablehnung superprovisorischer Massnahmen).",
        "beschreibung_fr": "Ordonnance du tribunal (p. ex. rejet de mesures superprovisionnelles).",
    },
    "verhandlung_protokoll": {
        "verfasser": "Gericht",
        "empfaenger": "Parteien",
        "ton": "formal_neutral",
        "woerter": (300, 500),
        "struktur": [
            "Anwesende",
            "Verhandlungsverlauf",
            "Anträge der Parteien",
            "Verfügungen / Ergebnis",
        ],
        "beschreibung_de": "Protokoll einer Gerichtsverhandlung.",
        "beschreibung_fr": "Procès-verbal d'une audience du tribunal.",
    },
    "Haftpflichtversicherungschreiben_regress": {
        "verfasser": "Haftpflichtversicherung",
        "empfaenger": "VN / Garantienehmer",
        "ton": "formal_brief",
        "woerter": (300, 500),
        "struktur": [
            "Bezugnahme auf Garantiezahlung",
            "Regressforderung mit Betrag",
            "Rechtsgrundlage",
            "Zahlungsfrist / Ratenvorschlag",
        ],
        "beschreibung_de": "Regressschreiben der Haftpflichtversicherung an den Garantienehmer.",
        "beschreibung_fr": "Courrier de recours de l'assureur RC au preneur de garantie.",
    },
    "Haftpflichtversicherungschreiben_vertretung": {
        "verfasser": "Haftpflichtversicherung",
        "empfaenger": "Schlichtungsbehörde / Gericht",
        "ton": "formal_brief",
        "woerter": (150, 300),
        "struktur": [
            "Bezugnahme auf Vorladung",
            "Anmeldung der Vertretung",
            "Bevollmächtigung",
        ],
        "beschreibung_de": "Anmeldung der Vertretung der Haftpflichtversicherung bei Gericht/Schlichtung.",
        "beschreibung_fr": "Annonce de représentation de l'assureur RC auprès du tribunal/conciliation.",
    },
    "schlichtungsvorladung": {
        "verfasser": "Schlichtungsbehörde",
        "empfaenger": "Parteien",
        "ton": "formal_neutral",
        "woerter": (150, 300),
        "struktur": [
            "Bezeichnung der Parteien",
            "Datum und Ort der Verhandlung",
            "Hinweise zum Erscheinen",
            "Streitgegenstand",
        ],
        "beschreibung_de": "Vorladung zur Schlichtungsverhandlung.",
        "beschreibung_fr": "Citation à l'audience de conciliation.",
    },
    "mediationsnotiz": {
        "verfasser": "Mediator oder Claims Handler",
        "empfaenger": "Intern / Parteien",
        "ton": "intern_sachlich",
        "woerter": (200, 400),
        "struktur": [
            "Teilnehmer",
            "Verhandlungsverlauf",
            "Ergebnis / Scheitern",
            "Nächste Schritte",
        ],
        "beschreibung_de": "Notiz über den Mediationsversuch und dessen Ergebnis.",
        "beschreibung_fr": "Note sur la tentative de médiation et son résultat.",
    },
    "arbitre_verfuegung": {
        "verfasser": "Schiedsgericht / Einzelschiedsrichter",
        "empfaenger": "Parteien",
        "ton": "gerichtlich_formal",
        "woerter": (300, 500),
        "struktur": [
            "Verfahrensstand",
            "Zwischenergebnis",
            "Anordnungen",
            "Nächste Schritte",
        ],
        "beschreibung_de": "Zwischenverfügung des Schiedsgerichts.",
        "beschreibung_fr": "Ordonnance intermédiaire du tribunal arbitral.",
    },
    "schiedsspruch": {
        "verfasser": "Schiedsgericht",
        "empfaenger": "Parteien",
        "ton": "gerichtlich_formal",
        "woerter": (500, 800),
        "struktur": [
            "Rubrum und Verfahrensgeschichte",
            "Erwägungen",
            "Dispositiv (Spruch)",
            "Kostenfolgen",
        ],
        "beschreibung_de": "Endgültiger Schiedsspruch des Schiedsgerichts.",
        "beschreibung_fr": "Sentence arbitrale définitive du tribunal arbitral.",
    },
}


def get_template(doc_type: str) -> dict[str, Any]:
    """Return the template for a document type, with fallback for unknown types."""
    if doc_type in DOCUMENT_TEMPLATES:
        return DOCUMENT_TEMPLATES[doc_type]
    return {
        "verfasser": "Verfasser",
        "empfaenger": "Empfänger",
        "ton": "formal_brief",
        "woerter": (300, 600),
        "struktur": ["Einleitung", "Hauptteil", "Schluss"],
        "beschreibung_de": f"Dokument vom Typ '{doc_type}'.",
        "beschreibung_fr": f"Document de type '{doc_type}'.",
    }


def build_user_prompt(case_bible: dict, doc_entry: dict, template: dict) -> str:
    """Build the user prompt for a single document generation."""
    sprache = doc_entry.get("sprache", case_bible.get("sprache", "DE"))
    beschreibung_key = "beschreibung_fr" if sprache == "FR" else "beschreibung_de"
    beschreibung = template.get(beschreibung_key, template.get("beschreibung_de", ""))

    min_w, max_w = template["woerter"]
    struktur_text = "\n".join(f"  - {s}" for s in template["struktur"])

    case_json = json.dumps(case_bible, indent=2, ensure_ascii=False)

    if sprache == "FR":
        prompt = (
            f"## Case-Bible (contexte du cas)\n\n```json\n{case_json}\n```\n\n"
            f"## Document à générer\n\n"
            f"- **Type** : {doc_entry['typ']}\n"
            f"- **Date** : {doc_entry['datum']}\n"
            f"- **Description** : {beschreibung}\n"
            f"- **Auteur** : {template['verfasser']}\n"
            f"- **Destinataire** : {template['empfaenger']}\n"
            f"- **Ton** : {template['ton']}\n"
            f"- **Longueur** : {min_w}–{max_w} mots\n\n"
            f"## Structure attendue\n\n{struktur_text}\n\n"
            f"Rédigez le document complet en français. "
            f"Utilisez UNIQUEMENT les faits du Case-Bible ci-dessus."
        )
    else:
        prompt = (
            f"## Case-Bible (Fallkontext)\n\n```json\n{case_json}\n```\n\n"
            f"## Zu generierendes Dokument\n\n"
            f"- **Typ** : {doc_entry['typ']}\n"
            f"- **Datum** : {doc_entry['datum']}\n"
            f"- **Beschreibung** : {beschreibung}\n"
            f"- **Verfasser** : {template['verfasser']}\n"
            f"- **Empfänger** : {template['empfaenger']}\n"
            f"- **Ton** : {template['ton']}\n"
            f"- **Länge** : {min_w}–{max_w} Wörter\n\n"
            f"## Erwartete Struktur\n\n{struktur_text}\n\n"
            f"Erstelle das vollständige Dokument auf Deutsch. "
            f"Verwende NUR Fakten aus der obigen Case-Bible."
        )

    return prompt
