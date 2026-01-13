import asyncio
from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.db.session import get_db
from app.models import Attendance, ClassSession, User, UserRole
from app.services.dashboard import build_dashboard_payload

router = APIRouter(tags=["ws"])

connections: Dict[int, List[WebSocket]] = {}


async def broadcast(session_id: int, message: dict):
    websockets = connections.get(session_id, [])
    for ws in list(websockets):
        try:
            await ws.send_json(message)
        except RuntimeError:
            websockets.remove(ws)


def schedule_broadcast(session_id: int, message: dict) -> None:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        loop.create_task(broadcast(session_id, message))


async def send_snapshot(session: ClassSession, websocket: WebSocket, db: Session) -> None:
    snapshot = build_dashboard_payload(db, session)
    await websocket.send_json({"type": "snapshot", "payload": snapshot.dict()})


@router.websocket("/ws/session/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: int,
    token: str,
    db: Session = Depends(get_db),
):
    payload = verify_token(token)
    if payload is None:
        await websocket.close(code=4001)
        return

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        await websocket.close(code=4003)
        return

    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        await websocket.close(code=4404)
        return

    if user.role == UserRole.TEACHER:
        if session.teacher_id != user.id:
            await websocket.close(code=4003)
            return
    else:
        attendance = (
            db.query(Attendance)
            .filter(Attendance.session_id == session_id, Attendance.student_id == user.id)
            .first()
        )
        if not attendance:
            await websocket.close(code=4003)
            return

    await websocket.accept()
    connections.setdefault(session_id, []).append(websocket)

    if user.role == UserRole.TEACHER:
        await send_snapshot(session, websocket, db)

    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif user.role == UserRole.TEACHER:
                # teachers broadcast manual annotations (alerts)
                schedule_broadcast(
                    session_id,
                    {
                        "type": "teacher_note",
                        "payload": data,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )
    except WebSocketDisconnect:
        connections[session_id].remove(websocket)

