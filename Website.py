"""Simple FastAPI site for the Friend Roulette project.

This file serves a small static site and exposes an API endpoint that
reuses the CSV overlap logic from `friend-roulette-overlaps.py`.
Run with:

    uvicorn Website:app --reload

or

    python Website.py

"""

import os
import importlib.util
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = os.path.dirname(__file__)

app = FastAPI()

# Serve templates and static assets
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def load_overlaps_module():
    """Dynamically load the `friend-roulette-overlaps.py` script as a module."""
    path = os.path.join(BASE_DIR, "friend-roulette-overlaps.py")
    spec = importlib.util.spec_from_file_location("overlaps_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the index page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/overlaps")
async def api_overlaps():
    """Return overlapping availability as JSON by reusing the CSV script."""
    overlaps_mod = load_overlaps_module()
    csv_path = os.path.join(BASE_DIR, "CMU Friend Roulette Availability Responses - Form Responses 1.csv")

    if not os.path.exists(csv_path):
        return JSONResponse({"error": "CSV file not found", "path": csv_path}, status_code=404)

    try:
        data = overlaps_mod.load_availability_data(csv_path)
        pairs = overlaps_mod.find_overlapping_pairs_by_day(data)
        
        # Convert tuple keys to string keys for JSON serialization
        pairs_list = []
        for (id1, id2), schedule in pairs.items():
            pairs_list.append({
                "id1": id1,
                "id2": id2,
                "schedule": schedule
            })
        
        return JSONResponse({"pairs_count": len(pairs_list), "pairs": pairs_list})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("Website:app", host="127.0.0.1", port=8000, reload=True)
