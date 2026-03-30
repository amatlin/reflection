"""UMAP coordinates endpoint — serves precomputed 2D scatter data."""

import json
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/umap", tags=["umap"])

COORDS_PATH = Path(__file__).resolve().parent.parent.parent / "pipeline" / "umap" / "coordinates.json"

_coords_cache: list[dict] | None = None
_coords_mtime: float = 0.0


def _load_coordinates() -> list[dict]:
    """Load coordinates from disk, re-reading if the file has changed."""
    global _coords_cache, _coords_mtime
    if COORDS_PATH.exists():
        mtime = COORDS_PATH.stat().st_mtime
        if _coords_cache is None or mtime != _coords_mtime:
            with open(COORDS_PATH) as f:
                _coords_cache = json.load(f)
            _coords_mtime = mtime
    elif _coords_cache is None:
        _coords_cache = []
    return _coords_cache


@router.get("/coordinates")
async def get_coordinates():
    """Return precomputed UMAP coordinates for the scatter plot."""
    coords = _load_coordinates()
    return JSONResponse(content=coords)
