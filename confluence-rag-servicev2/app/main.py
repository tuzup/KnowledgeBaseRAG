from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.pipeline import RAGPipeline

app = FastAPI(title="Confluence RAG Service")

class Request(BaseModel):
    url: str
    username: str
    token: str
    recursive: bool = True
    max_depth: int = -1

@app.post("/process")
def run_process(req: Request):
    try:
        pipeline = RAGPipeline(req)
        result = pipeline.run()
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(500, detail=str(e))