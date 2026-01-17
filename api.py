from fastapi import APIRouter, HTTPException
from schemas import GetCombined, Termin
from config import EV_URL
import httpx
import asyncio
from datetime import time

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/")
async def bool(get: GetCombined) -> list[Termin]:
    async with httpx.AsyncClient(timeout=20.0) as client:
        requests = (
            client.get(f"{EV_URL}/urniki/{user_id}") for user_id in get.user_ids
        )
        responses = await asyncio.gather(*requests)

    combined_termini = []

    for response in responses:
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail="Error fetching data."
            )
        data = response.json()
        raw_terms = data.get("termini", [])
        combined_termini.extend(Termin(**t) for t in raw_terms)

    return merge_overlapping_terms(combined_termini)


def merge_overlapping_terms(terms: list[Termin]) -> list[Termin]:
    sorted_terms = sorted(terms, key=lambda t: (t.dan, t.zacetek))
    merged_terms = []

    for current in sorted_terms:
        if not merged_terms:
            merged_terms.append(current)
        else:
            last_merged = merged_terms[-1]
            last_end_time = time(
                hour=(last_merged.zacetek.hour + last_merged.dolzina // 60) % 24,
                minute=(last_merged.zacetek.minute + last_merged.dolzina % 60) % 60,
            )

            if current.dan == last_merged.dan and current.zacetek < last_end_time:
                new_dolzina = max(
                    last_merged.dolzina,
                    current.dolzina
                    + (current.zacetek.hour - last_merged.zacetek.hour) * 60
                    + (current.zacetek.minute - last_merged.zacetek.minute),
                )

                merged_terms[-1] = Termin(
                    termin_id=None,
                    zacetek=min(last_merged.zacetek, current.zacetek),
                    dolzina=new_dolzina,
                    dan=last_merged.dan,
                    lokacija=None,
                    tip=None,
                    predmet=None,
                    aktivnost=None,
                )
            else:
                merged_terms.append(current)

    return merged_terms
