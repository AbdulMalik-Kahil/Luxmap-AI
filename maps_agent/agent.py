from google.adk.agents import Agent , LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from mcp.client.stdio import StdioServerParameters
from google.adk.planners import BuiltInPlanner
from google.genai import types as genai_types
from .prompt import MAPS_PROMPT
from config import GOOGLE_MAPS_API_KEY

def create_maps_agent() -> Agent:
    return LlmAgent(
        name="maps_agent_mcp",
        model="gemini-2.5-flash",
        description="Specialized agent for retrieving information from Google Maps via MCPToolset.",
        instruction=MAPS_PROMPT,
        planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=False)
    ),
        tools=[
            MCPToolset(
                connection_params=StdioServerParameters(
                    
                        command='npx',
                        args=["-y", "@modelcontextprotocol/server-google-maps"],
                        env={"GOOGLE_MAPS_API_KEY": GOOGLE_MAPS_API_KEY}
                )
            )
        ]
    )

root_agent = create_maps_agent()

