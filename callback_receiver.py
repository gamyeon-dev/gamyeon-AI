# callback_receiver.py
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.post("/internal/v1/questions/callback")
async def receive_question_callback(request: Request):
    body = await request.json()
    print("🟢 WEBHOOK 수신 성공!")
    print("  📋 Payload:", body)
    print("  🆔 intvId:", body.get("intvId"))
    print("  ✅ Status:", body.get("status"))
    print("  ❓ Questions:", body.get("questions", []))
    print("  ❌ Error:", body.get("errorMessage"))
    print("-" * 50)
    return {"status": "received"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)
