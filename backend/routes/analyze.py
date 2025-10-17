from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Dict, Any
from models.schemas import AnalysisRequest, AnalysisResponse, IdeaAnalyzeRequest, IdeaAnalyzeResponse
from services.analysis_service import AnalysisService
from config.snowflake import get_snowflake_connection
import json

router = APIRouter()
analysis_service = AnalysisService()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_product_idea(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    conn = Depends(get_snowflake_connection)
):
    """
    Analyze a product idea and return market research results
    """
    try:
        # Create new session in Snowflake
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO SESSIONS (PRODUCT_IDEA, STATUS, CREATED_AT, UPDATED_AT) VALUES (%s, %s, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())",
                (request.product_idea, "processing"),
            )
        finally:
            cur.close()

        # Fetch the latest session id for this product idea
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT ID FROM SESSIONS WHERE PRODUCT_IDEA=%s ORDER BY CREATED_AT DESC LIMIT 1",
                (request.product_idea,),
            )
            row = cur.fetchone()
            if not row:
                raise RuntimeError("Failed to retrieve session id after insert")
            session_id = int(row[0])
        finally:
            cur.close()
        
        # Run analysis in background
        background_tasks.add_task(run_analysis_background, request.product_idea, session_id)
        
        # Return immediate response
        return AnalysisResponse(
            session_id=session_id,
            product_idea=request.product_idea,
            analysis_results=None,  # Will be updated via WebSocket
            metadata={
                "processing_started": True,
                "session_id": session_id
            },
            status="processing"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def run_analysis_background(product_idea: str, session_id: int):
    """
    Background task to run analysis and save results
    """
    try:
        # Run the analysis
        analysis_response = await analysis_service.run_analysis(product_idea, session_id)
        
        # Save results to Snowflake
        save_analysis_results(session_id, analysis_response)
        
    except Exception as e:
        print(f"Background analysis error: {e}")
        # Update session status to failed
        import snowflake.connector
        from config.settings import settings
        conn = snowflake.connector.connect(
            account=settings.snowflake_account,
            user=settings.snowflake_user,
            password=settings.snowflake_password,
            warehouse=settings.snowflake_warehouse,
            database=settings.snowflake_database,
            schema=settings.snowflake_schema,
        )
        try:
            cur = conn.cursor()
            try:
                cur.execute(
                    "UPDATE SESSIONS SET STATUS=%s, UPDATED_AT=CURRENT_TIMESTAMP() WHERE ID=%s",
                    ("failed", session_id),
                )
            finally:
                cur.close()
        finally:
            conn.close()

def save_analysis_results(session_id: int, analysis_response: AnalysisResponse):
    """Save analysis results to database"""
    try:
        # Convert results to JSON strings for storage
        personas_json = json.dumps([persona.dict() for persona in analysis_response.analysis_results.personas])
        opinions_json = json.dumps([opinion.dict() for opinion in analysis_response.analysis_results.opinions])
        sentiment_json = json.dumps(analysis_response.analysis_results.sentiment_breakdown.dict())
        
        import snowflake.connector
        from config.settings import settings
        conn = snowflake.connector.connect(
            account=settings.snowflake_account,
            user=settings.snowflake_user,
            password=settings.snowflake_password,
            warehouse=settings.snowflake_warehouse,
            database=settings.snowflake_database,
            schema=settings.snowflake_schema,
        )
        try:
            cur = conn.cursor()
            try:
                cur.execute(
                    """
                    INSERT INTO ANALYSIS_RESULTS (
                        SESSION_ID, PERSONAS, OPINIONS, SUMMARY, SENTIMENT_BREAKDOWN,
                        MARKET_POTENTIAL, CONFIDENCE_SCORE, CREATED_AT
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP())
                    """,
                    (
                        session_id,
                        personas_json,
                        opinions_json,
                        analysis_response.analysis_results.summary,
                        sentiment_json,
                        analysis_response.analysis_results.market_potential,
                        analysis_response.metadata.get("confidence_score", 0),
                    ),
                )
                cur.execute(
                    "UPDATE SESSIONS SET STATUS=%s, UPDATED_AT=CURRENT_TIMESTAMP() WHERE ID=%s",
                    ("completed", session_id),
                )
            finally:
                cur.close()
        finally:
            conn.close()
        
    except Exception as e:
        print(f"Error saving analysis results: {e}")
        db.rollback()

@router.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_results(analysis_id: int, conn = Depends(get_snowflake_connection)):
    """
    Get analysis results by ID
    """
    try:
        # Get session
        cur = conn.cursor()
        try:
            cur.execute("SELECT ID, PRODUCT_IDEA, STATUS FROM SESSIONS WHERE ID=%s", (analysis_id,))
            row = cur.fetchone()
        finally:
            cur.close()
        if not row:
            raise HTTPException(status_code=404, detail="Session not found")
        session_product_idea = row[1]
        session_status = row[2]
        
        # Get analysis results
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT PERSONAS, OPINIONS, SUMMARY, SENTIMENT_BREAKDOWN, MARKET_POTENTIAL,
                       CONFIDENCE_SCORE, CREATED_AT
                FROM ANALYSIS_RESULTS WHERE SESSION_ID=%s ORDER BY CREATED_AT DESC LIMIT 1
                """,
                (analysis_id,),
            )
            res = cur.fetchone()
        finally:
            cur.close()
        
        if not res:
            return AnalysisResponse(
                session_id=analysis_id,
                product_idea=session_product_idea,
                analysis_results=None,
                metadata={"status": "processing"},
                status=session_status
            )
        
        # Parse JSON data
        personas = json.loads(res[0]) if res[0] else []
        opinions = json.loads(res[1]) if res[1] else []
        sentiment_breakdown = json.loads(res[3]) if res[3] else {}
        
        # Create response
        from models.schemas import AnalysisResults, Persona, Opinion, SentimentBreakdown
        
        analysis_results = AnalysisResults(
            personas=[Persona(**p) for p in personas],
            opinions=[Opinion(**o) for o in opinions],
            summary=res[2] or "",
            sentiment_breakdown=SentimentBreakdown(**sentiment_breakdown),
            market_potential=res[4] or "unknown",
            key_insights=[],  # Could be stored separately if needed
            recommendations=[]  # Could be stored separately if needed
        )
        
        return AnalysisResponse(
            session_id=analysis_id,
            product_idea=session_product_idea,
            analysis_results=analysis_results,
            metadata={
                "confidence_score": res[5],
                "created_at": res[6].isoformat() if res[6] else None
            },
            status=session_status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rank", response_model=IdeaAnalyzeResponse)
async def rank_product_idea(
    request: IdeaAnalyzeRequest,
    conn = Depends(get_snowflake_connection)
):
    """
    Rank and evaluate a product idea with structured scoring using predefined personas
    """
    try:
        print(f"Starting ranking for idea: {request.idea}")
        
        # Import personas data
        from data.personas import get_random_personas
        print("Successfully imported personas module")
        
        # Get random personas for evaluation
        personas = get_random_personas(request.max_personas)
        print(f"Got {len(personas)} personas for evaluation")
        
        # Call OpenAI for ranking analysis with specific personas
        ranking_results = await analysis_service.openai_service.rank_product_idea(
            request.idea, 
            personas
        )
        print("OpenAI ranking completed successfully")
        
        # Create response using the ranking schemas
        response = IdeaAnalyzeResponse(
            enhancedIdea=ranking_results["enhanced_idea"],
            results=ranking_results["results"],
            summary=ranking_results["summary"]
        )
        
        return response
        
    except Exception as e:
        print(f"Error in rank_product_idea: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
