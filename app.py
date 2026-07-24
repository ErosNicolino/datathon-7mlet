from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

segmentos_stats = {
    "nonexistent": {"sucessos": 1, "falhas": 1},
    "failure": {"sucessos": 1, "falhas": 1},
    "success": {"sucessos": 1, "falhas": 1},
}

import numpy as np

class Cliente(BaseModel):
    poutcome: str

@app.post("/recomendar")
def recomendar(cliente: Cliente):
    amostras = {}
    for s, stats in segmentos_stats.items():
        amostras[s] = np.random.beta(stats["sucessos"], stats["falhas"])
    melhor_segmento = max(amostras, key=amostras.get)
    decisao = "OFERTAR" if cliente.poutcome == melhor_segmento else "NAO_PRIORIZAR"
    return {"cliente_poutcome": cliente.poutcome, "decisao": decisao}