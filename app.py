from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API IA Rutas Industriales funcionando correctamente 🚀"}
