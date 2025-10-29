from fastapi import FastAPI
from app.routers import example

app = FastAPI(title="SaveWorkIA")

# Registrar routers
app.include_router(example.router)

@app.get("/")
def read_root():
    return {"message": "Proyecto SaveWorkIA funcionando"}
