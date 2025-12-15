from textwrap import dedent
from typing import List

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.workflow.condition import Condition
from agno.workflow.loop import Loop
from agno.workflow.step import Step
from agno.workflow.types import StepInput, StepOutput, WorkflowExecutionInput
from agno.workflow.workflow import Workflow
from pydantic import BaseModel

from app.models import OPENAI_MODEL_ID
from db.session import get_postgres_db


# ************* Input Schema *************
class InvestmentWorkflowInput(BaseModel):
    investment_request: str


# ************* Agents *************
market_researcher = Agent(
    name="Financial Market Researcher",
    model=OpenAIChat(id=OPENAI_MODEL_ID),
    tools=[DuckDuckGoTools()],
    description=dedent("""\
        Expert financial researcher specializing in comprehensive market analysis, 
        company research, and investment opportunity identification.
    """),
    instructions=dedent("""\
        You are a professional financial market researcher with expertise in investment analysis.

        **Your Mission:**
        Conduct comprehensive research on investment opportunities using advanced search techniques.

        **Research Strategy:**
        1. **Parse Investment Request** - Extract companies, sectors, investment goals, and criteria
        
        2. **Multi-Source Research** - Use DuckDuckGo search for comprehensive coverage:
        
        **DuckDuckGo Research ** - Use for broader market coverage:
           - Yahoo Finance, Bloomberg, MarketWatch data
           - SEC filings and investor relations pages
           - Financial news and market commentary
           - Analyst ratings and price targets

        **Research Areas:**
        - **Company Fundamentals**: Revenue, earnings, growth rates, financial health
        - **Market Position**: Competitive landscape, market share, industry trends
        - **Recent Developments**: News, earnings reports, product launches, partnerships
        - **Analyst Opinions**: Ratings, price targets, investment recommendations
        - **Risk Factors**: Market risks, company-specific risks, regulatory concerns

        **Output Format:**
        - **Company Overview**: Basic information and business model
        - **Financial Performance**: Key metrics and recent performance
        - **Market Analysis**: Industry trends and competitive position
        - **Recent News**: Important developments and market impact
        - **Analyst Sentiment**: Professional opinions and ratings
        - **Source References**: All URLs and sources used in research

        Always capture and save source URLs for credibility and further research.
    """),
    db=get_postgres_db(),
    markdown=True,
    debug_mode=True,
)

financial_analyst = Agent(
    name="Financial Analyst",
    model=OpenAIChat(id=OPENAI_MODEL_ID),
    tools=[DuckDuckGoTools()],
    description=dedent("""\
        Expert financial analyst specializing in quantitative analysis, 
        valuation modeling, and investment recommendations.
    """),
    instructions=dedent("""\
        You are a professional financial analyst focused on quantitative analysis and valuation.

        **Your Role:**
        Analyze financial data and provide investment recommendations based on research findings.

        **Analysis Tasks:**
        1. **Financial Analysis** - Evaluate financial metrics and performance
        2. **Valuation Analysis** - Calculate intrinsic value and compare to market price
        3. **Risk Assessment** - Identify and quantify investment risks
        4. **Comparative Analysis** - Compare multiple investment opportunities
        5. **Investment Recommendations** - Provide clear buy/hold/sell recommendations

        **Use Python Tools For:**
        - Financial ratio calculations (P/E, P/B, ROE, ROA, etc.)
        - Valuation models (DCF, comparable company analysis)
        - Risk metrics (beta, volatility, Sharpe ratio)
        - Portfolio optimization and allocation
        - Data visualization and charts

        **Output Format:**
        - **Financial Summary**: Key metrics and ratios
        - **Valuation Analysis**: Fair value estimates and price targets
        - **Risk Assessment**: Risk factors and mitigation strategies
        - **Investment Recommendation**: Clear recommendation with rationale
        - **Supporting Calculations**: Python-generated analysis and charts
        - **References**: Source URLs for all data and research

        Focus on data-driven analysis with clear supporting calculations and credible sources.
    """),
    db=get_postgres_db(),
    markdown=True,
    debug_mode=True,
)

portfolio_strategist = Agent(
    name="Portfolio Strategist",
    model=OpenAIChat(id=OPENAI_MODEL_ID),
    tools=[DuckDuckGoTools()],
    description=dedent("""\
        Expert portfolio strategist specializing in asset allocation, 
        risk management, and investment strategy development.
    """),
    instructions=dedent("""\
        You are a professional portfolio strategist focused on creating optimal investment strategies.

        **Your Role:**
        Synthesize research and analysis to create comprehensive investment strategies and portfolio recommendations.

        **Strategy Development:**
        1. **Portfolio Construction** - Create optimal asset allocation
        2. **Risk Management** - Implement risk controls and diversification
        3. **Strategic Recommendations** - Provide actionable investment advice
        4. **Performance Monitoring** - Set benchmarks and success metrics
        5. **Market Timing** - Assess optimal entry and exit strategies

        **Use Python Tools For:**
        - Portfolio optimization calculations
        - Risk-return analysis and efficient frontier
        - Monte Carlo simulations for scenario analysis
        - Correlation analysis and diversification metrics
        - Performance attribution and tracking

        **Output Format:**
        - **Investment Strategy**: Overall approach and philosophy
        - **Portfolio Allocation**: Specific weightings and rationale
        - **Risk Management**: Risk controls and mitigation strategies
        - **Implementation Plan**: Step-by-step execution guidance
        - **Performance Metrics**: Success measures and benchmarks
        - **References**: All sources and supporting research

        Create comprehensive strategies backed by quantitative analysis and credible market research.
    """),
    db=get_postgres_db(),
    markdown=True,
    debug_mode=True,
)


# ************* Step Functions *************
async def parse_investment_request_step(execution_input: WorkflowExecutionInput) -> StepOutput:
    """Parse and validate the investment request"""
    search_input = execution_input.input

    parse_prompt = f"""
    Parse this investment request and extract key information:
    
    **Request**: {search_input.investment_request}
    
    Extract and identify:
    1. **Companies/Tickers**: Specific company names or stock symbols mentioned
    2. **Sectors/Industries**: Industry sectors or themes (tech, healthcare, etc.)
    3. **Investment Goals**: Growth, income, value, speculation, etc.
    4. **Time Horizon**: Short-term, medium-term, long-term
    5. **Risk Tolerance**: Conservative, moderate, aggressive
    6. **Budget/Amount**: Investment amount if mentioned
    7. **Special Criteria**: ESG, dividend yield, market cap, etc.
    
    If the request is vague or missing key information, suggest specific companies or sectors to research.
    Provide at least 1 specific investment opportunity to analyze.
    
    Format your response as:
    - **Companies**: [list of companies/tickers]
    - **Sectors**: [list of sectors]
    - **Goals**: [investment objectives]
    - **Horizon**: [time frame]
    - **Risk**: [risk level]
    - **Criteria**: [special requirements]
    """

    result = await market_researcher.arun(parse_prompt)

    return StepOutput(
        content=f"""
            # Investment Request Parsing

            ## Original Request
            {search_input.investment_request}

            ## Parsed Investment Criteria
            {result.content}
        """.strip(),
        success=True,
    )


async def conduct_market_research_step(execution_input: WorkflowExecutionInput) -> StepOutput:
    """Conduct comprehensive market research"""
    search_input = execution_input.input

    research_prompt = f"""
    Conduct comprehensive investment research based on this request:
    
    **Investment Request**: {search_input.investment_request}
    
    **Research Strategy - Execute Multiple Searches:**
    
    **Phase 1: Company Research** (Use DuckDuckGo search for high-quality data)
    - Search for each company's latest earnings reports and financial statements
    - Find recent analyst reports and investment research
    - Look for company news, developments, and market updates
    - Research management changes, product launches, partnerships
    
    **Phase 2: Market Context** (Use DuckDuckGo search)
    - Industry trends and sector performance
    - Competitive landscape and market positioning  
    - Economic factors affecting the investments
    - Regulatory changes and policy impacts
    
    **Quality Standards:**
    - Include specific numbers and data points
    - Cite recent sources (within last 6 months preferred)
    - Provide balanced view (pros and cons)
    - Include at least 5 credible source URLs
    
    **Reference Collection:**
    - **Capture all source URLs** from your research
    - **Save links** to financial reports, analyst research, and news sources
    - **Note the source** for each piece of financial data
    
    Focus on finding credible, recent information from reputable financial sources.
    """

    result = await market_researcher.arun(research_prompt)

    return StepOutput(
        content=f"""
            # Market Research Findings

            ## Investment Request
            {search_input.investment_request}

            ## Research Results
            {result.content}
        """.strip(),
        success=True,
    )


async def financial_analysis_step(execution_input: WorkflowExecutionInput) -> StepOutput:
    """Conduct financial analysis and valuation"""
    search_input = execution_input.input
    research_content = execution_input.get_step_content("Market Research")

    analysis_prompt = f"""
    Conduct detailed financial analysis based on the market research:
    
    **Original Investment Request**: {search_input.investment_request}
    
    **Market Research Data**:
    {research_content}
    
    Please provide:
    
    1. **Financial Analysis**: 
       - Calculate key financial ratios and metrics
       - Evaluate financial health and performance trends
       - Compare metrics to industry benchmarks
       - Assess growth rates and profitability
    
    2. **Valuation Analysis**:
       - Estimate intrinsic value using appropriate models
       - Compare current market price to fair value
       - Calculate price targets and potential returns
       - Assess valuation relative to peers
    
    3. **Risk Assessment**:
       - Identify and quantify investment risks
       - Calculate risk metrics (beta, volatility, etc.)
       - Assess company-specific and market risks
       - Evaluate risk-adjusted returns
    
    4. **Investment Recommendations**:
       - Provide clear buy/hold/sell recommendations
       - Explain rationale with supporting analysis
       - Set price targets and time horizons
       - Identify key catalysts and risks
    
    5. **Supporting Analysis**:
       - Use Python tools for calculations and visualizations
       - Create charts and graphs where helpful
       - Show detailed financial modeling work
    
    6. **References & Sources**:
       - List all source URLs from your research
       - Include publication dates and data sources
       - Provide links to financial reports and analysis
    
    Use DuckDuckGo search for additional financial data.
    """

    result = await financial_analyst.arun(analysis_prompt)

    return StepOutput(
        content=f"""
            # Financial Analysis & Investment Recommendations       

            ## Investment Request
            {search_input.investment_request}       

            ## Financial Analysis
            {result.content}        
        """.strip(),
        success=True,
    )


async def portfolio_strategy_step(execution_input: WorkflowExecutionInput) -> StepOutput:
    """Create comprehensive portfolio strategy and implementation plan"""

    search_input = execution_input.input
    research_content = execution_input.get_step_content("Market Research")
    analysis_content = execution_input.get_step_content("Financial Analysis")

    strategy_prompt = f"""
    Create a comprehensive investment strategy based on all research and analysis:
    
    **Original Investment Request**: {search_input.investment_request}
    
    **Market Research**:
    {research_content}
    
    **Financial Analysis**:
    {analysis_content}
    
    Please provide:
    
    1. **Investment Strategy**: Overall approach and philosophy
    2. **Portfolio Allocation**: Specific allocation percentages and weightings
    3. **Risk Management**: Risk controls and position sizing
    4. **Implementation Plan**: Step-by-step execution guidance
    5. **Performance Metrics**: Success measures and benchmarks
    6. **References**: All sources and supporting research
    
    Include comprehensive references to all research sources.
    """

    result = await portfolio_strategist.arun(strategy_prompt)

    return StepOutput(
        content=f"""
            # Investment Strategy & Portfolio Recommendations
            
            ## Investment Request
            {search_input.investment_request}
            
            ## Strategic Recommendations
            {result.content}
            
            ## Disclaimer
            This analysis is for educational purposes only and should not be considered as financial advice.
            Please consult with a qualified financial advisor before making investment decisions.
        """.strip(),
        success=True,
    )


# ************* Quality Check Functions *************
def check_research_quality(outputs: List[StepOutput]) -> bool:
    """Check if research quality is sufficient"""
    if not outputs:
        return False

    latest_output = outputs[-1]
    content = latest_output.content.lower()

    # Quality indicators
    quality_indicators = [
        "price" in content or "market cap" in content,
        "revenue" in content or "earnings" in content,
        "http" in content or "source" in content,  # URLs/references
        len(content) > 1000,  # Substantial content
        "risk" in content or "analysis" in content,
    ]

    # Need at least 3 out of 5 quality indicators
    return sum(quality_indicators) >= 3


def check_analysis_quality(outputs: List[StepOutput]) -> bool:
    """Check if financial analysis quality is sufficient"""
    if not outputs:
        return False

    latest_output = outputs[-1]
    content = latest_output.content.lower()

    # Analysis quality indicators
    analysis_indicators = [
        "valuation" in content or "value" in content,
        "recommendation" in content or "buy" in content or "sell" in content,
        "risk" in content or "beta" in content,
        "python" in content or "calculation" in content,
    ]

    # Need at least 3 out of 4 analysis indicators
    return sum(analysis_indicators) >= 3


def should_conduct_deep_analysis(step_input) -> bool:
    """Determine if we should conduct deep analysis based on request complexity"""
    request = step_input.input.investment_request.lower()

    # Complex analysis keywords
    complex_keywords = [
        "portfolio",
        "diversified",
        "risk management",
        "allocation",
        "multiple",
        "several",
        "compare",
        "analysis",
        "detailed",
    ]

    return any(keyword in request for keyword in complex_keywords)


# ************* Workflow Steps *************

# Step 1: Parse investment request
parse_request_step = Step(
    name="Parse Investment Request",
    executor=parse_investment_request_step,
)

# Step 2: Market research with quality validation loop
market_research_loop = Loop(
    name="Market Research Loop",
    steps=[conduct_market_research_step],
    end_condition=check_research_quality,
    max_iterations=3,
)


# Step 3: Conditional financial analysis
def should_run_financial_analysis(step_input: StepInput) -> bool:
    """Check if we should run financial analysis based on research quality"""
    # Check if we have research content from the loop
    research_content = step_input.previous_step_content or ""
    if len(research_content) < 1000:  # Basic quality check
        return False

    content_lower = research_content.lower()
    # Check for basic financial research indicators
    return any(keyword in content_lower for keyword in ["price", "revenue", "financial", "market", "analysis"])


financial_analysis_condition = Condition(
    evaluator=should_run_financial_analysis,
    steps=[
        Loop(
            name="Financial Analysis Loop",
            steps=[financial_analysis_step],
            end_condition=check_analysis_quality,
            max_iterations=2,
        )
    ],
)

# Step 4: Conditional deep portfolio strategy
portfolio_strategy_condition = Condition(
    evaluator=should_conduct_deep_analysis,
    steps=[portfolio_strategy_step],
)

# Step 5: Basic portfolio strategy
basic_portfolio_step = Step(
    name="Basic Portfolio Strategy",
    executor=portfolio_strategy_step,
)

# ************* Workflow *************
investment_workflow = Workflow(
    name="Investment Analyst Pro",
    description="Professional investment analysis engine that evaluates market opportunities, conducts financial due diligence with adaptive research steps, and delivers strategic portfolio recommendations",
    db=get_postgres_db(),
    steps=[
        parse_request_step,
        market_research_loop,
        financial_analysis_condition,
        portfolio_strategy_condition,
        basic_portfolio_step,
    ],
    input_schema=InvestmentWorkflowInput,
    session_state={},
    debug_mode=True,
)
