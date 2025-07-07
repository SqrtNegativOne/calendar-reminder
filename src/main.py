import uvicorn
from config import PORT
from app import create_app # for uvicorn

if __name__ == "__main__":
    uvicorn.run("main:create_app", host="0.0.0.0", port=PORT, factory=True)