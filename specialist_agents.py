# specialist_agents.py (Final Corrected and Secure Version)

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Note: The API key is now correctly handled only in dashboard.py

def create_technical_agent():
    """Creates a LangChain-powered Technical Agent using LCEL."""
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
    
    prompt = PromptTemplate.from_template(
        """
        You are a master technical analyst for the Indian stock market. Your sole purpose is to provide a concise, expert analysis of a stock's technical health based on the structured data provided.

        Analyze the following data for the stock ticker {ticker}:
        - 5-day SMA is above 20-day SMA (Trend filter): {passes_sma}
        - RSI is below 70 (Momentum filter): {passes_rsi}
        - Current volume is greater than 3x the 15-day average (Volume filter): {passes_volume}

        Based on this data, provide a 2-3 sentence summary of the technical picture.
        Start with a clear "Bullish," "Bearish," or "Neutral" stance.
        Focus only on the technicals. Mention if the stock is a good candidate that is simply awaiting a volume trigger.
        Do not provide financial advice. Your Analysis:
        """
    )
    
    return prompt | llm | StrOutputParser()

def create_fundamental_agent():
    """Creates a LangChain-powered Fundamental Agent using LCEL."""
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
    
    prompt = PromptTemplate.from_template(
        """
        You are a meticulous fundamental analyst. Your task is to summarize a company's financial health based on pre-calculated data points.

        **Stock Ticker:** {ticker}

        **Analysis Data:**
        - Meets our size criteria (Market Cap between ₹1k Cr & ₹20k Cr): `{passes_mc}`
        - Is profitable (Profit Margin > 5%): `{passes_pm}`
        - Has a low debt profile (Debt-to-Equity < 1.0): `{passes_de}`

        **Your Task:**
        Based *only* on the data above, provide a 2-3 sentence summary of the company's fundamental health.
        Start by stating if the fundamentals are "Solid," "Acceptable," or "Weak."
        Briefly explain your reasoning. Do not provide financial advice.

        **Fundamental Health Summary:**
        """
    )
    
    return prompt | llm | StrOutputParser()

def create_sentiment_agent():
    """Creates a LangChain-powered Sentiment Agent using LCEL."""
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
    
    prompt = PromptTemplate.from_template(
        """
        You are a market sentiment analyst. Your sole purpose is to analyze news headlines and determine the overall market sentiment for a stock.

        Review the following recent headlines for the stock {ticker}:
        {headlines}

        Based *only* on these headlines, provide a 1-2 sentence summary of the current market sentiment.
        Start with a clear "Positive," "Negative," or "Neutral" sentiment rating.
        If no headlines are found, state that the sentiment is Neutral due to a lack of recent news.
        Do not provide financial advice. Your Analysis:
        """
    )

    return prompt | llm | StrOutputParser()