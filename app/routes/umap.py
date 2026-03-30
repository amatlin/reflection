"""UMAP coordinates endpoint — serves precomputed 2D scatter data."""

import json
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/umap", tags=["umap"])

COORDS_PATH = Path(__file__).resolve().parent.parent.parent / "pipeline" / "umap" / "coordinates.json"

_coords_cache: list[dict] | None = None


def _load_coordinates() -> list[dict]:
    global _coords_cache
    if _coords_cache is None:
        if COORDS_PATH.exists():
            with open(COORDS_PATH) as f:
                _coords_cache = json.load(f)
        else:
            _coords_cache = []
    return _coords_cache


@router.get("/coordinates")
async def get_coordinates():
    """Return precomputed UMAP coordinates for the scatter plot."""
    coords = _load_coordinates()
    return JSONResponse(content=coords)
