from pydantic import BaseModel, Field


class AIAnalyzeRequest(BaseModel):
    debate_id: str
    force: bool = False


class AIClaimOutput(BaseModel):
    position: str
    text: str
    confidence: float = 0.5


class AIEvidenceOutput(BaseModel):
    claim_text: str
    title: str
    content: str
    source_type: str = "web"
    supports: bool = True
    relevance: float = 0.5
    reliability_score: float = 0.5
    url: str | None = None


class AICounterargumentOutput(BaseModel):
    claim_text: str
    text: str
    strength: float = 0.5
    type: str = "rebuttal"


class AISynthesisOutput(BaseModel):
    synthesis: str
    confidence: float
    pro_score: float
    con_score: float
    uncertainty: float
    supporting_factors: list[str] = []
    weaknesses: list[str] = []
    unresolved_questions: list[str] = []
    fallback_used: bool = False


class AIAnalysisResult(BaseModel):
    claims_created: int
    evidence_created: int
    counterarguments_created: int
    contradictions_detected: int
    synthesis: AISynthesisOutput
    fallback_used: bool = False
