import uvicorn
from fastapi import FastAPI
from routers import router

app = FastAPI(title="CarbonCount API")

app.include_router(router)

@app.get("/")
def root():
    return {"status": "OK"}

if __name__ == "__main__":
    # 关键修正：使用字符串形式启动
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)