import asyncio

from fastapi import WebSocket , APIRouter , WebSocketDisconnect

router = APIRouter(prefix="/chat" , tags=["Chat"])

connetion_dict = {}

@router.websocket("/{user_id}")
async def connected_users(websocket : WebSocket , user_id : int):
    await websocket.accept()
    connetion_dict[user_id] = websocket

    async def keepalive():
        while True:
            await asyncio.sleep(20)  # ping every 20 seconds
            try:
                await websocket.send_text("ping")
            except:
                break

    asyncio.create_task(keepalive()) 

    try:
        while True:
            data = await websocket.receive_text()  # wait for incoming
            if data == "ping":
                continue  # ignore ping messages  
            # send to everyone else
            for uid, ws in connetion_dict.items():
                if uid != user_id:
                    await ws.send_text(f"user {user_id}: {data}")
                    
    except WebSocketDisconnect:
        del connetion_dict[user_id]
        await ws.send_text(f"user {user_id} has left the chat")
            # clean up when user leaves