# CrewAI + Pomera MCP Integration

Use Pomera's 22+ text processing tools inside [CrewAI](https://crewai.com) agent workflows.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ CrewAI Python Script                                            │
│   MCPServerStdio(command="npx", args=["pomera-mcp"])            │
│         │                                                       │
│         └── spawns Pomera MCP (same as IDE does)                │
│                   ↑↓ stdio                                      │
│              Agent uses pomera_web_search, pomera_notes, etc.   │
└─────────────────────────────────────────────────────────────────┘
```

**Same pattern as IDE** - CrewAI spawns MCP server via stdio.

---

## Setup

```bash
pip install crewai crewai-tools
```

---

## Example Crews

### Research Crew

```python
# crews/research_crew.py
from crewai import Agent, Task, Crew, Process
from crewai.mcp import MCPServerStdio
import sys

# Pomera MCP server (spawned like IDE does)
pomera_mcp = MCPServerStdio(
    command="npx",
    args=["pomera-mcp"],
    env={"OPENAI_API_KEY": "your-key"}  # if needed
)

researcher = Agent(
    role="Research Analyst",
    goal="Find comprehensive information on {topic}",
    backstory="Expert researcher using multiple search engines",
    mcps=[pomera_mcp],
    verbose=True
)

analyzer = Agent(
    role="Content Analyzer", 
    goal="Synthesize research into actionable insights",
    backstory="Analyst who transforms data into insights",
    mcps=[pomera_mcp],
    verbose=True
)

search_task = Task(
    description="Search for {topic} using pomera_web_search with tavily",
    expected_output="List of relevant sources with summaries",
    agent=researcher
)

analyze_task = Task(
    description="Analyze findings using pomera_ai_tools deepreasoning",
    expected_output="Structured analysis with key insights",
    agent=analyzer,
    context=[search_task]
)

crew = Crew(
    agents=[researcher, analyzer],
    tasks=[search_task, analyze_task],
    process=Process.sequential,
    verbose=True
)

if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "AI orchestration"
    result = crew.kickoff(inputs={"topic": topic})
    print(result)
```

### Blog Crew

```python
# crews/blog_crew.py
from crewai import Agent, Task, Crew, Process
from crewai.mcp import MCPServerStdio
import sys

pomera_mcp = MCPServerStdio(command="npx", args=["pomera-mcp"])

researcher = Agent(
    role="SEO Researcher",
    goal="Find trending keywords for {niche}",
    backstory="SEO expert",
    mcps=[pomera_mcp]
)

writer = Agent(
    role="Blog Writer",
    goal="Write engaging blog posts",
    backstory="Professional blogger",
    mcps=[pomera_mcp]
)

keyword_task = Task(
    description="Find top keywords for {niche} using pomera_web_search",
    expected_output="10 keywords with search intent",
    agent=researcher
)

write_task = Task(
    description="Write 1500-word blog post targeting the keywords",
    expected_output="SEO-optimized blog post in markdown",
    agent=writer,
    context=[keyword_task],
    output_file="blog_output.md"
)

crew = Crew(agents=[researcher, writer], tasks=[keyword_task, write_task])

if __name__ == "__main__":
    niche = sys.argv[1] if len(sys.argv) > 1 else "cycling"
    crew.kickoff(inputs={"niche": niche})
    print("Blog saved to blog_output.md")
```

---

## Run From IDE

```bash
python crews/research_crew.py "AI agent frameworks"
python crews/blog_crew.py "road cycling"
```

---

## Pomera Tools Available

| Tool | Use |
|------|-----|
| `pomera_web_search` | 5 search engines |
| `pomera_ai_tools` | 11 AI providers |
| `pomera_notes` | Persistent memory |
| `pomera_read_url` | Web scraping |

See [Tools Documentation](tools/INDEX.md) for the full list.

---

## Save Results to Notes

```python
save_task = Task(
    description="Save analysis to pomera_notes with title 'Research/{topic}'",
    expected_output="Note ID confirmation",
    agent=analyzer,
    context=[analyze_task]
)
```
