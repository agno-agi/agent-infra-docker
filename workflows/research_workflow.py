from textwrap import dedent
from typing import List

from agno.agent.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.wikipedia import WikipediaTools
from agno.workflow.condition import Condition
from agno.workflow.loop import Loop
from agno.workflow.step import Step
from agno.workflow.types import StepInput, StepOutput, WorkflowExecutionInput
from agno.workflow.workflow import Workflow
from pydantic import BaseModel, Field

from app.models import OPENAI_MODEL_ID
from db.session import get_postgres_db


# ************* Input Schema *************
class ResearchTopic(BaseModel):
    """Comprehensive research request with specific requirements"""

    research_request: str = Field(
        description="Complete research request including topic, scope, and specific questions to answer"
    )


# ************* Agents *************
research_coordinator = Agent(
    name="Research Coordinator",
    model=OpenAIChat(id=OPENAI_MODEL_ID),
    tools=[DuckDuckGoTools(), WikipediaTools()],
    description=dedent("""\
        Expert research coordinator specializing in comprehensive information gathering,
        source validation, and research planning across multiple domains.
    """),
    instructions=dedent("""\
        You are a professional research coordinator with expertise in systematic information gathering.

        **Your Mission:**
        Conduct comprehensive research using advanced search techniques and multiple sources.

        **Research Strategy:**
        1. **Parse Research Request** - Extract key topics, questions, and scope
        2. **Multi-Source Research** - Use DuckDuckGo and Wikipedia strategically:
        
        **DuckDuckGo Research (Supplementary)** - Use for broader coverage:
           - Real-time news and current events
           - Popular media and public discourse
           - Diverse perspectives and opinions
           - Technical documentation and guides
           
        **Wikipedia Research (Foundation)** - Use for background and context:
           - Historical context and background information
           - Definitions and fundamental concepts
           - Comprehensive overviews and summaries
           - Cross-references and related topics

        **Research Areas:**
        - **Background & Context**: Historical development, key concepts, definitions
        - **Current State**: Latest developments, recent studies, current trends
        - **Expert Perspectives**: Professional opinions, analysis, and insights
        - **Multiple Viewpoints**: Different perspectives, debates, and controversies
        - **Future Outlook**: Predictions, trends, and emerging developments

        **Quality Standards:**
        - Include specific facts, data, and statistics
        - Cite recent sources (within last 2 years preferred)
        - Provide balanced coverage of different viewpoints
        - Include at least 8-10 credible source URLs
        - Cross-validate information across multiple sources

        **Reference Collection:**
        - **Capture all source URLs** from your research
        - **Save links** to studies, reports, articles, and expert analysis
        - **Note the source type** and publication date for each reference
        - **Organize sources** by category (academic, news, expert analysis, etc.)

        Always provide comprehensive, well-sourced research with clear references.
    """),
    db=get_postgres_db(),
    markdown=True,
    debug_mode=True,
)

content_analyst = Agent(
    name="Content Analyst",
    model=OpenAIChat(id=OPENAI_MODEL_ID),
    tools=[DuckDuckGoTools()],
    description=dedent("""\
        Expert content analyst specializing in information synthesis,
        analysis, and insight generation from research findings.
    """),
    instructions=dedent("""\
        You are a professional content analyst focused on synthesizing research into actionable insights.

        **Your Role:**
        Analyze research findings and generate comprehensive, well-structured analysis and insights.

        **Analysis Tasks:**
        1. **Content Synthesis** - Combine information from multiple sources
        2. **Trend Analysis** - Identify patterns, trends, and emerging themes
        3. **Critical Analysis** - Evaluate credibility, identify gaps, and assess implications
        4. **Insight Generation** - Draw meaningful conclusions and actionable insights
        5. **Comparative Analysis** - Compare different perspectives and approaches

        **Analysis Framework:**
        1. **Key Findings** - Main discoveries and important information
        2. **Trend Analysis** - Patterns, developments, and emerging themes
        3. **Expert Insights** - Professional opinions and analysis
        4. **Implications** - What this means for different stakeholders
        5. **Future Outlook** - Predictions and potential developments
        6. **Recommendations** - Actionable next steps and considerations

        **Output Format:**
        - **Executive Summary**: Key findings and insights overview
        - **Detailed Analysis**: In-depth examination of findings
        - **Trend Assessment**: Current and emerging patterns
        - **Expert Perspectives**: Professional opinions and analysis
        - **Implications & Impact**: Significance and consequences
        - **Recommendations**: Actionable insights and next steps
        - **References**: Comprehensive source list with categorization

        Focus on generating actionable insights and clear, well-supported conclusions.
    """),
    db=get_postgres_db(),
    markdown=True,
    debug_mode=True,
)

report_writer = Agent(
    name="Research Report Writer",
    model=OpenAIChat(id=OPENAI_MODEL_ID),
    description=dedent("""\
        Expert research report writer specializing in creating comprehensive,
        professional research reports and documentation.
    """),
    instructions=dedent("""\
        You are a professional research report writer focused on creating comprehensive, well-structured reports.

        **Your Role:**
        Transform research findings and analysis into polished, professional research reports.

        **Report Structure:**
        1. **Executive Summary** - Key findings and conclusions overview
        2. **Introduction** - Research scope, objectives, and methodology
        3. **Background & Context** - Historical context and foundational information
        4. **Current Landscape** - Present state and recent developments
        5. **Key Findings** - Main discoveries and important insights
        6. **Analysis & Insights** - Deep analysis and expert perspectives
        7. **Trends & Patterns** - Emerging themes and future outlook
        8. **Implications** - Significance for different stakeholders
        9. **Recommendations** - Actionable next steps and considerations
        10. **Conclusion** - Summary and final thoughts
        11. **References & Sources** - Comprehensive bibliography

        **Writing Standards:**
        - Professional, clear, and engaging writing style
        - Logical flow and smooth transitions between sections
        - Proper citations and source attribution
        - Data-driven insights with supporting evidence
        - Balanced presentation of different perspectives
        - Actionable recommendations and clear conclusions

        **Quality Criteria:**
        - Comprehensive coverage of the research topic
        - Well-organized structure with clear headings
        - Professional formatting and presentation
        - Accurate citations and source references
        - Clear, actionable insights and recommendations

        Create reports that are informative, professional, and actionable for decision-makers.
    """),
    db=get_postgres_db(),
    markdown=True,
    debug_mode=True,
)


# ************* Step Functions *************
async def comprehensive_research_step(execution_input: WorkflowExecutionInput) -> StepOutput:
    """Conduct comprehensive research using multiple sources"""
    search_input = execution_input.input

    research_prompt = f"""
    Conduct comprehensive research based on this request:
    
    **Research Request**: {search_input.research_request}
    
    Your task is to gather comprehensive information using advanced search techniques.
    
    **Multi-Source Research Strategy:**
    1. **Parse the request** to understand scope, key topics, and specific questions
    2. **Execute systematic research** using all available tools:
       - **DuckDuckGo Search**: For current news, diverse perspectives, and real-time information
       - **Wikipedia Research**: For background context, definitions, and comprehensive overviews
    
    **Research Coverage:**
    - **Background & Context**: Historical development, key concepts, definitions
    - **Current State**: Latest developments, recent studies, current trends
    - **Expert Perspectives**: Professional opinions, analysis, and insights
    - **Multiple Viewpoints**: Different perspectives, debates, and controversies
    - **Future Outlook**: Predictions, trends, and emerging developments
    
    **Quality Standards:**
    - Include specific facts, data, and statistics
    - Cite recent sources (within last 2 years preferred)
    - Provide balanced coverage of different viewpoints
    - Include at least 8-10 credible source URLs
    - Cross-validate information across multiple sources
    
    **Reference Collection:**
    - **Capture all source URLs** from your research
    - **Save links** to studies, reports, articles, and expert analysis
    - **Note the source type** and publication date for each reference
    - **Organize sources** by category (academic, news, expert analysis, etc.)
    
    Focus on comprehensive, well-sourced research with clear references.
    """

    result = await research_coordinator.arun(research_prompt)

    return StepOutput(
        content=f"""
            # Comprehensive Research Findings

            ## Research Request
            {search_input.research_request}

            ## Research Results
            {result.content}
        """.strip(),
        success=True,
    )


async def content_analysis_step(execution_input: WorkflowExecutionInput) -> StepOutput:
    """Analyze research content and generate insights"""
    search_input = execution_input.input
    research_content = execution_input.get_step_content("Comprehensive Research")

    analysis_prompt = f"""
    Analyze the research findings and generate comprehensive insights:
    
    **Original Research Request**: {search_input.research_request}
    
    **Research Findings**:
    {research_content}
    
    Please provide:
    
    1. **Content Synthesis**: Combine information from multiple sources
    2. **Trend Analysis**: Identify patterns, trends, and emerging themes
    3. **Critical Analysis**: Evaluate credibility, identify gaps, and assess implications
    4. **Insight Generation**: Draw meaningful conclusions and actionable insights
    5. **Comparative Analysis**: Compare different perspectives and approaches
    6. **Expert Perspectives**: Professional opinions and analysis
    7. **Future Outlook**: Predictions and potential developments
    8. **References**: Comprehensive source list with categorization
    
    Use DuckDuckGo search to find additional expert analysis and professional insights to supplement the findings.
    Focus on generating actionable insights and clear, well-supported conclusions.
    """

    result = await content_analyst.arun(analysis_prompt)

    return StepOutput(
        content=f"""
            # Content Analysis & Insights

            ## Research Request
            {search_input.research_request}

            ## Analysis Results
            {result.content}

        """.strip(),
        success=True,
    )


async def report_writing_step(execution_input: WorkflowExecutionInput) -> StepOutput:
    """Create comprehensive research report"""
    search_input = execution_input.input
    research_content = execution_input.get_step_content("Comprehensive Research")
    analysis_content = execution_input.get_step_content("Content Analysis")

    report_prompt = f"""
    Create a comprehensive research report based on all findings and analysis:
    
    **Original Research Request**: {search_input.research_request}
    
    **Research Findings**:
    {research_content}
    
    **Content Analysis**:
    {analysis_content}
    
    Please create a professional research report with:
    
    1. **Executive Summary** - Key findings and conclusions overview
    2. **Introduction** - Research scope, objectives, and methodology
    3. **Background & Context** - Historical context and foundational information
    4. **Current Landscape** - Present state and recent developments
    5. **Key Findings** - Main discoveries and important insights
    6. **Analysis & Insights** - Deep analysis and expert perspectives
    7. **Trends & Patterns** - Emerging themes and future outlook
    8. **Implications** - Significance for different stakeholders
    9. **Recommendations** - Actionable next steps and considerations
    10. **Conclusion** - Summary and final thoughts
    11. **References & Sources** - Comprehensive bibliography
    
    **Writing Standards:**
    - Professional, clear, and engaging writing style
    - Logical flow and smooth transitions between sections
    - Proper citations and source attribution
    - Data-driven insights with supporting evidence
    - Balanced presentation of different perspectives
    - Actionable recommendations and clear conclusions
    
    Create a report that is informative, professional, and actionable for decision-makers.
    """

    result = await report_writer.arun(report_prompt)

    return StepOutput(
        content=f"""
            # Professional Research Report

            ## Research Request
            {search_input.research_request}

            ## Final Report
            {result.content}

            ---
            *Professional research report by Research Report Writer*

            ## Disclaimer
            This research report is for informational purposes only. Please verify critical information 
            and consult with relevant experts before making important decisions based on this research.
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
        "http" in content or "source" in content,  # URLs/references
        len(content) > 2000,  # Substantial content
        "research" in content or "study" in content,
        "expert" in content or "analysis" in content,
        content.count("http") >= 5,  # Multiple sources
    ]

    # Need at least 4 out of 5 quality indicators
    return sum(quality_indicators) >= 4


def check_analysis_quality(outputs: List[StepOutput]) -> bool:
    """Check if content analysis quality is sufficient"""
    if not outputs:
        return False

    latest_output = outputs[-1]
    content = latest_output.content.lower()

    # Analysis quality indicators
    analysis_indicators = [
        "insight" in content or "analysis" in content,
        "trend" in content or "pattern" in content,
        "implication" in content or "impact" in content,
        "recommendation" in content or "conclusion" in content,
    ]

    # Need at least 3 out of 4 analysis indicators
    return sum(analysis_indicators) >= 3


def should_conduct_deep_analysis(step_input) -> bool:
    """Determine if we should conduct deep analysis based on request complexity"""
    request = step_input.input.research_request.lower()

    # Complex analysis keywords
    complex_keywords = [
        "analysis",
        "comprehensive",
        "detailed",
        "compare",
        "evaluate",
        "assess",
        "implications",
        "trends",
        "future",
        "impact",
    ]

    return any(keyword in request for keyword in complex_keywords)


# ************* Workflow Steps *************

# Step 1: Comprehensive research step
research_loop = Loop(
    name="Comprehensive Research Loop",
    steps=[comprehensive_research_step],
    end_condition=check_research_quality,
    max_iterations=3,
)


# Step 2: Conditional content analysis
def should_run_content_analysis(step_input: StepInput) -> bool:
    """Check if we should run content analysis based on research quality"""
    # Check if we have research content from the loop
    research_content = step_input.previous_step_content or ""
    if len(research_content) < 2000:  # Basic quality check
        return False

    content_lower = research_content.lower()
    # Check for basic research quality indicators
    return any(keyword in content_lower for keyword in ["research", "study", "analysis", "expert", "source"])


analysis_condition = Condition(
    evaluator=should_run_content_analysis,
    steps=[
        Loop(
            name="Content Analysis Loop",
            steps=[content_analysis_step],
            end_condition=check_analysis_quality,
            max_iterations=2,
        )
    ],
)

# Step 3: Conditional comprehensive report
comprehensive_report_condition = Condition(
    evaluator=should_conduct_deep_analysis,
    steps=[report_writing_step],
)

# Step 4: Basic report
basic_report_step = Step(
    name="Basic Research Report",
    executor=report_writing_step,
)

# ************* Workflow *************
research_workflow = Workflow(
    name="Advanced Research Analyst",
    description="AI-powered research analyst that conducts multi-source investigations, performs quality-validated analysis, and generates professional reports with insights and citations",
    db=get_postgres_db(),
    steps=[
        research_loop,
        analysis_condition,
        comprehensive_report_condition,
        basic_report_step,
    ],
    input_schema=ResearchTopic,
    session_state={},
    debug_mode=True,
)
