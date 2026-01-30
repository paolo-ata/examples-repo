from __future__ import annotations

from pydantic import BaseModel


class Spanne(BaseModel):
    min: float
    max: float


class Betraege(BaseModel):
    forderung_brutto: float
    erwartete_spanne: Spanne
    sb: float
    pe_logic: str


class Parteien(BaseModel):
    vn: str
    g01: str
    anwalt_vn: str
    anwalt_g01: str


class Ereignis(BaseModel):
    t: str
    event: str


class Sachverhalt(BaseModel):
    kurz: str
    zeitleiste: list[Ereignis]


class Recht(BaseModel):
    normen: list[str]
    strittig: list[str]
    deckung: list[str]


class DokumentPlanEintrag(BaseModel):
    typ: str
    datum: str
    sprache: str


class CaseBible(BaseModel):
    case_id: str
    sprache: str
    kanton: str
    gericht: str
    branche: str
    cluster: str
    parteien: Parteien
    sachverhalt: Sachverhalt
    recht: Recht
    betraege: Betraege
    status: str
    dokument_plan: list[DokumentPlanEintrag]


class GeneratedDocument(BaseModel):
    content: str
    metadata: dict


class DocumentProgress(BaseModel):
    case_id: str
    doc_index: int
    status: str = "pending"  # pending / completed / failed
