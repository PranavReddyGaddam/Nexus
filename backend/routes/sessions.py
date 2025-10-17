from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.schemas import SessionCreate, SessionResponse
from config.snowflake import get_snowflake_connection

router = APIRouter()

@router.get("/sessions", response_model=List[SessionResponse])
async def get_sessions(conn = Depends(get_snowflake_connection)):
    """
    Get all analysis sessions
    """
    try:
        cur = conn.cursor()
        try:
            cur.execute("SELECT ID, PRODUCT_IDEA, STATUS, CREATED_AT, UPDATED_AT FROM SESSIONS ORDER BY CREATED_AT DESC")
            rows = cur.fetchall()
        finally:
            cur.close()
        return [
            SessionResponse(
                id=row[0],
                product_idea=row[1],
                status=row[2],
                created_at=row[3],
                updated_at=row[4],
            )
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions", response_model=SessionResponse)
async def create_session(session_data: SessionCreate, conn = Depends(get_snowflake_connection)):
    """
    Create a new analysis session
    """
    try:
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO SESSIONS (PRODUCT_IDEA, STATUS, CREATED_AT, UPDATED_AT) VALUES (%s, %s, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())",
                (session_data.product_idea, "created"),
            )
        finally:
            cur.close()

        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT ID, PRODUCT_IDEA, STATUS, CREATED_AT, UPDATED_AT FROM SESSIONS WHERE PRODUCT_IDEA=%s ORDER BY CREATED_AT DESC LIMIT 1",
                (session_data.product_idea,),
            )
            row = cur.fetchone()
            if not row:
                raise RuntimeError("Failed to retrieve new session after insert")
        finally:
            cur.close()

        return SessionResponse(
            id=row[0],
            product_idea=row[1],
            status=row[2],
            created_at=row[3],
            updated_at=row[4],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: int, conn = Depends(get_snowflake_connection)):
    """
    Get a specific analysis session
    """
    try:
        cur = conn.cursor()
        try:
            cur.execute("SELECT ID, PRODUCT_IDEA, STATUS, CREATED_AT, UPDATED_AT FROM SESSIONS WHERE ID=%s", (session_id,))
            row = cur.fetchone()
        finally:
            cur.close()
        if not row:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionResponse(
            id=row[0],
            product_idea=row[1],
            status=row[2],
            created_at=row[3],
            updated_at=row[4]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: int, conn = Depends(get_snowflake_connection)):
    """
    Delete an analysis session
    """
    try:
        cur = conn.cursor()
        try:
            cur.execute("SELECT 1 FROM SESSIONS WHERE ID=%s", (session_id,))
            exists = cur.fetchone() is not None
        finally:
            cur.close()
        if not exists:
            raise HTTPException(status_code=404, detail="Session not found")

        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM SESSIONS WHERE ID=%s", (session_id,))
        finally:
            cur.close()
        
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
