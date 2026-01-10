from pydantic import BaseModel
from typing import Optional
from datetime import time


class GetCombined(BaseModel):
    user_ids: list[int]


class Predmet(BaseModel):
    predmet_id: int
    oznaka: str
    ime: str


class Aktivnost(BaseModel):
    aktivnost_id: Optional[int] = None
    oznaka: str
    ime: str


class Termin(BaseModel):
    termin_id: int
    zacetek: time
    dolzina: int
    dan: int
    lokacija: str
    tip: str
    predmet: Optional[Predmet] = None
    aktivnost: Optional[Aktivnost] = None
