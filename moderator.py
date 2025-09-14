# moderator.py (Final Secure Version)

import os
import json
import glob
from tools import get_watchlist_candidates, get_full_analysis, get_news_headlines, calculate_price_targets
from specialist_agents import create_technical_agent, create_fundamental_agent, create_sentiment_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# The API key is now handled by the main app (dashboard.py), so we don't need to import config or set the environment variable here.

def create_moderator_agent():
    """
    This function is a wrapper that returns a function to run the full two-step debate.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)

    cross_examination_prompt = PromptTemplate.from_template(
        """
        You are a Head Analyst reviewing three reports. Your only job is to find the single most critical conflict or weakness in these reports and formulate a direct, one-sentence question about it.

        Reports:
        - Technical: {technical_report}
        - Fundamental: {fundamental_report}
        - Sentiment: {sentiment_report}

        Critical Question:
        """
    )
    
    final_report_prompt = PromptTemplate.from_template(
        """
        You are the Head Analyst creating a final "Analysis Transcript" by summarizing a discussion with your team.

        **Stock:** {ticker} ({name})

        **Specialist Reports:**
        - Technical View: {technical_report}
        - Fundamental View: {fundamental_report}
        - Sentiment View: {sentiment_report}

        **Key Point of Debate (The Critical Question):** {critical_question}

        **Your Task:**
        Generate a concise "Final Analysis Transcript" that explicitly incorporates the debate. Follow this structure:

        **[Final Analysis Transcript: {ticker}]**

        **1. Specialist Summaries:**
        - **Technical View:** [Insert a 1-sentence summary of the Technical Report.]
        - **Fundamental View:** [Insert a 1-sentence summary of the Fundamental Report.]
        - **Sentiment View:** [Insert a 1-sentence summary of the Sentiment Report.]

        **2. The Debate:**
        [Start with "The key point of debate was clear:" and then state the critical question. Follow with a 1-2 sentence synthesis of how the team weighed this conflict.]

        **3. Conviction Score Calculation:**
        [Explicitly show the math for the conviction score. Assign a score out of 100 for each category before calculating the weighted total (60% Tech, 30% Fund, 10% Sent).]
        
        **4. Final Recommendation:**
        [Provide a final, one-sentence recommendation.]
        """
    )
    
    question_chain = cross_examination_prompt | llm | StrOutputParser()
    report_chain = final_report_prompt | llm | StrOutputParser()

    def run_full_process(data):
        critical_question = question_chain.invoke(data)
        data_with_question = {**data, "critical_question": critical_question}
        final_report = report_chain.invoke(data_with_question)
        return final_report
        
    return run_full_process

def run_moderator_session(stock_universe):
    """Finds candidates and runs the full agentic analysis, returning a list of reports."""
    print(f"Moderator session started for {len(stock_universe)} stocks...")
    
    watchlist = get_watchlist_candidates(stock_universe)
    final_reports = []

    if not watchlist:
        print("Moderator concludes: No interesting candidates found today.")
    else:
        print(f"Moderator found {len(watchlist)} candidate(s) to debate: {watchlist}")
        
        technical_agent = create_technical_agent()
        fundamental_agent = create_fundamental_agent()
        sentiment_agent = create_sentiment_agent()
        moderator_process = create_moderator_agent()
        
        for ticker in watchlist:
            analysis_data = get_full_analysis(ticker)
            if not analysis_data: continue
            
            tech_report = technical_agent.invoke(analysis_data)
            fund_report = fundamental_agent.invoke(analysis_data)
            headlines = get_news_headlines(ticker)
            sent_report = sentiment_agent.invoke({"ticker": ticker, "headlines": headlines})
            
            moderator_input = {
                "ticker": ticker,
                "name": analysis_data.get('name', ''),
                "technical_report": tech_report,
                "fundamental_report": fund_report,
                "sentiment_report": sent_report
            }
            
            report_text = moderator_process(moderator_input)
            
            targets = calculate_price_targets(ticker)
            sma_20 = analysis_data.get('sma_20_value', 0)
            
            final_reports.append({
                "ticker": ticker,
                "name": analysis_data.get('name', ''),
                "report": report_text,
                "targets": targets,
                "sma_20": sma_20
            })
            
    return final_reports