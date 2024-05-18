import structlog
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
import threading

log = structlog.get_logger()
app = FastAPI()

# Global variable to store the table data
table_data = []


def fetch_data_from_url(url):
    log.info("Fetching data from URL", url=url)
    response = requests.get(url)
    return response


def split_names(names):
    """Split names into first and last names."""
    split_names = []
    for name in names:
        if ", " in name:
            last_name, first_name = name.split(", ", 1)
            split_names.append({"first_name": first_name, "last_name": last_name})
        else:
            split_names.append({"first_name": name, "last_name": ""})
    return split_names


def extract_table_data(soup):
    table = soup.find("table", class_="mktt_active_tables")
    rows = table.find_all("tr")[1:]  # Skip the header row
    table_data = []

    for row in rows:
        cols = row.find_all("td")
        tisch = int(cols[0].text.strip()) if cols[0].text.strip().isdigit() else None
        spieler_1 = (
            [name.strip() for name in cols[1].get_text(separator="<br>").split("<br>")]
            if cols[1].get_text(separator="<br>")
            else []
        )
        spieler_2 = (
            [name.strip() for name in cols[2].get_text(separator="<br>").split("<br>")]
            if cols[2].get_text(separator="<br>")
            else []
        )
        klasse = cols[3].text.strip() if cols[3].text.strip() else ""
        typ = cols[4].text.strip() if cols[4].text.strip() else ""

        table_data.append(
            {
                "Tisch": tisch,
                "Spieler 1": split_names(spieler_1),
                "Spieler 2": split_names(spieler_2),
                "Klasse": klasse,
                "Typ": typ,
            }
        )

    return table_data


def update_table_data():
    global table_data
    url = (
        "https://www.tvwallau.de/abteilungen/tischtennis/turnier2024/active_tables.html"
    )
    response = fetch_data_from_url(url)
    soup = BeautifulSoup(response.text, "html.parser")
    table_data = extract_table_data(soup)
    log.info("Table data updated")


def periodic_update(interval: int):
    while True:
        update_table_data()
        time.sleep(interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the background thread to update the table data periodically
    interval = 60  # Update every 60 seconds
    thread = threading.Thread(target=periodic_update, args=(interval,), daemon=True)
    thread.start()
    yield
    # Cleanup code can be added here if needed


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Table Tennis Tournament API"}


@app.get("/table_data")
def get_table_data():
    return JSONResponse(content=table_data)


# Allow CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
