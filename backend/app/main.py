from fastapi import FastAPI

app = FastAPI(title="ORKO API", version="0.0.1")

@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "orko-api"}
