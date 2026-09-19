# 🔍 InsightForge — Multi-Agent AI Research & Report Generation System

InsightForge is a collaborative **multi-agent AI research system** built with **LangChain**, **LangGraph**, **Groq**, and **Tavily**.

It uses a team of specialized AI agents to research a topic, evaluate the gathered evidence, generate a structured report, critique the report, and iteratively refine it until the report is approved.

The project is designed around an autonomous workflow where a **Supervisor Agent coordinates the specialized agents and controls the execution flow**.

![LangGraph Architecture](assets/research_graph.png)

*Multi-agent research workflow built with LangGraph.*

---

## 🚀 Features

- 🤖 Multi-agent AI research workflow
- 🎯 Supervisor-based agent orchestration
- 🔎 Web research using Tavily
- 📊 Dedicated Evidence Analyzer Agent
- ✍️ Automated research report generation
- 🔍 Automated report critique and revision
- 🔄 Iterative refinement loop
- 📚 Source collection and tracking
- 📈 Research workflow activity display
- 📊 Report statistics
- 🖥️ Interactive Streamlit dashboard
- 📄 PDF report export
- 🔤 Unicode-safe PDF rendering
- ⚙️ Configurable maximum workflow iterations

---

## 🏗️ System Architecture

InsightForge currently uses five specialized agents:

```text
                    ┌─────────────────┐
                    │    Supervisor   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    Researcher   │
                    └────────┬────────┘
                             │
                             ▼
                 ┌──────────────────────┐
                 │  Evidence Analyzer   │
                 └──────────┬───────────┘
                            │
                            ▼
                    ┌─────────────────┐
                    │    Supervisor   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │      Writer     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    Critiquer    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    Supervisor   │
                    └────────┬────────┘
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
                END                  Writer
                                      │
                                      └──► Revision Loop
Workflow
Supervisor
    ↓
Researcher
    ↓
Evidence Analyzer
    ↓
Supervisor
    ↓
Writer
    ↓
Critiquer
    ↓
Supervisor
    ↓
END / Writer

The Supervisor dynamically determines the next step based on the current workflow state.

If the Critiquer requests improvements, the report is sent back to the Writer for revision.

🤖 Agents
1. 🎯 Supervisor Agent

The Supervisor coordinates the entire research workflow.

Responsibilities:

Determines which agent should execute next
Routes tasks between agents
Tracks workflow state
Controls the revision loop
Determines when the report is ready to finish

The Supervisor can route execution to:

Researcher
Evidence Analyzer
Writer
END
2. 🔎 Researcher Agent

The Researcher gathers information from the web using Tavily.

Responsibilities:

Searches for relevant information
Collects research findings
Extracts source URLs
Produces concise research summaries
Provides evidence for downstream agents

The Researcher returns both:

Research Findings
Sources
3. 📊 Evidence Analyzer Agent

The Evidence Analyzer evaluates the quality and reliability of the collected research.

Responsibilities:

Identifies important claims
Distinguishes stronger evidence from weaker evidence
Identifies supporting sources
Detects contradictions and evidence gaps
Highlights limitations and uncertainty
Produces an evidence assessment for the Writer

This additional analysis layer helps prevent the Writer from simply summarizing search results without evaluating their evidentiary strength.

4. ✍️ Writer Agent

The Writer generates the final research report using:

Research findings
Collected sources
Evidence analysis
Critiquer feedback

Reports are structured around sections such as:

Executive Summary
Introduction
Key Findings
Evidence Analysis
Detailed Analysis
Limitations
Conclusion
Sources

When the Critiquer requests revisions, the Writer generates a complete revised version of the report.

5. 🔍 Critiquer Agent

The Critiquer evaluates the generated report.

Responsibilities:

Reviews report quality
Identifies weaknesses
Checks structure and clarity
Provides revision feedback
Approves the report when requirements are satisfied

The Critiquer controls whether the workflow should finish or continue through another revision cycle.

🖥️ Streamlit Dashboard

InsightForge includes an interactive Streamlit dashboard for running the research workflow.

The dashboard provides:

Research Configuration

Users can enter a research topic and configure the maximum number of workflow iterations.

Autonomous Research Pipeline

The interface displays the five-agent pipeline:

Supervisor
Researcher
Evidence Analyzer
Writer
Critiquer
Agent Activity

The dashboard displays live workflow activity including:

Current agent
Workflow step
Supervisor decisions
Research completion
Evidence analysis
Writer revisions
Critiquer feedback/approval
Report Statistics

The completed report displays:

Number of revisions
Number of research sources/findings
Word count
Character count
📄 PDF Export

After the research workflow completes, the final report can be downloaded as a PDF.

The PDF is generated directly from the final report content and supports Markdown-style formatting including:

Headings
Bold text
Bullet lists
Numbered lists
Tables
Source sections

The PDF generator also uses a Unicode-capable font so characters such as:

–
—
’
•

render correctly instead of appearing as unsupported-character squares.

The exported PDF uses the same final_draft that is displayed in the dashboard, keeping the final report as the single source of truth.

📁 Project Structure
InsightForge/
│
├── assets/
│   └── research_graph.png
│
├── .env
├── requirements.txt
├── prompts.py
├── agents.py
├── graph.py
├── visualize_graph.py
├── app.py
└── README.md
File Responsibilities
File	Purpose
app.py	Streamlit dashboard and PDF export
agents.py	AI agents, LLM configuration, Tavily research
graph.py	LangGraph workflow and state management
prompts.py	Agent prompt templates
visualize_graph.py	Generates the LangGraph workflow visualization
requirements.txt	Python dependencies
assets/	Architecture and graph visualizations
.env	API keys and environment configuration
🛠️ Technology Stack
Technology	Purpose
Python	Core programming language
LangChain	LLM and agent framework
LangGraph	Multi-agent workflow orchestration
Groq	LLM inference
openai/gpt-oss-20b	Current Groq model
Tavily	Web research and search
Streamlit	Interactive web dashboard
ReportLab	PDF generation
Python-Markdown	Markdown processing
Graphviz	Optional workflow visualization
⚙️ Installation
Prerequisites
Python 3.11+
pip
Git
Groq API key
Tavily API key
Graphviz (optional, only required for graph visualization)
1. Clone the Repository
git clone https://github.com/rishabh-23-ctrl/InsightForge-Multi-Agent-AI-Research-Report-Generation-System.git

Navigate into the project:

cd InsightForge-Multi-Agent-AI-Research-Report-Generation-System
2. Create a Virtual Environment
Windows
py -3.11 -m venv venv

Activate it:

venv\Scripts\activate
macOS / Linux
python3.11 -m venv venv
source venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
🔑 Environment Configuration

Create a .env file in the project root:

GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
Groq API Key

Create a Groq API key from:

https://console.groq.com/

Tavily API Key

Create a Tavily API key from:

https://tavily.com/

Never commit your .env file or expose your API keys publicly.

▶️ Running the Application

Start the Streamlit application:

streamlit run app.py


Enter a research topic and click:

🚀 Start Research

InsightForge will then execute the multi-agent workflow.

📊 Generate Workflow Visualization

The project includes a script for generating the LangGraph architecture visualization.

Run:

python visualize_graph.py

The generated visualization is saved inside:

assets/

Graphviz is optional and is not required to run the Streamlit application.

🔄 Research Workflow Example

For a topic such as:

Impact of Generative AI on Software Development

the system follows this process:

1. Supervisor
   ↓
2. Researcher
   ↓
3. Evidence Analyzer
   ↓
4. Supervisor
   ↓
5. Writer
   ↓
6. Critiquer
   ↓
7. Supervisor
   ↓
8. END or Writer

If revisions are requested:

Writer
   ↓
Critiquer
   ↓
Supervisor
   ↓
Writer

This continues until the Critiquer approves the report or the configured workflow iteration limit is reached.

🧠 State Management

The LangGraph workflow maintains shared state containing information such as:

main_task
research_findings
sources
evidence_analysis
draft
critique_notes
revision_number
next_step
current_sub_task

This shared state allows the specialized agents to collaborate while maintaining context throughout the workflow.

📋 Report Output

The generated report is designed to contain:

Executive Summary
Introduction
Key Findings
Evidence Analysis
Detailed Analysis
Limitations
Conclusion
Sources

The final report is displayed directly in the Streamlit dashboard.

It can also be exported as a PDF using:

📄 Download Research Report (PDF)


🎯 Project Goal

InsightForge aims to demonstrate how multiple specialized AI agents can collaborate through a structured workflow rather than relying on a single LLM call.

The system separates:

Research
   ↓
Evidence Evaluation
   ↓
Report Generation
   ↓
Quality Review
   ↓
Revision

This architecture makes the research process more modular, observable, and extensible.

👨‍💻 Author

Rishabh Tiwari

BTech Information Technology Student

GitHub:

https://github.com/rishabh-23-ctrl