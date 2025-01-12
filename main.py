from fastapi import FastAPI
from routers import contacts  

app = FastAPI()


app.include_router(contacts.router, prefix="/contacts", tags=["contacts"])

@app.get("/")
def read_root():
    """
    Этот маршрут обрабатывает запросы к корню URL (http://127.0.0.1:8000/).
    """
    return {"message": "Welcome to the Contacts API!"}

@app.get("/favicon.ico")
async def favicon():
    """
    Этот маршрут обрабатывает запросы на favicon.ico (например, от браузеров).
    """
    return {"message": "No favicon available"}
