"""WebSocket endpoints for SLA monitoring, real-time notifications, and delivery status."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sla_ws_manager import sla_ws_manager
from routes.notification_routes import ws_manager as notif_ws_manager
from utils.delivery_ws_manager import delivery_ws_manager

router = APIRouter(tags=["WebSockets"])


@router.websocket("/ws/sla")
async def sla_websocket_endpoint(websocket: WebSocket):
    user_id = websocket.query_params.get("user_id")
    await sla_ws_manager.connect(websocket, user_id=user_id)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text('{"type":"pong"}')
    except WebSocketDisconnect:
        sla_ws_manager.disconnect(websocket, user_id=user_id)
    except Exception:
        sla_ws_manager.disconnect(websocket, user_id=user_id)


@router.websocket("/ws/notifications")
async def notifications_websocket(websocket: WebSocket):
    user_id = websocket.query_params.get("user_id")
    if not user_id:
        await websocket.close(code=4001)
        return
    await notif_ws_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text('{"type":"pong"}')
    except WebSocketDisconnect:
        notif_ws_manager.disconnect(websocket, user_id)
    except Exception:
        notif_ws_manager.disconnect(websocket, user_id)


@router.websocket("/ws/delivery")
async def delivery_websocket_endpoint(websocket: WebSocket):
    user_id = websocket.query_params.get("user_id")
    if not user_id:
        await websocket.close(code=4001)
        return
    await delivery_ws_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text('{"type":"pong"}')
    except WebSocketDisconnect:
        delivery_ws_manager.disconnect(websocket, user_id)
    except Exception:
        delivery_ws_manager.disconnect(websocket, user_id)

