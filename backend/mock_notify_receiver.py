from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Data receiver")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/notify")
async def receiver1(request: Request):
    data = await request.json()

    print("==============================\n")
    print(data["data"])
    print("==============================\n")

    return {"status": "received"}

@app.post("/notify2")
async def receiver2(request: Request):
    data = await request.json()

    print("==============================\n")
    print(data["data"])
    print("==============================\n")

    return {"status": "received"}

if __name__ == "__main__":
    uvicorn.run("mock_notify_receiver:app", host="0.0.0.0", port=9000)
