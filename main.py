from fastapi import FastAPI
from routers import contacts  
from routers.auth import router as auth_router


app = FastAPI()


app.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])

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
