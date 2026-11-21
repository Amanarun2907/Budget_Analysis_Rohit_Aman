from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from app.services.mcp.server import mcp_server

router = APIRouter()

class MCPToolCallRequest(BaseModel):
    name: str = Field(..., description="Tool name to execute")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool input arguments")

@router.get("/tools")
async def list_mcp_tools():
    """List all available Model Context Protocol (MCP) tools for budget analysis."""
    return {"tools": mcp_server.list_tools()}

@router.post("/execute")
async def execute_mcp_tool(request: MCPToolCallRequest):
    """Execute an MCP tool and return structured financial and econometric data."""
    try:
        result = mcp_server.call_tool(request.name, request.arguments)
        return {
            "status": "success",
            "tool": request.name,
            "content": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")
