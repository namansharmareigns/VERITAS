from fastapi import APIRouter, HTTPException

from app.agents.debate_pipeline import DebateAnalysisPipeline
from app.schemas.ai import AIAnalyzeRequest

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/analyze")
async def analyze_debate(payload: AIAnalyzeRequest):
    pipeline = DebateAnalysisPipeline()
    try:
        result = await pipeline.analyze_debate(payload.debate_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result


@router.post("/synthesize")
async def synthesize_debate(payload: AIAnalyzeRequest):
    return await analyze_debate(payload)
