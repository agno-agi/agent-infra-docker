from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools

from app.models import OPENAI_MODEL_ID
from db.session import get_postgres_db

# ************* Team Members Setup *************
web_agent = Agent(
    id="web-agent",
    name="Web Search Agent",
    role="Handle web search requests and general research",
    model=OpenAIChat(id=OPENAI_MODEL_ID),
    instructions=[
        "Search for current and relevant information on financial topics",
        "Always include sources and publication dates",
        "Focus on reputable financial news sources",
        "Provide context and background information",
    ],
    tools=[DuckDuckGoTools()],
    db=get_postgres_db(),
    add_datetime_to_context=True,
)

research_agent = Agent(
    id="research-agent",
    name="Research Specialist",
    role="Advanced research and analysis using AI-powered search",
    model=OpenAIChat(id=OPENAI_MODEL_ID),
    instructions=[
        "You are a professional research specialist using comprehensive web search capabilities.",
        "Conduct thorough research on any topic using DuckDuckGo search to find authoritative sources.",
        "Focus on finding current and relevant information from reputable publications and websites.",
        "Use tables and structured formats to present your findings clearly.",
        "Always cite your sources and provide publication dates when available.",
        "Analyze trends, patterns, and insights from the research data.",
        "Provide well-reasoned analysis and actionable insights based on comprehensive web research.",
    ],
    tools=[DuckDuckGoTools()],
    db=get_postgres_db(),
    add_datetime_to_context=True,
)

# ************* Reasoning Research Team Setup *************
reasoning_research_team = Team(
    id="reasoning-research-team",
    name="Advanced Research & Analysis Team",
    model=OpenAIChat(id=OPENAI_MODEL_ID),
    description="Strategic research and analysis team combining web intelligence, advanced reasoning tools, and collaborative investigation to deliver evidence-based insights with structured analysis and clear recommendations",
    instructions=dedent("""\
        You are a professional research and analysis team. Collaborate to provide comprehensive research and analysis on any topic.
        Combine web search, advanced research, and content analysis capabilities.
        Provide well-researched insights with clear evidence and reasoning.
        Use tables and structured formats to display information clearly.
        Always cite sources and verify information accuracy.
        Present findings in a logical, easy-to-follow format.
        Focus on actionable insights and practical recommendations.
        Only output the final consolidated analysis, not individual agent responses.
        Keep responses professional and informative.
    """),
    # -*- Tools -*-
    tools=[ReasoningTools(add_instructions=True)],
    # -*- Members and Settings -*-
    members=[
        web_agent,
        research_agent,
    ],
    # -*- Storage -*-
    db=get_postgres_db(),
    add_history_to_context=True,
    num_history_runs=3,
    # Other settings
    markdown=True,
    add_datetime_to_context=True,
    debug_mode=True,
)
