
"""Google Maps Agent A2A Service Entry Point."""

import logging
import os

import click
import uvicorn

# A2A server imports
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from dotenv import load_dotenv

# ADK imports
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from maps_agent.agent import create_maps_agent

# Local agent imports
from maps_agent.agent_executor import MapsADKAgentExecutor

# Load environment variables from .env file
load_dotenv()

# Basic logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--host",
    "host",
    default=os.getenv("A2A_MAPS_HOST", "localhost"),
    show_default=True,
    help="Host for the Google Maps agent server.",
)
@click.option(
    "--port",
    "port",
    default=int(os.getenv("A2A_MAPS_PORT", 8002)),
    show_default=True,
    type=int,
    help="Port for the Google Maps agent server.",
)
def main(host: str, port: int) -> None:
    """Runs the Google Maps ADK Agent as an A2A service."""

    # Check for required API key
    if not os.getenv("GOOGLE_MAPS_API_KEY"):
        logger.warning(
            "GOOGLE_MAPS_API_KEY environment variable not set. "
            "The Google Maps MCP server might fail to authenticate."
        )

    # Define AgentCard for Google Maps
    maps_skill = AgentSkill(
        id="maps_search",
        name="Search Google Maps",
        description="Searches and retrieves information from Google Maps including places, directions, and location details.",
        tags=["maps", "search", "retrieval", "location", "places"],
        examples=[
            "Find restaurants near me",
            "Get directions to a location",
            "Search for hotels in Cairo",
        ],
    )

    agent_card = AgentCard(
        name="Google Maps Agent",
        description="Provides location-based information retrieval services from Google Maps using MCP.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=AgentCapabilities(streaming=False, pushNotifications=False),
        skills=[maps_skill],
    )

    try:
        # Create the actual ADK Agent
        adk_agent = create_maps_agent()

        # Initialize the ADK Runner (following official ADK pattern)
        runner = Runner(
            app_name=agent_card.name,
            agent=adk_agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

        # Instantiate the AgentExecutor with the runner
        agent_executor = MapsADKAgentExecutor(
            agent=adk_agent, agent_card=agent_card, runner=runner
        )

    except Exception as e:
        logger.error(
            f"Failed to initialize Google Maps Agent components: {e}", exc_info=True
        )
        return

    # Set up the A2A request handler
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor, task_store=InMemoryTaskStore()
    )

    # Create the A2A Starlette application
    a2a_app = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )

    logger.info(f"Starting Google Maps Agent server on http://{host}:{port}")
    logger.info(f"Agent Name: {agent_card.name}, Version: {agent_card.version}")
    if agent_card.skills:
        for skill in agent_card.skills:
            logger.info(f"  Skill: {skill.name} (ID: {skill.id}, Tags: {skill.tags})")

    # Run the Uvicorn server
    uvicorn.run(a2a_app.build(), host=host, port=port)


if __name__ == "__main__":
    main()
