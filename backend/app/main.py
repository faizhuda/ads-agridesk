from fastapi import FastAPI

app = FastAPI(title="Agridesk API")

@app.get("/")
def root():
    return {"message": "Agridesk API Running"}