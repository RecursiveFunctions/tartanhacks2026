"""Simple FastAPI site for the Friend Roulette project.

This file serves a small static site and exposes an API endpoint that
reuses the CSV overlap logic from `friend-roulette-overlaps.py`.
Run with:

    uvicorn Website:app --reload

or

    python Website.py

"""

import os
import csv
import importlib.util
import fcntl
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

BASE_DIR = os.path.dirname(__file__)

app = FastAPI()

# Serve templates and static assets
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# Pydantic model for bot submission
class AvailabilitySubmission(BaseModel):
    andrew_id: str
    availability: dict  # {hour_block: "days_string"}


def load_overlaps_module():
    """Dynamically load the `friend-roulette-overlaps.py` script as a module."""
    path = os.path.join(BASE_DIR, "friend-roulette-overlaps.py")
    spec = importlib.util.spec_from_file_location("overlaps_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_csv_headers():
    """Get all headers from the CSV file."""
    csv_path = os.path.join(BASE_DIR, "CMU Friend Roulette Availability Responses - Form Responses 1.csv")
    if not os.path.exists(csv_path):
        return []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or []


def append_to_csv(andrew_id, availability_dict):
    """Append a new row to the CSV with the user's availability."""
    csv_path = os.path.join(BASE_DIR, "CMU Friend Roulette Availability Responses - Form Responses 1.csv")
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    # Read all headers from the CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
    
    if not headers:
        raise ValueError("CSV file is empty or corrupted")
    
    # Build the new row
    new_row = {}
    new_row['Timestamp'] = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
    new_row['AndrewID'] = andrew_id
    
    # Fill in availability for each hour block
    for header in headers:
        if header.startswith('Please check which hour blocks'):
            # Extract hour block from header (e.g., "[7am - 8am]")
            hour_block = None
            if '[' in header and ']' in header:
                hour_block = header.split('[')[1].split(']')[0]
            
            # Set the day(s) available for this hour block
            if hour_block and hour_block in availability_dict:
                new_row[header] = availability_dict[hour_block]
            else:
                new_row[header] = ''
        elif header not in new_row:
            new_row[header] = ''
    
    # Append the row to the CSV while holding an exclusive file lock
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        try:
            # Acquire exclusive lock
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writerow(new_row)
            # Ensure data is flushed to disk
            f.flush()
            try:
                os.fsync(f.fileno())
            except Exception:
                # fsync may not be available on all platforms; ignore if it fails
                pass
        finally:
            # Release lock
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            except Exception:
                pass


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


@app.get("/bot", response_class=HTMLResponse)
async def bot_page(request: Request):
    """Render the bot form page."""
    return templates.TemplateResponse("bot.html", {"request": request})


@app.get("/api/bot/headers")
async def get_hour_blocks():
    """Return available hour blocks for the bot form."""
    csv_path = os.path.join(BASE_DIR, "CMU Friend Roulette Availability Responses - Form Responses 1.csv")
    
    if not os.path.exists(csv_path):
        return JSONResponse({"error": "CSV file not found"}, status_code=404)
    
    try:
        hour_blocks = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for header in reader.fieldnames:
                if header.startswith('Please check which hour blocks'):
                    block = header.split('[')[1].split(']')[0]
                    hour_blocks.append(block)
        
        return JSONResponse({"hour_blocks": sorted(hour_blocks)})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/bot/submit")
async def submit_availability(submission: AvailabilitySubmission):
    """Accept availability data and append to CSV."""
    try:
        # Validate Andrew ID
        if not submission.andrew_id or not submission.andrew_id.strip():
            return JSONResponse({"error": "Andrew ID is required"}, status_code=400)
        
        if not submission.availability or len(submission.availability) == 0:
            return JSONResponse({"error": "At least one time block must be selected"}, status_code=400)
        
        # Append to CSV
        append_to_csv(submission.andrew_id.strip(), submission.availability)
        
        return JSONResponse({
            "success": True,
            "message": f"Availability submitted for {submission.andrew_id}"
        })
    except FileNotFoundError as e:
        return JSONResponse({"error": str(e)}, status_code=404)
    except Exception as e:
        return JSONResponse({"error": f"Failed to submit: {str(e)}"}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("Website:app", host="127.0.0.1", port=8000, reload=True)
