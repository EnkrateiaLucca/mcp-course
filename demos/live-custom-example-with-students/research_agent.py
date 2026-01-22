#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "claude-agent-sdk>=0.1.21",
#     "arxiv",
# ]
# ///

"""
Research agent with ability to:
- Search through the arxiv database (with a custom mcp server tool!)
- Summarize the information from any paper retrieved
- Create custom quizzes that we can test ourselves with!
"""

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, tool, create_sdk_mcp_server
from typing import Any
import arxiv
import asyncio


# arxiv mcp server search tool
@tool(
    "search_arxiv",
    "Search academic papers on arXiv by query",
    {"query": str, "max_results": int}
)
async def search_arxiv(args: dict[str, Any]) -> dict[str, Any]:
    """
    Search arXiv database for academic papers.
    Returns paper titles, authors, summaries, and PDF links.
    """
    query = args["query"]
    max_results = args.get("max_results", 5)  # Default to 5 results

    # Create arXiv search client
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )

    # Collect results
    papers = []
    for result in search.results():
        paper_info = {
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "published": result.published.strftime("%Y-%m-%d"),
            "summary": result.summary,
            "pdf_url": result.pdf_url,
            "arxiv_id": result.entry_id.split("/")[-1]
        }
        papers.append(paper_info)

    # Format response for the agent
    if papers:
        response_text = f"Found {len(papers)} papers for query '{query}':\n\n"
        for i, paper in enumerate(papers, 1):
            response_text += f"{i}. **{paper['title']}**\n"
            response_text += f"   Authors: {', '.join(paper['authors'][:3])}"
            if len(paper['authors']) > 3:
                response_text += f" et al."
            response_text += f"\n   Published: {paper['published']}\n"
            response_text += f"   arXiv ID: {paper['arxiv_id']}\n"
            response_text += f"   Summary: {paper['summary'][:200]}...\n"
            response_text += f"   PDF: {paper['pdf_url']}\n\n"
    else:
        response_text = f"No papers found for query '{query}'"

    return {
        "content": [{
            "type": "text",
            "text": response_text
        }]
    }

@tool(
    "create_quiz_file",
    "Create a JSON quiz file from questions, alternatives, and correct answers",
    {"quiz_data": dict, "filename": str}
)
async def create_quiz_file(args: dict[str, Any]) -> dict[str, Any]:
    """
    Create a JSON quiz file that can be loaded into a quiz application.

    Expected quiz_data format:
    {
        "title": "Quiz Title",
        "description": "Quiz description (optional)",
        "questions": [
            {
                "question": "What is...?",
                "alternatives": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": 0,  # Index of correct answer (0-based)
                "explanation": "Why this answer is correct (optional)"
            }
        ]
    }

    Example:
    {
        "title": "Quantum Computing Quiz",
        "description": "Test your knowledge of quantum computing concepts",
        "questions": [
            {
                "question": "What is quantum superposition?",
                "alternatives": [
                    "A quantum bit being in multiple states simultaneously",
                    "The ability to process classical bits faster",
                    "A type of quantum error",
                    "A measurement technique"
                ],
                "correct_answer": 0,
                "explanation": "Superposition allows qubits to exist in multiple states at once"
            }
        ]
    }
    """
    import json
    from pathlib import Path

    quiz_data = args["quiz_data"]
    filename = args.get("filename", "quiz.json")

    # Ensure filename ends with .json
    if not filename.endswith(".json"):
        filename += ".json"

    # Create full path in the current directory
    quiz_path = Path.cwd() / filename

    # Validate quiz data structure
    if "questions" not in quiz_data:
        return {
            "content": [{
                "type": "text",
                "text": "Error: quiz_data must contain 'questions' key"
            }],
            "is_error": True
        }

    # Write the quiz to a JSON file
    try:
        with open(quiz_path, 'w', encoding='utf-8') as f:
            json.dump(quiz_data, f, indent=2, ensure_ascii=False)

        num_questions = len(quiz_data.get("questions", []))
        title = quiz_data.get("title", "Untitled Quiz")

        response_text = f"✅ Quiz file created successfully!\n\n"
        response_text += f"📁 File: {quiz_path}\n"
        response_text += f"📝 Title: {title}\n"
        response_text += f"❓ Questions: {num_questions}\n\n"
        response_text += f"The quiz file is ready to be loaded into a quiz application."

        return {
            "content": [{
                "type": "text",
                "text": response_text
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error creating quiz file: {str(e)}"
            }],
            "is_error": True
        } 

# Create MCP server with arXiv search and quiz creation tools
arxiv_server = create_sdk_mcp_server(
    name="arxiv_research",
    version="1.0.0",
    tools=[search_arxiv, create_quiz_file]
)


async def main():
    """Main function to run the research agent"""

    # Get user query
    user_query = input("Enter your research topic (e.g., 'quantum computing', 'neural networks'): ")

    # Create agent options with arXiv MCP server
    options = ClaudeAgentOptions(
        mcp_servers={"arxiv_research": arxiv_server},
        allowed_tools=[
            "mcp__arxiv_research__search_arxiv",
            "mcp__arxiv_research__create_quiz_file"
        ]
    )

    # Initialize Claude SDK client with options
    print(f"\n🔍 Searching arXiv for papers about '{user_query}'...\n")

    async with ClaudeSDKClient(options=options) as client:
        # Query the agent with enhanced prompt
        await client.query(
            f"""Search arXiv for papers about: {user_query}.

            After finding papers, create a quiz with 5 questions based on the paper summaries.
            Each question should have 4 multiple choice alternatives, with one correct answer.
            Save the quiz to a file named '{user_query.replace(' ', '_')}_quiz.json'.

            The quiz should test understanding of:
            - Key concepts from the papers
            - Research methods or approaches
            - Important findings or contributions
            """
        )

        # Process the response
        async for message in client.receive_response():
            if hasattr(message, 'result'):
                print(message.result)


if __name__ == "__main__":
    asyncio.run(main())