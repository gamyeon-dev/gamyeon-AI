# callback_receiver.py
from fastapi import FastAPI, Request
from datetime import date, datetime
import json
import uvicorn

app = FastAPI()



@app.post("/internal/v1/questions/callback")
async def receive_question_callback(request: Request):

    body = await request.json()
    now = datetime.now()
    print("🟢 WEBHOOK 수신 성공!")
    print("  📋 Payload:", body)
    print("  🆔 intvId:", body.get("intvId"))
    print("  ✅ Status:", body.get("status"))
    print("  ❓ Questions:", body.get("questions", []))
    print("  ❌ Error:", body.get("errorMessage"))
    print("-" * 50)
    return {"status": "received"}

@app.post("/internal/v1/reports/callback")
async def receive_callback(request: Request):
    body = await request.json()
    now = datetime.now()
    print("\n" + "="*60)
    print("✅ 콜백 수신!")
    print("현재 시간:", now)
    print(json.dumps(body, ensure_ascii=False, indent=2))
    print("="*60)
    return {"ok": True}



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)
