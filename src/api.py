from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import asyncio
import uvicorn
import json
from datetime import datetime

from main import EnhancedNPCSystem

# Modèles de données
class InteractionRequest(BaseModel):
    npc_id: str
    action: str
    data: Dict

class UpdateRequest(BaseModel):
    delta_time: float
    world_data: Optional[Dict] = None

class NPCQuery(BaseModel):
    npc_id: str
    properties: List[str]

# Création de l'application
app = FastAPI(
    title="Enhanced NPC System API",
    description="API pour le système de PNJ autonomes",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instance du système NPC
npc_system: Optional[EnhancedNPCSystem] = None
update_task: Optional[asyncio.Task] = None

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage"""
    global npc_system, update_task
    
    # Création du système
    npc_system = EnhancedNPCSystem()
    
    # Initialisation
    if not await npc_system.initialize():
        raise Exception("Erreur lors de l'initialisation du système NPC")
    
    # Démarrage de la boucle de mise à jour
    update_task = asyncio.create_task(update_loop())

@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage à l'arrêt"""
    global npc_system, update_task
    
    # Arrêt de la boucle de mise à jour
    if update_task:
        update_task.cancel()
        try:
            await update_task
        except asyncio.CancelledError:
            pass
    
    # Arrêt du système
    if npc_system:
        npc_system.shutdown()

async def update_loop():
    """Boucle de mise à jour du monde"""
    while True:
        try:
            await npc_system.update_world(1.0)
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Erreur dans la boucle de mise à jour: {str(e)}")

# Routes de l'API
@app.post("/interact")
async def interact_with_npc(request: InteractionRequest):
    """Interaction avec un PNJ"""
    if not npc_system:
        raise HTTPException(status_code=503, detail="Système non initialisé")
    
    result = await npc_system.interact_with_npc(
        request.npc_id,
        request.action,
        request.data
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@app.post("/update")
async def update_world(request: UpdateRequest):
    """Mise à jour manuelle du monde"""
    if not npc_system:
        raise HTTPException(status_code=503, detail="Système non initialisé")
    
    # Mise à jour des données du monde
    if request.world_data:
        npc_system.world_state.update(request.world_data)
    
    # Mise à jour du monde
    await npc_system.update_world(request.delta_time)
    
    return {"success": True}

@app.get("/npc/{npc_id}")
async def get_npc_info(npc_id: str):
    """Récupération des informations d'un PNJ"""
    if not npc_system:
        raise HTTPException(status_code=503, detail="Système non initialisé")
    
    npc = npc_system.get_npc(npc_id)
    if not npc:
        raise HTTPException(status_code=404, detail="PNJ non trouvé")
    
    return npc

@app.post("/npc/query")
async def query_npc(query: NPCQuery):
    """Requête d'informations spécifiques sur un PNJ"""
    if not npc_system:
        raise HTTPException(status_code=503, detail="Système non initialisé")
    
    npc = npc_system.get_npc(query.npc_id)
    if not npc:
        raise HTTPException(status_code=404, detail="PNJ non trouvé")
    
    result = {}
    for prop in query.properties:
        try:
            if prop in npc["data"]:
                result[prop] = npc["data"][prop]
            elif prop in npc["systems"]:
                system = npc["systems"][prop]
                if hasattr(system, "get_state"):
                    result[prop] = system.get_state()
        except Exception as e:
            result[prop] = str(e)
    
    return result

@app.get("/world")
async def get_world_state():
    """Récupération de l'état du monde"""
    if not npc_system:
        raise HTTPException(status_code=503, detail="Système non initialisé")
    
    return npc_system.world_state

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Point d'entrée WebSocket pour les mises à jour en temps réel"""
    if not npc_system:
        await websocket.close(code=1013)  # Try again later
        return
    
    await websocket.accept()
    
    try:
        while True:
            # Réception des messages
            data = await websocket.receive_json()
            
            # Traitement des différents types de messages
            if data["type"] == "interact":
                result = await npc_system.interact_with_npc(
                    data["npc_id"],
                    data["action"],
                    data["data"]
                )
                await websocket.send_json({
                    "type": "interaction_result",
                    "data": result
                })
            
            elif data["type"] == "subscribe":
                # Abonnement aux mises à jour d'un PNJ
                npc_id = data["npc_id"]
                while True:
                    npc = npc_system.get_npc(npc_id)
                    if npc:
                        await websocket.send_json({
                            "type": "npc_update",
                            "npc_id": npc_id,
                            "data": npc["data"]
                        })
                    await asyncio.sleep(1)
    
    except Exception as e:
        print(f"Erreur WebSocket: {str(e)}")
    
    finally:
        await websocket.close()

# Exemple d'intégration Unity
@app.post("/unity/update")
async def unity_update(data: Dict[str, Any]):
    """Point d'entrée spécifique pour Unity"""
    if not npc_system:
        raise HTTPException(status_code=503, detail="Système non initialisé")
    
    try:
        # Mise à jour de la position des PNJ
        for npc_id, position in data.get("npc_positions", {}).items():
            npc = npc_system.get_npc(npc_id)
            if npc:
                npc["data"]["position"] = position
        
        # Mise à jour des états d'animation
        for npc_id, anim_state in data.get("npc_animations", {}).items():
            npc = npc_system.get_npc(npc_id)
            if npc:
                npc["data"]["animation_state"] = anim_state
        
        # Mise à jour du monde
        await npc_system.update_world(data.get("delta_time", 1.0))
        
        # Retour des mises à jour
        return {
            "npc_updates": {
                npc_id: {
                    "target_position": npc["data"].get("target_position"),
                    "desired_animation": npc["data"].get("desired_animation"),
                    "dialogue_state": npc["data"].get("dialogue_state")
                }
                for npc_id, npc in npc_system.npcs.items()
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Exemple d'intégration Unreal
@app.post("/unreal/update")
async def unreal_update(data: Dict[str, Any]):
    """Point d'entrée spécifique pour Unreal Engine"""
    if not npc_system:
        raise HTTPException(status_code=503, detail="Système non initialisé")
    
    try:
        # Mise à jour similaire à Unity
        # Mais avec des formats de données spécifiques à Unreal
        return {
            "npc_updates": {
                npc_id: {
                    "behavior_tree_state": npc["data"].get("behavior_state"),
                    "blackboard_values": npc["data"].get("blackboard"),
                    "animation_montage": npc["data"].get("desired_montage")
                }
                for npc_id, npc in npc_system.npcs.items()
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def start_api(host: str = "0.0.0.0", port: int = 8000):
    """Démarre le serveur API"""
    uvicorn.run(app, host=host, port=port)
