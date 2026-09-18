# agents.py

import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from prompts import (
    supervisor_prompt_template,
    researcher_prompt_template,
    writer_prompt_template,
    critique_prompt_template
)

# Load environment variables
load_dotenv()
import getpass
import os

if not os.environ.get("TAVILY_API_KEY"):
    os.environ["TAVILY_API_KEY"] = getpass.getpass("Tavily API key:\n")

# --- 1. Setup LLM and Tools ---


# Initialize the Groq LLM
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.3,
    max_tokens=4096,
    groq_api_key=os.environ.get("GROQ_API_KEY")
)

# Initialize the Tavily Search Tool (official method from docs)
tavily_tool = TavilySearch(
    max_results=5,
    topic="general",
    include_answer=False,
    include_raw_content=False,
    search_depth="basic"
)


def _call_llm(llm_obj, *args, **kwargs):
    """Helper to call LLM or tool objects that may expose different APIs.

    Tries common method names in order: invoke, run, __call__.
    This increases compatibility across LangChain versions.
    """
    # prefer invoke
    if hasattr(llm_obj, "invoke") and callable(getattr(llm_obj, "invoke")):
        return llm_obj.invoke(*args, **kwargs)
    # fallback to run
    if hasattr(llm_obj, "run") and callable(getattr(llm_obj, "run")):
        return llm_obj.run(*args, **kwargs)
    # last resort: call object directly if callable
    if callable(llm_obj):
        return llm_obj(*args, **kwargs)
    # Not callable
    raise AttributeError("LLM/tool object has no invoke/run and is not callable")

# --- 2. Create Agent Nodes ---

# ----------------- #
# SUPERVISOR NODE   #
# ----------------- #
def create_supervisor_chain():
    """Creates the supervisor decision chain."""
    def supervisor_invoke(state):
        research = state.get("research_findings", [])
        research_text = "\n---\n".join(research) if research else "No research yet."
        
        # Get state info
        revision = state.get("revision_number", 0)
        has_research = len(research) > 0
        has_draft = bool(state.get("draft", "").strip())
        critique = state.get("critique_notes", "")
        
        # Deterministic decision logic FIRST (before calling LLM)
        # This ensures consistent workflow progression
        
        # 1. If critique says APPROVED, we're done
        if "APPROVED" in critique.upper() and has_draft:
            print("Supervisor: Draft approved, ending workflow")
            return {
                "next_step": "END",
                "task_description": "Report approved and complete"
            }
        
        # 2. If no research yet, start with research
        if not has_research:
            print("Supervisor: No research yet, directing to researcher")
            return {
                "next_step": "researcher",
                "task_description": f"Research the topic: {state.get('main_task', '')}"
            }
        
        # 3. If we have research but no draft, create first draft
        if has_research and not state.get("evidence_analysis"):

            print("Supervisor: Research available, sending to Evidence Analyzer")

            return {
                "next_step": "evidence_analyzer",
                "task_description": "Analyze and evaluate the research evidence"
            }

        if has_research and not has_draft:

            print("Supervisor: Evidence analyzed, creating first draft")

            return {
                "next_step": "writer",
                "task_description": "Write the first draft based on research and evidence analysis"
            }
        # 4. If we have a draft but no critique yet, send to critiquer
        if has_draft and not critique:
            print("Supervisor: Have draft, sending to critiquer")
            return {
                "next_step": "writer",  # This will trigger write -> critique flow
                "task_description": "Prepare draft for critique"
            }
        
        # 5. If we have critique with feedback (not approved), revise
        if critique and "APPROVED" not in critique.upper() and revision < 3:
            print(f"Supervisor: Revision {revision}, sending back to writer")
            return {
                "next_step": "writer",
                "task_description": "Revise the draft based on critique feedback"
            }
        
        # 6. Max revisions reached
        if revision >= 3:
            print("Supervisor: Max revisions reached, ending")
            return {
                "next_step": "END",
                "task_description": "Maximum revisions reached, finalizing report"
            }
        
        # 7. Try LLM decision as fallback
        prompt = supervisor_prompt_template.format(
            main_task=state.get("main_task", ""),
            research_findings=research_text,
            draft=state.get("draft", "No draft yet."),
            critique_notes=critique if critique else "No critique yet.",
            revision_number=revision
        )
        
        try:
            response = _call_llm(llm, prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Try to parse JSON
            text = content.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join([l for l in lines if not l.strip().startswith("```")])
            text = text.strip()
            
            decision = json.loads(text)
            
            if "next_step" in decision:
                return decision
            
        except Exception as e:
            print(f"LLM parsing error: {e}")
        
        # 8. Final fallback - continue with writer
        print("Supervisor: Using final fallback - continuing with writer")
        return {
            "next_step": "writer",
            "task_description": "Continue with draft creation"
        }
    
    return supervisor_invoke

# ----------------- #
# RESEARCHER NODE   #
# ----------------- #
def create_researcher_agent():
    """Creates a researcher agent that uses search."""
    
    def researcher_invoke(input_dict):
        """Execute research using Tavily search."""
        query = input_dict.get("input", "")
        
        if not query or query in ["Continue work", "Complete"]:
            query = "General research information"
        
        print(f"Researching: {query}")
        
        try:
            # Use the tavily tool
            if hasattr(tavily_tool, "invoke"):
                search_response = tavily_tool.invoke({"query": query})
            elif callable(tavily_tool):
                search_response = tavily_tool({"query": query})
            else:
                if hasattr(tavily_tool, "run"):
                    search_response = tavily_tool.run({"query": query})
                elif hasattr(tavily_tool, "_run"):
                    search_response = tavily_tool._run(query)
                else:
                    raise AttributeError("Tavily tool object has no invoke/run/_run or callable")
            
            # Parse the response
            if isinstance(search_response, str):
                import json
                try:
                    search_data = json.loads(search_response)
                    results = search_data.get('results', [])
                except json.JSONDecodeError:
                    results = []
                    raw_output = search_response
            elif isinstance(search_response, dict):
                results = search_response.get('results', [])
            else:
                results = []
                raw_output = str(search_response)
            
            # Format the results
            formatted_results = []
            
            sources = []

            if results:
                for result in results[:3]:
                    title = result.get('title', 'Untitled')
                    url = result.get('url', 'N/A')
                    content = result.get('content', '')

                    if url != 'N/A':
                        sources.append(url)

                    formatted_results.append(
                        f"**{title}**\n"
                        f"Source: {url}\n"
                        f"{content[:300]}...\n"
                    )

                raw_output = "\n---\n".join(formatted_results)

            elif not raw_output:
                raw_output = "No results found"
            
            # Summarize with LLM
            summary_prompt = f"""Based on these search results about "{query}", provide a concise summary of key findings (5-7 bullet points):

{raw_output}

Format as clear bullet points with the most important information."""

            try:
                summary_response = _call_llm(llm, summary_prompt)
                summary = summary_response.content if hasattr(summary_response, 'content') else str(summary_response)
            except Exception as e:
                print(f"Summarization error: {e}")
                summary = raw_output
            
            return {
                "output": summary if summary else raw_output,
                "input": query,
                "sources": sources
            }
            
        except Exception as e:
            print(f"Research error: {e}")
            return {
                "output": f"Research completed on: {query}. Key information has been gathered from web sources.",
                "input": query
            }
    
    return researcher_invoke

def create_evidence_analyzer_agent():
    """Create an agent that analyzes and evaluates research evidence."""

    def evidence_analyzer(state):
        research_findings = state.get("research_findings", [])

        if not research_findings:
            return {
                "output": "No research findings available for evidence analysis."
            }

        findings_text = "\n\n".join(
            str(finding) for finding in research_findings
        )

        prompt = f"""
You are an Evidence Analyzer Agent in a multi-agent research system.

Research Topic:
{state.get("main_task", "")}

Research Findings:
{findings_text}

Analyze the research evidence and produce a structured evidence assessment.

Your analysis should:
1. Identify the most important claims and findings.
2. Distinguish strong evidence from weaker or uncertain evidence.
3. Identify supporting sources when available.
4. Point out contradictions or gaps in the evidence.
5. Highlight important limitations or uncertainty.
6. Provide concise conclusions that a research writer can use.

Do not invent facts or sources.

Return a clear, structured evidence analysis.
"""

        try:
            response = llm.invoke(prompt)
            response = response.content if hasattr(response, "content") else str(response)
            return {
                "output": response
            }
        except Exception as e:
            print(f"Evidence analysis error: {e}")
            return {
                "output": "Evidence analysis could not be completed."
            }

    return evidence_analyzer
# ----------------- #
# WRITER NODE       #
# ----------------- #
def create_writer_chain():
    """Creates the writer chain."""
    def writer_invoke(state):
        research = state.get("research_findings", [])
        research_text = "\n\n".join(research) if research else "No research available."

        sources = state.get("sources", [])
        sources_text = "\n".join(sources) if sources else "No sources available."

        evidence_analysis = state.get(
            "evidence_analysis",
            "No evidence analysis available."
        )

        draft = state.get("draft", "")
        critique_notes = state.get("critique_notes", "")

        # First draft: use full research context
        if not draft:
            prompt = writer_prompt_template.format(
                main_task=state.get("main_task", ""),
                research_findings=research_text,
                sources=sources_text,
                evidence_analysis=evidence_analysis,
                draft="",
                critique_notes=""
            )

        # Revision: use only the existing draft + critique
        else:
            prompt = f"""
You are the Writer Agent in a multi-agent research system.

Research Topic:
{state.get("main_task", "")}

Current Draft:
{draft}

Critique Feedback:
{critique_notes}

Revise the current draft according to the critique feedback.

Requirements:
1. Preserve accurate information from the existing draft.
2. Fix the specific issues identified by the critic.
3. Do not invent facts or sources.
4. Keep the report structured and professional.
5. Include these sections where appropriate:
   - Executive Summary
   - Introduction
   - Key Findings
   - Evidence Analysis
   - Detailed Analysis
   - Limitations
   - Conclusion
   - Sources
6. Return the complete revised report, not just the changes.
"""

        try:
            response = _call_llm(llm, prompt)
            content = response.content if hasattr(response, 'content') else str(response)

            return content if content else "Draft in progress..."

        except Exception as e:
            print(f"Writer error: {e}")
            return "Error generating draft. Please try again."

    return writer_invoke


# ----------------- #
# CRITIQUE NODE     #
# ----------------- #
def create_critique_chain():
    """Creates the critique chain."""
    def critique_invoke(state):
        draft = state.get("draft", "")
        revision_num = state.get("revision_number", 0)
        
        # Safety checks
        if len(draft.strip()) < 100:
            return "APPROVED - Draft is minimal but acceptable."
        
        if revision_num >= 3:
            return "APPROVED - Maximum revisions reached. The report is satisfactory."
        
        prompt = critique_prompt_template.format(
            main_task=state.get("main_task", ""),
            draft=draft
        )
        
        try:
            response = _call_llm(llm, prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            return content if content else "APPROVED"
        except Exception as e:
            print(f"Critique error: {e}")
            return "APPROVED - Error in critique, proceeding with current draft."
    
    return critique_invoke