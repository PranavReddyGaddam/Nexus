import asyncio
import time
from typing import Optional
import httpx


BASE_URL = "http://127.0.0.1:8000"


async def main(product_idea: str = "AI-powered personal finance copilot") -> None:
    async with httpx.AsyncClient(timeout=60) as client:
        # Kick off analysis
        resp = await client.post(
            f"{BASE_URL}/api/analyze",
            json={"product_idea": product_idea},
        )
        resp.raise_for_status()
        data = resp.json()
        session_id = data["session_id"]
        print(f"Started session: {session_id}")

        # Poll for results
        start = time.time()
        while True:
            r = await client.get(f"{BASE_URL}/api/analysis/{session_id}")
            r.raise_for_status()
            result = r.json()
            status = result.get("status")
            print(f"Status: {status}")
            if status == "completed" and result.get("analysis_results"):
                print("Analysis complete. Summary:")
                print(result["analysis_results"].get("summary", ""))
                break
            if time.time() - start > 180:
                raise TimeoutError("Timed out waiting for analysis to complete")
            await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())


