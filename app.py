# app.py

import streamlit as st
import os
from dotenv import load_dotenv
from graph import app
import time

from io import BytesIO

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_LEFT
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# from reportlab.lib.units import inch
# Load environment variables
load_dotenv()

def generate_pdf(report_text):
    """Generate a formatted PDF from the final research report."""
    import re
    import html
    import markdown
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        KeepTogether
    )
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import (
        getSampleStyleSheet,
        ParagraphStyle
    )
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.units import mm
    from io import BytesIO

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()
    # Register a Unicode-capable font so characters like
    # –, —, ’ and • render correctly in the PDF.
    pdfmetrics.registerFont(
        TTFont("ArialUnicode", "C:/Windows/Fonts/arial.ttf")
    )

    pdfmetrics.registerFont(
        TTFont("ArialUnicodeBold", "C:/Windows/Fonts/arialbd.ttf")
    )

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="ArialUnicodeBold",
        fontSize=20,
        leading=25,
        spaceAfter=16,
        alignment=TA_LEFT
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontName="ArialUnicodeBold",
        fontSize=14,
        leading=18,
        spaceBefore=12,
        spaceAfter=8
    )

    subheading_style = ParagraphStyle(
        "ReportSubHeading",
        parent=styles["Heading3"],
        fontName="ArialUnicodeBold",
        fontSize=12,
        leading=16,
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontName="ArialUnicode",
        fontSize=10,
        leading=14,
        spaceAfter=7
    )

    bullet_style = ParagraphStyle(
        "ReportBullet",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-7,
        spaceAfter=5
    )

    story = []

    lines = report_text.splitlines()
    i = 0

    while i < len(lines):

        line = lines[i].strip()

        # Empty line
        if not line:
            story.append(Spacer(1, 5))
            i += 1
            continue

        # Markdown table
        if (
            "|" in line
            and i + 1 < len(lines)
            and "|" in lines[i + 1]
            and re.match(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$", lines[i + 1])
        ):
            table_data = []

            header = [
                cell.strip()
                for cell in line.strip("|").split("|")
            ]

            table_data.append(header)

            i += 2

            while i < len(lines) and "|" in lines[i]:
                row = [
                    cell.strip()
                    for cell in lines[i].strip("|").split("|")
                ]

                table_data.append(row)
                i += 1

            formatted_table = []

            for row_index, row in enumerate(table_data):
                formatted_row = []

                for cell in row:
                    cell_html = markdown.markdown(
                        cell,
                        extensions=["extra"]
                    )

                    cell_html = cell_html.replace(
                        "<p>", ""
                    ).replace(
                        "</p>", ""
                    )

                    if row_index == 0:
                        cell_style = ParagraphStyle(
                            "TableHeader",
                            parent=body_style,
                            fontName="ArialUnicodeBold",
                            fontSize=9,
                            leading=12
                        )
                    else:
                        cell_style = ParagraphStyle(
                            "TableCell",
                            parent=body_style,
                            fontSize=8.5,
                            leading=11
                        )

                    formatted_row.append(
                        Paragraph(cell_html, cell_style)
                    )

                formatted_table.append(formatted_row)

            available_width = A4[0] - 36 * mm

            column_count = len(table_data[0])

            table = Table(
                formatted_table,
                colWidths=[
                    available_width / column_count
                ] * column_count,
                repeatRows=1,
                hAlign="LEFT"
            )

            table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ])
            )

            story.append(
                KeepTogether(table)
            )

            story.append(Spacer(1, 8))
            continue

        # H1
        if line.startswith("# "):
            text = line[2:]
            html_text = markdown.markdown(text)

            story.append(
                Paragraph(
                    html_text,
                    title_style
                )
            )

        # H2
        elif line.startswith("## "):
            text = line[3:]
            html_text = markdown.markdown(text)

            story.append(
                Paragraph(
                    html_text,
                    heading_style
                )
            )

        # H3
        elif line.startswith("### "):
            text = line[4:]
            html_text = markdown.markdown(text)

            story.append(
                Paragraph(
                    html_text,
                    subheading_style
                )
            )

        # Bullet list
        elif line.startswith("- ") or line.startswith("* "):
            text = line[2:]
            html_text = markdown.markdown(text)

            story.append(
                Paragraph(
                    f"• {html_text}",
                    bullet_style
                )
            )

        # Numbered list
        elif re.match(r"^\d+\.\s+", line):
            match = re.match(r"^(\d+)\.\s+(.*)", line)

            number = match.group(1)
            text = match.group(2)

            html_text = markdown.markdown(text)

            story.append(
                Paragraph(
                    f"{number}. {html_text}",
                    body_style
                )
            )

        # Normal paragraph
        else:
            html_text = markdown.markdown(
                line,
                extensions=["extra"]
            )

            html_text = html_text.replace(
                "<p>", ""
            ).replace(
                "</p>", ""
            )

            story.append(
                Paragraph(
                    html_text,
                    body_style
                )
            )

        i += 1

    doc.build(story)

    buffer.seek(0)

    return buffer.getvalue()
# --- Page Configuration ---
st.set_page_config(
    page_title="InsightForge | AI Research",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom UI Styling ---
st.markdown("""
<style>

    /* Main application */
    .stApp {
        background-color: #f8fafc;
    }

    /* Main content width */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
    }

    [data-testid="stSidebar"] * {
        color: #e2e8f0;
    }

    /* Sidebar divider */
    [data-testid="stSidebar"] hr {
        border-color: #334155;
    }

    /* Main title */
    .insightforge-title {
        font-size: 3.2rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0.2rem;
    }

    .insightforge-gradient {
        background: linear-gradient(
            90deg,
            #2563eb,
            #7c3aed
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .insightforge-subtitle {
        font-size: 1.15rem;
        color: #64748b;
        margin-bottom: 2rem;
    }

    /* Workflow card */
    .workflow-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin: 1rem 0 2rem 0;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }

    .workflow-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 1rem;
    }

    .workflow {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
        flex-wrap: wrap;
    }

    .agent {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.7rem 1rem;
        text-align: center;
        min-width: 130px;
        font-weight: 600;
        color: #1e293b;
    }

    .arrow {
        color: #94a3b8;
        font-size: 1.2rem;
    }

    /* Section headings */
    h1, h2, h3 {
        color: #0f172a;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        min-height: 3rem;
    }

    /* Text input */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #cbd5e1;
        min-height: 3rem;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
    }

    /* Footer */
    .insightforge-footer {
        text-align: center;
        color: #94a3b8;
        padding: 1.5rem 0;
        font-size: 0.9rem;
    }

</style>
""", unsafe_allow_html=True)

# --- Check for API Keys ---
def check_api_keys():
    """Check if required API keys are present."""
    groq_key = os.environ.get("GROQ_API_KEY")
    tavily_key = os.environ.get("TAVILY_API_KEY")

    if not groq_key or not tavily_key:
        st.error(
            "🚨 API keys not found! Please set "
            "GROQ_API_KEY and TAVILY_API_KEY in your .env file."
        )
        return False

    st.success("✅ API keys loaded successfully.")
    return True


# --- Header ---
st.markdown("# 🔍 InsightForge")

st.markdown(
    "### Multi-Agent AI Research & Report Generation System"
)

st.markdown(
    "Research a topic and let a team of specialized AI agents "
    "**research, analyze evidence, write, and refine** your report."
)


# --- Workflow Overview ---
st.markdown("### ⚡ Autonomous Research Pipeline")

workflow_cols = st.columns(5)

agents = [
    ("🎯", "Supervisor", "Coordinates"),
    ("🔎", "Researcher", "Collects evidence"),
    ("📊", "Evidence Analyzer", "Evaluates evidence"),
    ("✍️", "Writer", "Generates report"),
    ("🔍", "Critiquer", "Reviews quality")
]

for col, (icon, name, description) in zip(workflow_cols, agents):
    with col:
        st.info(
            f"{icon} **{name}**\n\n"
            f"{description}"
        )

st.caption(
    "🔄 The Supervisor coordinates the pipeline and routes the report "
    "through revision cycles until the Critiquer approves it."
)

# --- Check API Keys ---
if not check_api_keys():
    st.stop()


st.divider()

# --- Main Application ---

st.markdown("## 🚀 Start Your Research")

st.markdown(
    "Enter a topic and let InsightForge research, evaluate evidence, "
    "generate a report, and refine it automatically."
)

topic = st.text_input(
    "Research Topic",
    placeholder="e.g., Impact of quantum computing on cybersecurity",
    key="topic_input"
)

st.markdown("")

# --- Sidebar ---
with st.sidebar:

    # Branding
    st.markdown("## 🔍 InsightForge")

    st.caption("AI Research Intelligence")

    st.divider()

    # Configuration
    st.markdown("### ⚙️ Configuration")

    max_iterations = st.slider(
        "Max Workflow Iterations",
        min_value=5,
        max_value=25,
        value=15,
        help="Maximum number of agent interactions"
    )

    st.divider()

    # Research Pipeline
    st.markdown("### 🔄 Research Pipeline")

    st.markdown("""
    🟢 **Supervisor**

    🔵 **Researcher**

    🟣 **Evidence Analyzer**

    🟡 **Writer**

    🔴 **Critiquer**
    """)

    st.divider()

    # About
    st.markdown("### ℹ️ About")

    st.caption(
        "InsightForge uses specialized AI agents "
        "to research, analyze, write, and refine reports."
    )

# Start button
if st.button("🚀 Start Research", type="primary", use_container_width=True):
    if not topic:
        st.error("⚠️ Please enter a research topic.")
    else:
        # Define the initial state
        initial_state = {
            "main_task": topic,
            "research_findings": [],
            "draft": "",
            "critique_notes": "",
            "revision_number": 0,
            "next_step": "",
            "current_sub_task": ""
        }
        
        # Configuration
        config = {"recursion_limit": max_iterations}
        
        st.info("🤖 Agents are starting their work...")
        
        # Create containers for live updates
        st.markdown("**Workflow Progress**")
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        # Container for step-by-step progress
        progress_container = st.container()
        
        final_state = None
        step_count = 0
        all_states = []  # Keep track of all states
        
        try:
            # Stream the graph execution
            with progress_container:
                st.markdown("### 🔄 Agent Activity")
                st.caption("Live updates from the InsightForge research pipeline")
                
                for step in app.stream(initial_state, config=config):
                    step_count += 1
                    progress_bar.progress(min(step_count / max_iterations, 1.0))
                    
                    # Get node name and output
                    node_name = list(step.keys())[0]
                    node_output = step[node_name]
                    
                    # Store the complete state
                    all_states.append((node_name, node_output))
                    
                    # Display node output with expandable previews
                    with st.container():

                        col1, col2 = st.columns([4, 1])

                        with col1:
                            st.markdown(
                                f"**🤖 {node_name.replace('_', ' ').title()}**"
                            )

                        with col2:
                            st.caption(f"Step {step_count}")

                        
                        if node_name == "supervisor":
                            next_step = node_output.get("next_step", "N/A")
                            task = node_output.get("current_sub_task", "N/A")

                            st.info(
                                f"**Decision:** {next_step}\n\n"
                                f"**Task:** {task}"
    )
                        
                        elif node_name == "researcher":
                            findings = node_output.get('research_findings', [])
                            if findings:
                                latest = findings[-1]
                                st.success("✓ Research completed")
                                
                                # Preview with "Show More" button
                                preview_length = 300
                                if len(latest) > preview_length:
                                    st.markdown("**Research Preview:**")
                                    st.info(latest[:preview_length] + "...")
                                    
                                    # Unique key for each expander
                                    with st.expander(f"📖 Show Full Research (Step {step_count})"):
                                        st.markdown(latest)
                                else:
                                    st.markdown("**Research:**")
                                    st.info(latest)
                        
                        elif node_name == "evidence_analyzer":
                            analysis = node_output.get("evidence_analysis", "")

                            if analysis:
                                st.success("📊 Evidence analysis completed")

                                preview_length = 350

                                if len(analysis) > preview_length:
                                    st.markdown("**Evidence Assessment Preview:**")
                                    st.info(analysis[:preview_length] + "...")

                                    with st.expander(
                                        f"📖 Show Full Evidence Analysis (Step {step_count})"
                                    ):
                                        st.markdown(analysis)
                                else:
                                    st.markdown("**Evidence Assessment:**")
                                    st.info(analysis)
                        elif node_name == "writer":
                            draft = node_output.get('draft', '')
                            revision = node_output.get('revision_number', 0)
                            st.success(f"✓ Draft {revision} generated ({len(draft)} chars)")
                            
                            # Preview with "Show More" button
                            preview_length = 400
                            if len(draft) > preview_length:
                                st.markdown("**Draft Preview:**")
                                st.info(draft[:preview_length] + "...")
                                
                                # Unique key for each expander
                                with st.expander(f"📖 Show Full Draft (Step {step_count})"):
                                    st.markdown(draft)
                            else:
                                st.markdown("**Draft:**")
                                st.info(draft)
                        
                        elif node_name == "critiquer":
                            critique = node_output.get('critique_notes', '')
                            if "APPROVED" in critique.upper():
                                st.success("✅ Report approved by Critiquer")
                            else:
                                st.warning("📝 Revisions requested by Critiquer")
                            
                            # Preview with "Show More" button
                            preview_length = 300
                            if len(critique) > preview_length:
                                st.markdown("**Critique Preview:**")
                                st.info(critique[:preview_length] + "...")
                                
                                # Unique key for each expander
                                with st.expander(f"📖 Show Full Critique (Step {step_count})"):
                                    st.markdown(critique)
                            else:
                                st.markdown("**Critique:**")
                                st.info(critique)
                        
                        st.divider()
                    
                    time.sleep(0.3)
            
            # Update status when done
            status_placeholder.success("✅ Research Complete!")
            progress_bar.progress(1.0)
            # Reconstruct final state from all streamed node outputs
            final_state = {}

            for node_name, state in all_states:
                if isinstance(state, dict):
                    final_state.update(state)
            # Debug: Print final state info
            print(f"Final state type: {type(final_state)}")
            print(f"Final state keys: {final_state.keys() if isinstance(final_state, dict) else 'Not a dict'}")
            print(f"Draft exists: {bool(final_state.get('draft') if isinstance(final_state, dict) else False)}")
            print(f"Sources collected: {len(final_state.get('sources', []))}")
            print("Sources:")
            for source in final_state.get("sources", []):
                print(f"- {source}")
            print(f"Draft length: {len(final_state.get('draft', '')) if isinstance(final_state, dict) else 0}")
            
        except Exception as e:
            status_placeholder.error("❌ Error occurred")
            st.error(f"An error occurred: {str(e)}")
            st.exception(e)
            final_state = None
        
        # Display final report - IMPROVED LOGIC
        st.divider()
        
        # Reconstruct useful final state from all node outputs
        final_state = {}

        for node_name, state in all_states:
            if isinstance(state, dict):
                final_state.update(state)
                
        # Try to get the draft from final_state
        final_draft = None
        if final_state and isinstance(final_state, dict):
            final_draft = final_state.get("draft", "")
        
        # If no draft in final_state, search through all states
        if not final_draft or len(final_draft.strip()) < 50:
            print("Searching for draft in all states...")
            for node_name, state in reversed(all_states):
                if isinstance(state, dict) and state.get("draft"):
                    draft_candidate = state.get("draft", "")
                    if len(draft_candidate.strip()) > 50:
                        final_draft = draft_candidate
                        final_state = state
                        print(f"Found draft in {node_name} state")
                        break
        
        if final_draft and len(final_draft.strip()) > 50:
            st.header("📄 Final Research Report")
            
            # Display report in a nice container
            with st.container(border=True):
                st.markdown(final_draft)
            
            st.divider()
            
            # Display metadata
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Report Statistics")

                revision_count = (
                    final_state.get("revision_number", 0)
                    if isinstance(final_state, dict)
                    else 0
                )

                research_count = (
                    len(final_state.get("research_findings", []))
                    if isinstance(final_state, dict)
                    else 0
                )

                word_count = len(final_draft.split())
                character_count = len(final_draft)

                metric1, metric2, metric3, metric4 = st.columns(4)

                with metric1:
                    st.metric("Revisions", revision_count)

                with metric2:
                    st.metric("Sources", research_count)

                with metric3:
                    st.metric("Words", f"{word_count:,}")

                with metric4:
                    st.metric("Characters", f"{character_count:,}")
            
            with col2:
                st.subheader("🔍 Research Findings")
                if isinstance(final_state, dict) and final_state.get("research_findings"):
                    # Use expander here (safe, outside of workflow)
                    with st.expander("View all research data", expanded=False):
                        for idx, finding in enumerate(final_state.get("research_findings", []), 1):
                            st.markdown(f"**Finding {idx}:**")
                            st.write(finding)
                            if idx < len(final_state.get("research_findings", [])):
                                st.divider()
                else:
                    st.info("No research findings available")
            
            # Download button
            st.markdown("### 📥 Export Report")
            st.caption("Save your completed research report for later use.")

            pdf_data = generate_pdf(final_draft)

            st.download_button(
                label="📄 Download Research Report (PDF)",
                data=pdf_data,
                file_name=f"research_report_{topic.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.error("❌ No report was generated. Please try again.")
            if final_state:
                with st.expander("🔍 Debug: View Final State"):
                    st.json(final_state if isinstance(final_state, dict) else {"error": "State is not a dictionary"})

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Powered by LangChain, LangGraph, Groq & Tavily</p>
</div>
""", unsafe_allow_html=True)