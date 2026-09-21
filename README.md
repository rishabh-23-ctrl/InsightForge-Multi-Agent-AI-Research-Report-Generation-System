# InsightForge — Multi-Agent AI Research & Report Generation System

A collaborative **multi-agent AI research system** built using **LangChain**, **LangGraph**, **Groq**, and **Tavily**, designed to generate detailed and well-structured research reports through intelligent agent cooperation.

InsightForge uses multiple specialized AI agents to research a topic, evaluate the gathered evidence, generate a structured report, critique the report, and iteratively refine it until the report is approved.

The project is designed around an autonomous workflow where a **Supervisor Agent coordinates the specialized agents and controls the execution flow**.

![LangGraph Architecture](assets/research_graph.png)

*System architecture built with LangGraph illustrating multi-agent collaboration.*

---
## 🚀 Features

🤖 Multi-agent AI research workflow
🎯 Supervisor-based agent orchestration
🔎 Web research using Tavily
📊 Dedicated Evidence Analyzer Agent
✍️ Automated research report generation
🔍 Automated report critique and revision
🔄 Iterative refinement loop
📚 Source collection and tracking
📈 Research workflow activity display
📊 Report statistics
🖥️ Interactive Streamlit dashboard
📄 PDF report export
🔤 Unicode-safe PDF rendering
⚙️ Configurable maximum workflow iterations

---

## 📁 Project Structure

```text
InsightForge/
├── assets/
│   └── research_graph.png
├── .env
├── requirements.txt
├── prompts.py
├── agents.py
├── graph.py
├── visualize_graph.py
├── app.py
└── README.md
## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/rishabh-23-ctrl/InsightForge-Multi-Agent-AI-Research-Report-Generation-System.git
```

Navigate into the project:

```bash
cd InsightForge-Multi-Agent-AI-Research-Report-Generation-System
```

### 2. Create a Virtual Environment

For Python 3.11:

```bash
py -3.11 -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Replace the placeholder values with your own API keys.

### 5. Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your browser at:

```text
http://localhost:8501
```

---
## 🏗️ System Architecture

The complete InsightForge workflow is coordinated using LangGraph.

```text
Start
  |
  v
Supervisor
  |
  v
Researcher
  |
  v
Evidence Analyzer
  |
  v
Supervisor
  |
  v
Writer
  |
  v
Critiquer
  |
  v
Supervisor
  |
  +----> Approved ----> END
  |
  +----> Revision Required ----> Writer
```

### Workflow Stages

1. **Supervisor** receives the research task and determines the next agent.
2. **Researcher** searches the web and collects relevant findings and sources.
3. **Evidence Analyzer** evaluates the collected research and identifies evidence quality, gaps, contradictions, and uncertainty.
4. **Supervisor** routes the workflow toward report generation.
5. **Writer** generates the initial research report.
6. **Critiquer** reviews the report and provides feedback.
7. **Supervisor** evaluates the critique result.
8. If the report is approved, the workflow ends.
9. If revisions are required, the Writer receives the feedback and generates an improved version.
10. The revision cycle continues until the report is approved or the configured workflow limit is reached.

### Streamlit Dashboard

The Streamlit interface provides visibility into the workflow while it is running.

The dashboard displays:

- Research topic input
- Configurable workflow iterations
- Agent activity
- Supervisor decisions
- Evidence analysis
- Writer revisions
- Critiquer feedback
- Final report
- Report statistics
- Research evidence
- PDF export

---
## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| LangChain | LLM and agent integration |
| LangGraph | Multi-agent workflow orchestration |
| Groq | LLM inference |
| Tavily | Web research and source discovery |
| Streamlit | Interactive web dashboard |
| ReportLab | PDF generation |
| Markdown | Report formatting |
| python-dotenv | Environment variable management |

## Troubleshooting

### API Key Error

If the application reports that API keys are missing, verify that the `.env` file exists in the project root and contains:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

### Dependency Installation Issues

Make sure the virtual environment is activated before installing dependencies:

```bash
venv\Scripts\activate
```

Then run:

```bash
pip install -r requirements.txt
```

### Streamlit Application Does Not Start

Verify that Streamlit is installed and run:

```bash
streamlit run app.py
```

### API Rate or Usage Limits

The application depends on external APIs for LLM inference and web research. API usage limits can prevent individual agents from completing their tasks.

If an API limit is reached, wait for the provider's usage window to reset and run the workflow again.

---

## Project State

The current implementation provides an end-to-end multi-agent research workflow with:

- Supervisor orchestration
- Web research
- Evidence analysis
- Report generation
- Automated critique
- Iterative revision
- Streamlit monitoring
- Research evidence tracking
- PDF report export

The project is being developed incrementally, with additional production-oriented features planned for future phases.

---
## 🎯 Project Goal

The goal of InsightForge is to demonstrate how multiple specialized AI agents can collaborate through a structured workflow to perform research, evaluate evidence, generate reports, and iteratively improve their output.

The project focuses on combining:

- Agentic AI
- LLM engineering
- Multi-agent orchestration
- Web research
- Evidence evaluation
- Automated report generation
- Human-readable reporting
- Interactive AI applications

---

## 👨‍💻 Author

**Rishabh Tiwari**

BTech IT Student | AI/ML | LLM Engineering | Generative AI

---

## License

This project is intended for educational and portfolio purposes.

---