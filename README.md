# AnalyticoGPT

**AnalyticoGPT** is a custom AI agent built for enterprise data analytics and reporting. It blends a Streamlit frontend with a Python service layer and Google ADK/Gemini-powered AI agents to ingest CSV data, clean it, analyze it, visualize it, and generate executive reports.

---

## 🤖 Google ADK Integration

AnalyticoGPT uses Google Agent Development Kit (ADK) to build and orchestrate a multi-agent analytics workflow.

### ADK Usage
- Agent creation using `google.adk.Agent`
- Centralized agent management through `AgentRegistry`
- Task routing via `AgentRouter`
- Workflow orchestration using `google.adk.Workflow`
- Gemini-powered reasoning and report generation
- Sequential agent pipeline for end-to-end analytics

### ADK Workflow
Dataset Detection → Data Cleaning → Analysis → Visualization → Forecasting → Insights → Report Generation

### ADK Components
- `ADKConfig` – Gemini model and API configuration
- `AgentRegistry` – Agent registration and retrieval
- `AgentRouter` – Task delegation
- `AnalysisWorkflowBuilder` – Multi-agent workflow construction

---

## 🏛️ Architecture

**AnalyticoGPT follows a modular multi-tier architecture**, providing a clean separation of concerns for scalability, maintainability, and security.

---

## ☁️ SaaS 

AnalyticoGPT follows the **Software as a Service (SaaS)** model by providing centrally hosted functionality that users access through a browser interface without local installation.

---

## ✨ Features

### 📊 Data Pipeline
- CSV upload and validation  
- Automatic data cleaning and standardization  
- Numeric default-filling and null handling  
- Dataset profiling with metadata extraction  

### 🧠 AI Agent Orchestration
- Custom `root_agent` orchestrates end-to-end analysis workflow  
- Dedicated agents for dataset detection, cleaning, analysis, visualization, forecasting, insights, and reporting  
- Google Gemini / GenAI integration for executive narrative generation  

### 📈 Analytics & Visualization
- Descriptive statistics and correlation matrix generation  
- Top performer extraction  
- Heatmap and trend chart export  
- Linear forecasting and projection output  

### 📄 Reporting
- Structured PDF report generation with ReportLab  
- Executive summary, top metrics, and asset export  
- Downloadable report asset from the UI  

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit  
- **Backend:** Python  
- **AI / Agent:** Google ADK + Gemini / GenAI  
- **Data:** Pandas, NumPy  
- **Visualization:** Matplotlib, Seaborn  
- **PDF:** ReportLab  
- **Schema:** Pydantic  
- **Config:** dotenv  

---

## 🚀 Getting Started

