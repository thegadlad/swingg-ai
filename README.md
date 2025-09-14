# swingg-ai
A Stateful and Conversational Multi-Agent Trading Ecosystem
Executive Summary
Swingg AI is an advanced, autonomous system designed to solve the two biggest challenges in swing trading: emotional decision-making and information overload. It employs a team of specialized agents (technical, fundamental and sentimental) that work together to scan the Indian stock market, identify high-potential trading opportunities and present them in a clear, actionable report. The system moves beyond simple screening by facilitating a dynamic, AI-powered back and forth "debate" for each stock, providing a level of qualitative analysis that mirrors the process of a professional investment committee to carefully pick the next right investment for you.

How It Works: The 2-Stage Process
The agent operates in two distinct stages to ensure both efficiency and depth of analysis:
Stage 1: Wide-Net Quantitative Screen
The system first scans a broad universe of over 160 stocks against a robust, 6-point "Quality Momentum" strategy. This quantitative filter analyzes size, profitability, financial risk, trend, and momentum to distill the entire market down to a small, manageable watchlist of 2-5 high-potential candidates.
Stage 2: Deep-Dive Agentic Debate
The small list of candidates is then passed to the Moderator Agent. This agent orchestrates a "debate" between three specialists:
The Technical Agent: Analyzes price action, charts, and momentum.
The Fundamental Agent: Assesses the company's financial health.
The Sentiment Agent: Reviews recent news to gauge market narrative.
The Moderator facilitates a multi-round discussion, challenges the agents' findings, and synthesizes their diverse viewpoints into a final, comprehensive report.


Key Features
Multi-Agent System: Utilizes a team of distinct AI agents with specialized roles, orchestrated by a Head Analyst (Moderator) to provide a 360-degree view.
AI-Powered Debate: Generates a dynamic, conversational "Final Analysis Transcript" for each stock, making the reasoning process transparent and easy to understand.
Data-Driven Strategy: Employs a sophisticated 6-rule filter combining fundamental health checks (Profit Margin, Debt-to-Equity) with technical triggers (SMA Trend, RSI, Volume Breakout).
Complete Trade Plan: The final report includes a full Exit Strategy with calculated price targets and a dynamic, rule-based stop-loss for comprehensive trade management.
Performance Tracking: Includes a daily Validation Report that re-evaluates the previous day's watchlist, informing the user if signals have strengthened, weakened, or remain intact.
Interactive Dashboard: Features a clean, professional, and user-friendly web interface built with Streamlit for easy interaction and data visualization.

Technology Stack
Backend & Core Logic: Python
Agentic Framework: LangChain
Large Language Model (LLM): Google Gemini 1.5 Flash
User Interface: Streamlit
Data & Analysis: Pandas, yfinance, ta
External APIs: NewsAPI

How to Run Locally
Clone the repository from GitHub.
Install the required libraries: pip install -r requirements.txt
Create a folder named .streamlit and a file inside it named secrets.toml.
Add your API keys to the secrets.toml file.
Run the application from your terminal: streamlit run dashboard.py

Try Swingg-ai now : https://swingg-ai.streamlit.app/
