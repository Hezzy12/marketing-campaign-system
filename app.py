import os
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from functools import lru_cache
import gradio as gr
from pydantic import BaseModel
from duckduckgo_search import DDGS
from praisonai import PraisonAI
from praisonai_tools import BaseTool

# Data Models
class CampaignParameters(BaseModel):
    target_industry: str
    campaign_focus: str 
    budget_range: float
    target_audience: Optional[str]
    timeline: Optional[str]
    kpis: Optional[List[str]]

class CampaignOutput(BaseModel):
    market_analysis: str
    strategy: str
    campaign_concepts: List[Dict[str, str]]
    creative_assets: List[Dict[str, str]]
    timeline: Dict[str, Any]
    budget_allocation: Dict[str, float]
    kpi_targets: Dict[str, Any]
    execution_metrics: Dict[str, Any]

# Enhanced Search Tool
class EnhancedSearchTool(BaseTool):
    name: str = "EnhancedSearchTool"
    description: str = "Advanced internet search with caching and rate limiting"
    
    def __init__(self):
        self.cache = {}
        self.last_request_time = {}
        self.rate_limit = 1.0  # seconds between requests
        
    @lru_cache(maxsize=100)
    async def _run(self, query: str) -> List[Dict]:
        """Execute search with rate limiting and caching"""
        now = datetime.now()
        if query in self.last_request_time:
            time_diff = (now - self.last_request_time[query]).total_seconds()
            if time_diff < self.rate_limit:
                await asyncio.sleep(self.rate_limit - time_diff)
        
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(
                    keywords=query,
                    region='wt-wt',
                    safesearch='moderate',
                    max_results=5
                ))
            self.cache[query] = results
            self.last_request_time[query] = now
            return results
        except Exception as e:
            print(f"Search error: {str(e)}")
            return self.cache.get(query, [])

class MarketingCampaignSystem:
    def __init__(self):
        self.agent_yaml = """
        framework: "crewai"
        topic: "Enterprise Marketing Campaign Development"
        
        agent_groups:
          research_team:
            agents:
              market_analyst:
                role: "Senior Market Analyst"
                backstory: "Expert in B2B tech market analysis with 15 years experience"
                goal: "Provide comprehensive market insights and competitor analysis"
                tools: ["EnhancedSearchTool"]
              
              audience_researcher:
                role: "Audience Research Specialist"
                backstory: "Specialist in B2B audience behavior and demographics"
                goal: "Define and analyze target audience segments"
                tools: ["EnhancedSearchTool"]
          
          strategy_team:
            agents:
              marketing_strategist:
                role: "Chief Marketing Strategist"
                backstory: "Veteran B2B marketing strategist with enterprise focus"
                goal: "Develop comprehensive marketing strategy and campaign framework"
                tools: ["EnhancedSearchTool"]
              
              budget_planner:
                role: "Campaign Budget Specialist"
                backstory: "Expert in enterprise marketing budget optimization"
                goal: "Create detailed budget allocation and ROI projections"
          
          creative_team:
            agents:
              content_director:
                role: "Creative Content Director"
                backstory: "Award-winning B2B content strategist"
                goal: "Design compelling campaign narratives and content strategy"
              
              creative_designer:
                role: "Senior Creative Designer"
                backstory: "Experienced in enterprise brand visual communication"
                goal: "Create engaging visual concepts and design guidelines"
        
        workflows:
          market_research:
            sequence: ["market_analyst", "audience_researcher"]
            output: "Comprehensive market and audience analysis"
          
          strategy_development:
            sequence: ["marketing_strategist", "budget_planner"]
            output: "Strategic campaign plan with budget allocation"
          
          creative_development:
            sequence: ["content_director", "creative_designer"]
            output: "Campaign creative concepts and assets"
        """
        
        self.praisonai = PraisonAI(
            agent_yaml=self.agent_yaml,
            tools=[EnhancedSearchTool],
            cache_results=True,
            parallel_execution=True
        )

    async def execute_campaign(self, params: CampaignParameters) -> CampaignOutput:
        """Execute full marketing campaign development process"""
        try:
            context = params.dict()
            result = await self.praisonai.run_async(context=context)
            
            # Process and structure the output
            output = CampaignOutput(
                market_analysis=result.tasks_output[0].raw,
                strategy=result.tasks_output[1].raw,
                campaign_concepts=self._parse_campaign_concepts(result.tasks_output[2].raw),
                creative_assets=self._parse_creative_assets(result.tasks_output[3].raw),
                timeline=self._generate_timeline(result.tasks_output[4].raw),
                budget_allocation=self._parse_budget(result.tasks_output[5].raw),
                kpi_targets=self._parse_kpis(result.tasks_output[6].raw),
                execution_metrics={
                    "token_usage": result.token_usage,
                    "execution_time": result.execution_time,
                    "cost_estimate": result.cost_estimate
                }
            )
            
            return output
            
        except Exception as e:
            raise Exception(f"Campaign execution failed: {str(e)}")

    def _parse_campaign_concepts(self, raw_concepts: str) -> List[Dict[str, str]]:
        """Parse campaign concepts from raw output"""
        # Implementation for parsing concepts
        pass

    def _parse_creative_assets(self, raw_assets: str) -> List[Dict[str, str]]:
        """Parse creative assets from raw output"""
        # Implementation for parsing assets
        pass

    def _generate_timeline(self, raw_timeline: str) -> Dict[str, Any]:
        """Generate structured timeline"""
        # Implementation for timeline generation
        pass

    def _parse_budget(self, raw_budget: str) -> Dict[str, float]:
        """Parse budget allocation"""
        # Implementation for budget parsing
        pass

    def _parse_kpis(self, raw_kpis: str) -> Dict[str, Any]:
        """Parse KPI targets"""
        # Implementation for KPI parsing
        pass

# Gradio Interface
def create_gradio_interface():
    """Create professional Gradio interface"""
    
    def execute_campaign_sync(
        industry: str,
        focus: str,
        budget: float,
        audience: str,
        timeline: str,
        kpis: str
    ) -> str:
        params = CampaignParameters(
            target_industry=industry,
            campaign_focus=focus,
            budget_range=budget,
            target_audience=audience,
            timeline=timeline,
            kpis=kpis.split(',') if kpis else None
        )
        
        system = MarketingCampaignSystem()
        result = asyncio.run(system.execute_campaign(params))
        
        # Format output for display
        return f"""
        # Marketing Campaign Development Report
        
        ## Market Analysis
        {result.market_analysis}
        
        ## Strategy
        {result.strategy}
        
        ## Campaign Concepts
        {result.campaign_concepts}
        
        ## Creative Assets
        {result.creative_assets}
        
        ## Timeline
        {result.timeline}
        
        ## Budget Allocation
        {result.budget_allocation}
        
        ## KPI Targets
        {result.kpi_targets}
        
        ## Execution Metrics
        - Token Usage: {result.execution_metrics['token_usage']}
        - Execution Time: {result.execution_metrics['execution_time']}s
        - Estimated Cost: ${result.execution_metrics['cost_estimate']}
        """

    iface = gr.Interface(
        fn=execute_campaign_sync,
        inputs=[
            gr.Dropdown(
                choices=["Technology", "Healthcare", "Finance", "Manufacturing", "Retail"],
                label="Target Industry"
            ),
            gr.Radio(
                choices=["Brand Awareness", "Lead Generation", "Product Launch", "Thought Leadership"],
                label="Campaign Focus"
            ),
            gr.Slider(
                minimum=10000,
                maximum=1000000,
                step=10000,
                label="Budget Range ($)"
            ),
            gr.Textbox(
                label="Target Audience",
                placeholder="e.g., Enterprise CTOs, IT Directors"
            ),
            gr.Dropdown(
                choices=["3 months", "6 months", "12 months"],
                label="Campaign Timeline"
            ),
            gr.Textbox(
                label="KPIs (comma-separated)",
                placeholder="e.g., leads generated, engagement rate, conversion rate"
            )
        ],
        outputs=gr.Markdown(label="Campaign Development Output"),
        title="Enterprise Marketing Campaign Development System",
        description="""
        Professional marketing campaign development powered by AI agent teams.
        Input your campaign parameters to receive a comprehensive marketing strategy and execution plan.
        """,
        theme="default",
        css=".gradio-container {background-color: #f7f7f7;}"
    )
    
    return iface

if __name__ == "__main__":
    # Set up environment
    os.environ["OPENAI_API_KEY"] = "your-api-key"  # Replace with your API key
    
    # Launch Gradio interface
    iface = create_gradio_interface()
    iface.launch(share=True) 