from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API IA Rutas Industriales funcionando correctamente por ROQUE GARCIA ESPINOZA 🚀"}

from typing import List, Literal, Tuple, Dict
from fastapi import FastAPI
from pydantic import BaseModel
import itertools
import random

app = FastAPI(title="IA Rutas Industriales")

# -----------------------------
# 1) Modelo de la planta (rejilla) y ubicaciones
#    Usamos distancia Manhattan.
# -----------------------------

Point = Tuple[int, int]

ALMACEN: Point = (0, 0)  # puedes ajustar según tu figura (origen)

# Ubicaciones de ejemplo (x, y) en la rejilla.
# Ajusta los puntos para que coincidan con tu diagrama.
DESTINOS: Dict[str, Point] = {
    # nombres únicos para cada “embalaje”
    "emb_A_p1": (9, 9),    # Embalaje A, protocolo_1
    "emb_A_p2": (9, 8),    # Embalaje A, protocolo_2
    "emb_B_p1": (9, 7),
    "emb_B_p2": (9, 6),
    "emb_C_p1": (9, 5),
    "emb_C_p2": (9, 4),
}

def manhattan(a: Point, b: Point) -> int:
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

# -----------------------------
# 2) Modelos de entrada/salida
# -----------------------------
Protocol = Literal["protocolo_1", "protocolo_2"]

class Producto(BaseModel):
    destino_id: str      # debe existir en DESTINOS
    protocolo: Protocol  # "protocolo_1" | "protocolo_2"

class PlanRequest(BaseModel):
    # productos disponibles en almacén (sin orden)
    productos: List[Producto]

class Ruta(BaseModel):
    secuencia: List[str]   # ["ALMACEN", destino1, destino2, ...]
    distancia: int

class PlanResponse(BaseModel):
    viaje_destinos: List[str]   # hasta 3 destinos elegidos
    ruta_optima: Ruta
    notas: str

# -----------------------------
# 3) Selección de hasta 3 destinos:
#    - Prioriza protocolo_1
#    - No repite destino
#    - Si faltan, completa al azar (prob. uniforme)
# -----------------------------
def seleccionar_destinos(productos: List[Producto], k: int = 3) -> List[str]:
    # filtra válidos
    productos = [p for p in productos if p.destino_id in DESTINOS]
    # evita duplicados por destino
    vistos = set()
    lista = []
    for p in productos:
        if p.destino_id not in vistos:
            lista.append(p)
            vistos.add(p.destino_id)

    # prioriza protocolo_1
    p1 = [p.destino_id for p in lista if p.protocolo == "protocolo_1"]
    p2 = [p.destino_id for p in lista if p.protocolo == "protocolo_2"]

    random.shuffle(p2)  # prob. uniforme al completar
    elegidos = p1[:k]
    if len(elegidos) < k:
        faltan = k - len(elegidos)
        elegidos += p2[:faltan]

    return elegidos

# -----------------------------
# 4) Ruta mínima (permuta exhaustiva)
#    Desde ALMACEN -> d1 -> d2 -> d3 (hasta 3)
# -----------------------------
def mejor_ruta(destinos: List[str]) -> Ruta:
    if not destinos:
        return Ruta(secuencia=["ALMACEN"], distancia=0)

    best_dist = 10**9
    best_seq = None

    for perm in itertools.permutations(destinos):
        dist = 0
        actual = ALMACEN
        sec = ["ALMACEN"]
        for d in perm:
            nxt = DESTINOS[d]
            dist += manhattan(actual, nxt)
            actual = nxt
            sec.append(d)
        if dist < best_dist:
            best_dist = dist
            best_seq = sec

    return Ruta(secuencia=best_seq, distancia=best_dist)

# -----------------------------
# 5) Endpoint principal: /plan
# -----------------------------
@app.post("/plan", response_model=PlanResponse)
def planificar(req: PlanRequest):
    destinos_viaje = seleccionar_destinos(req.productos, k=3)
    ruta = mejor_ruta(destinos_viaje)
    notas = (
        "Se priorizaron destinos con protocolo_1. "
        "No se repitió ningún destino en el viaje. "
        "Se usó distancia Manhattan y permutación exhaustiva para minimizar la ruta."
    )
    return PlanResponse(viaje_destinos=destinos_viaje, ruta_optima=ruta, notas=notas)

@app.get("/")
def health():
    return {"message": "API IA Rutas Industriales funcionando correctamente 🚀"}


