
Skip to content

    lastmile-ai
    mcp-eval

Repository navigation

    Code
    Issues20 (20)
    Pull requests3 (3)
    Agents
    Actions
    Projects

Owner avatar
mcp-eval
Public

lastmile-ai/mcp-eval
Name	Last commit message
	Last commit date
MahtabSarvmailipetersonbill64
MahtabSarvmaili
and
petersonbill64
Add benchmarking examples and configurations (#45)
7c0f4d1
 · 
Sep 10, 2025
.github
	
Fix test dir in MCP-Eval CI workflow (#48)
	
Sep 6, 2025
.vscode
	
Update settings.json to include remote url for mcpeval schema
	
Aug 14, 2025
benchmarks
	
Add benchmarking examples and configurations (#45)
	
Sep 10, 2025
docs
	
Add action to generate and upload MCP-Eval badges from JSON report (#34)
	
Sep 6, 2025
examples
	
Add action to generate and upload MCP-Eval badges from JSON report (#34)
	
Sep 6, 2025
schema
	
Many fixes to CLI, generation script, schema, and Makefile
	
Aug 27, 2025
scripts
	
Add action to generate and upload MCP-Eval badges from JSON report (#34)
	
Sep 6, 2025
src/mcp_eval
	
Ensure setup and teardown are file-scoped (#33)
	
Sep 4, 2025
tests
	
Ensure setup and teardown are file-scoped (#33)
	
Sep 4, 2025
.coveragerc
	
mcp-eval final body join (#8)
	
Aug 26, 2025
.gitattributes
	
Create .gitattributes to ignore generated files
	
Aug 28, 2025
.gitignore
	
mcp-eval final body join (#8)
	
Aug 26, 2025
.pre-commit-config.yaml
	
mcp-eval final body join (#8)
	
Aug 26, 2025
.python-version
	
v0.1 implementation
	
Jul 5, 2025
CHANGELOG.md
	
mcp-eval final body join (#8)
	
Aug 26, 2025
CODE_OF_CONDUCT.md
	
mcp-eval final body join (#8)
	
Aug 26, 2025
CONTRIBUTING.md
	
mcp-eval final body join (#8)
	
Aug 26, 2025
GUIDE.md
	
More checkpoint
	
Aug 17, 2025
LICENSE
	
Initial commit
	
May 19, 2025
Makefile
	
Many fixes to CLI, generation script, schema, and Makefile
	
Aug 27, 2025
README.md
	
Docs updates
	
Aug 27, 2025
SECURITY.md
	
mcp-eval final body join (#8)
	
Aug 26, 2025
SUPPORT.md
	
mcp-eval final body join (#8)
	
Aug 26, 2025
pyproject.toml
	
Add benchmarking examples and configurations (#45)
	
Sep 10, 2025
pytest.ini
	
mcp-eval final body join (#8)
	
Aug 26, 2025
uv.lock
	
Add benchmarking examples and configurations (#45)
	
Sep 10, 2025
Repository files navigation

    README
    Code of conduct

mcp-eval

Documentation PyPI License

mcp-eval is an evaluation framework for testing Model Context Protocol (MCP) servers and the agents that use them. Unlike traditional testing approaches that mock interactions or test components in isolation, mcp-eval exercises your complete system in the environment it actually runs in: an LLM/agent calling real MCP tools.
Why mcp-eval exists
The challenge

As AI agents become more sophisticated and MCP servers proliferate, teams face critical questions:

    For MCP server developers: "Will my server handle real agent requests correctly? What about edge cases?"
    For agent developers: "Is my agent using tools effectively? Does it recover from errors?"
    For both: "How do we measure quality, performance, and reliability before production?"

The solution

mcp-eval addresses these challenges by providing:

    Real environment testing - No mocks, actual agent-to-server communication
    Full observability - OpenTelemetry traces capture detailed agent execution to run evals over
    Rich assertion library - From tool checks to sophisticated path analysis
    Multiple test styles - Choose what fits your workflow -- pytest, datasets or @task decorators
    Language agnostic - Test MCP servers written in any language

How it works

    Model Context Protocol standardizes how applications provide context to large language models (LLMs). Think of MCP like a USB-C port for AI applications.

    mcp-eval ensures your MCP servers, and agents built with them, work reliably in production.

    Test any MCP server: It doesn't matter what language your MCP server is written in - Python, TypeScript, Go, Rust, Java, or any other. As long as it implements the MCP protocol, mcp-eval can test it!

Installation

We recommend using uv to install mcp-eval as a global tool:

# Install mcp-eval globally (for CLI)
uv tool install mcpevals

# Add mcp-eval dependency to your project
uv add mcpevals

# Initialize your project (interactive setup)
mcp-eval init

# Add your MCP server to test
mcp-eval server add

# Auto-generate tests with an LLM
mcp-eval generate

# Run tests
mcp-eval run tests/

Alternatively with pip:

# Install mcp-eval
pip install mcpevals

# Initialize your project
mcp-eval init

# Add your MCP server
mcp-eval server add

# Run tests
mcp-eval run tests/

Requirements:

    Python 3.10+
    Any MCP server to test

📚 Ready to dive deeper? Follow our complete Getting Started Guide →
What mcp-eval Does for You

    Test MCP Servers: Ensure your MCP servers respond correctly to agent requests and handle edge cases gracefully
    Evaluate Agents: Measure how effectively agents use tools, follow instructions, and recover from errors
    Track Performance: Monitor latency, token usage, cost, and success rates with OpenTelemetry-backed metrics
    Assert Quality: Use structural checks, LLM judges, and path efficiency validators to ensure high quality

Why Teams Choose mcp-eval

    Production-ready: Built on OpenTelemetry for enterprise-grade observability
    Multiple test styles: Choose between decorators, pytest, or dataset-driven testing
    Rich assertions: Content checks, tool verification, performance gates, and LLM judges
    CI/CD friendly: GitHub Actions support, JSON/HTML reports, and regression detection
    Language agnostic: Test MCP servers written in any language
    Built on mcp-agent: Leverage sophisticated agent patterns from Anthropic's Building Effective Agents

Quick Example

from mcp_eval import task, Expect

@task("Verify fetch server works correctly")
async def test_fetch(agent, session):
    # Ask the agent to fetch a webpage
    response = await agent.generate_str("Fetch https://example.com and summarize it")
    
    # Assert the right tool was called
    await session.assert_that(Expect.tools.was_called("fetch"))
    
    # Verify the content is correct
    await session.assert_that(
        Expect.content.contains("Example Domain"), 
        response=response
    )
    
    # Check performance
    await session.assert_that(Expect.performance.response_time_under(5000))

Run with:

mcp-eval run test_fetch.py -v

Core Features
Test Organization

MCP-Eval supports multiple testing patterns:

Decorator-based tests: Simple async functions with @task decorator

@task("Test name")
async def test_something(agent, session):
    # agent: TestAgent instance connected to MCP servers
    # session: TestSession for assertions and metrics
    pass

Pytest integration: Use familiar pytest patterns

@pytest.mark.asyncio
async def test_with_pytest(mcp_agent):
    response = await mcp_agent.generate_str("...")
    assert "expected" in response

Dataset testing: Systematic evaluation across multiple cases

from mcp_eval import Dataset, Case

dataset = Dataset(
    name="Calculator Tests",
    cases=[
        Case(inputs="2+2", expected="4", evaluators=[...]),
        Case(inputs="10*5", expected="50", evaluators=[...])
    ]
)

Assertion System

All assertions use the Expect API with specialized namespaces:

Content assertions: Verify response text

Expect.content.contains("text")           # Substring check
Expect.content.regex(r"\d+ items?")       # Regex pattern

Tool assertions: Verify MCP tool usage

Expect.tools.was_called("tool_name")      # Tool was invoked
Expect.tools.count("dangerous", 0)        # Tool was not invoked  
Expect.tools.sequence(["read", "write"])  # Exact sequence
Expect.tools.success_rate(min_rate=0.95)  # Success threshold
Expect.tools.output_matches(               # Check tool output
    tool_name="fetch",
    expected_output="data",
    match_type="contains"
)

Performance assertions: Verify efficiency metrics

Expect.performance.response_time_under(5000)      # Max latency (ms)
Expect.performance.max_iterations(3)              # Max LLM calls

LLM judge assertions: Quality evaluation using LLMs

Expect.judge.llm(
    rubric="Evaluate for accuracy and clarity",
    min_score=0.8,
    model="claude-3-opus-20240229"  # Optional: specific judge model
)

Expect.judge.multi_criteria([
    EvaluationCriterion(name="accuracy", weight=3.0, min_score=0.9),
    EvaluationCriterion(name="clarity", weight=1.0, min_score=0.7)
])

Path assertions: Verify execution sequences

Expect.path.efficiency(
    expected_tool_sequence=["validate", "process", "save"],
    tool_usage_limits={"validate": 1, "process": 1},
    allow_extra_steps=0,
    penalize_backtracking=True
)

Metrics Collection

Every test automatically collects:

    Performance metrics: Response time, token usage, cost per interaction
    Tool metrics: Call counts, success rates, error patterns, latencies
    Conversation metrics: Number of turns, total duration, cumulative costs
    Trace data: Complete OTEL spans for debugging and analysis

Test Lifecycle

from mcp_eval import setup, teardown, task

@setup
def prepare():
    """Run before all tests"""
    initialize_test_data()

@teardown  
def cleanup():
    """Run after all tests"""
    cleanup_test_data()

@task("Test with lifecycle")
async def test_something(agent, session):
    # Test implementation
    pass

Complete Example

Testing an MCP server that provides web fetching and filesystem operations:

# test_document_processor.py
from mcp_eval import task, setup, teardown, Expect
from mcp_eval.session import TestSession
from pathlib import Path

@setup
def prepare_test_environment():
    """Create test directory and files."""
    test_dir = Path("test_output")
    test_dir.mkdir(exist_ok=True)
    return test_dir

@task("Test document processing workflow")
async def test_document_workflow(agent: TestAgent, session: TestSession):
    """Test fetching a document, processing it, and saving results."""
    
    # Step 1: Fetch document
    fetch_response = await agent.generate_str(
        "Fetch the content from https://example.com/api/document.json"
    )
    
    # Verify fetch was successful
    await session.assert_that(
        Expect.tools.was_called("fetch"),
        name="fetch_called"
    )
    
    # Step 2: Process and save
    save_response = await agent.generate_str(
        "Parse the JSON and save a summary to test_output/summary.md"
    )
    
    # Verify complete workflow
    await session.assert_that(
        Expect.tools.sequence(["fetch", "write_file"]),
        name="correct_sequence"
    )
    
    # Check output quality
    await session.assert_that(
        Expect.judge.llm(
            rubric="""The summary should:
            1. Extract key information from the JSON
            2. Be formatted as valid Markdown
            3. Be concise (under 200 words)""",
            min_score=0.8
        ),
        response=save_response,
        name="summary_quality"
    )
    
    # Verify performance
    await session.assert_that(
        Expect.performance.response_time_under(10000),
        name="completed_quickly"
    )
    
    # Check golden path (no redundant operations)
    await session.assert_that(
        Expect.path.efficiency(
            expected_tool_sequence=["fetch", "write_file"],
            tool_usage_limits={"fetch": 1, "write_file": 1},
            penalize_backtracking=True
        ),
        name="efficient_path"
    )

@teardown
def cleanup():
    """Remove test artifacts."""
    import shutil
    shutil.rmtree("test_output", ignore_errors=True)

Run with detailed output:

mcp-eval run test_document_processor.py -v --html report.html

Configuration
Configuration Files

mcpeval.yaml structure:

# Provider configuration
provider: anthropic  # or openai, google
model: claude-3-5-sonnet-20241022

# Execution settings
execution:
  timeout_seconds: 300
  max_concurrency: 5
  max_retries: 3

# Reporting
reporting:
  output_dir: test-reports
  formats: [json, html, markdown]
  include_traces: true

# MCP servers
mcp:
  servers:
    my_server:
      command: "uvx"
      args: ["mcp-server-fetch"]
      env:
        LOG_LEVEL: "info"

# Test agents
agents:
  default:
    model: claude-3-5-sonnet-20241022
    provider: anthropic
    server_names: ["my_server"]
    instruction: "You are a helpful test agent."

# Judge settings
judge:
  provider: anthropic
  model: claude-3-5-sonnet-20241022
  min_score: 0.7

Environment Variables

# API Keys
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."

# Override config
export MCPEVAL_PROVIDER="openai"
export MCPEVAL_MODEL="gpt-4-turbo-preview"
export MCPEVAL_TIMEOUT_SECONDS="600"

Programmatic Configuration

from mcp_eval.config import use_agent, update_config
from mcp_agent.agents.agent_spec import AgentSpec

# Use specific agent
use_agent(AgentSpec(
    name="test_agent",
    instruction="Be extremely thorough in testing.",
    server_names=["server1", "server2"]
))

# Update settings
update_config({
    "execution": {"timeout_seconds": 600},
    "reporting": {"output_dir": "custom-reports"}
})

CI/CD Integration
GitHub Actions

MCP-Eval includes pre-built GitHub Actions:

name: MCP Server Tests
on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run MCP-Eval tests
        uses: ./.github/actions/mcp-eval/run
        with:
          python-version: '3.11'
          tests: tests/
          run-args: '-v --max-concurrency 4'
          pr-comment: 'true'           # Add results to PR
          upload-artifacts: 'true'      # Save reports
          set-summary: 'true'           # GitHub job summary
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

  publish:
    needs: test
    if: github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./test-reports

GitLab CI

test:mcp:
  image: python:3.11
  script:
    - pip install mcp-eval
    - mcp-eval run tests/ --json results.json
  artifacts:
    reports:
      junit: results.json
    paths:
      - test-reports/

CLI Reference

MCP-Eval provides comprehensive CLI commands:

# Initialize configuration
mcp-eval init

# Run tests
mcp-eval run tests/                    # Run all tests in directory
mcp-eval run test_file.py -v          # Run with verbose output
mcp-eval run tests/ --max-concurrency 4
mcp-eval run tests/ --html report.html --json metrics.json

# Generate tests
mcp-eval generate --n-examples 10     # Generate test cases

# Server management
mcp-eval server list                  # List configured servers
mcp-eval server add --from-mcp-json   # Import from mcp.json

# Utilities
mcp-eval doctor --full                 # Diagnose configuration issues
mcp-eval validate                     # Validate config files

Advanced Features
Test Generation

Automatically generate test cases for your MCP server:

mcp-eval generate \
  --style pytest \
  --n-examples 10 \
  --provider anthropic \
  --model claude-3-5-sonnet-20241022

This analyzes your server's tools and generates comprehensive test coverage.
Scenario Testing

Compose multiple focused assertions in one coherent workflow:

from mcp_eval import task, Expect

@task("Fetch and summarize")
async def test_fetch_and_summarize(agent, session):
    response = await agent.generate_str(
        "Fetch https://example.com and summarize in one sentence"
    )

    await session.assert_that(
        Expect.tools.was_called("fetch"),
        name="fetch_called"
    )
    await session.assert_that(
        Expect.content.contains("Example Domain"),
        response=response,
        name="has_expected_text"
    )
    await session.assert_that(
        Expect.performance.max_iterations(3),
        name="efficient"
    )

Custom Evaluators

Create domain-specific evaluators:

from mcp_eval.evaluators import BaseEvaluator

class SecurityEvaluator(BaseEvaluator):
    """Check for security best practices."""
    
    async def evaluate(self, response, context):
        # Check for exposed secrets
        if "api_key" in response.lower():
            return False, "Potential API key exposure"
        
        # Check for SQL injection patterns
        if "DROP TABLE" in response.upper():
            return False, "Potential SQL injection"
        
        return True, "Security checks passed"

# Use in tests
await session.assert_that(
    SecurityEvaluator(),
    response=response
)

Performance Analysis

Use session.get_metrics() and CLI reports (--json/--markdown/--html) to analyze latency, token usage, and tool behavior.
Documentation

    Full Documentation
    Quickstart Guide
    API Reference
    Common Workflows
    Best Practices
    Troubleshooting

Examples

Complete working examples are available in examples/:

    mcp_server_fetch/ - Testing the fetch MCP server
    calculator_server/ - Testing a calculator with multiple operations
    multi_server/ - Testing agents using multiple MCP servers
    dataset_testing/ - Systematic testing with datasets
    llm_judges/ - Quality evaluation using LLM judges
    performance/ - Performance and load testing
    security/ - Security testing patterns

Architecture

MCP-Eval is built on key architectural principles:

    OTEL as Single Source of Truth: All metrics and assertions are derived from OpenTelemetry traces
    Agent-Server Separation: Clean separation between test agents and MCP servers
    Composable Assertions: All assertions follow a consistent API pattern
    Async-First: Built on asyncio for concurrent test execution
    Provider Agnostic: Works with any LLM provider (Anthropic, OpenAI, Google, etc.)

Contributing

Contributions are welcome. See CONTRIBUTING.md for:

    Development setup
    Code style guidelines
    Testing requirements
    Pull request process

Support

    Issues: GitHub Issues
    Discussions: GitHub Discussions
    Documentation: mcp-eval.ai

License

Apache 2.0 - see LICENSE for details.
About

Lightweight eval framework for MCP servers, built on mcp-agent
Resources
Readme
License
Apache-2.0 license
Code of conduct
Code of conduct
Contributing
Contributing
Security policy
Security policy
Activity
Custom properties
Stars
23 stars
Watchers
0 watching
Forks
8 forks
Report repository
Releases
7 tags
Deployments 41

github-pages September 6, 2025 20:09
staging - docs September 6, 2025 11:36

    production September 4, 2025 11:23

+ 38 deployments
Packages
No packages published
Contributors 5

    @StreetLamb
    @saqadri
    @petersonbill64
    @andrew-lastmile
    @MahtabSarvmaili

Languages

Python 99.4%

    Other 0.6% 

Footer
© 2026 GitHub, Inc.
Footer navigation

    Terms
    Privacy
    Security
    Status
    Community
    Docs
    Contact


Skip to content

    SalesforceAIResearch
    MCPEval

Repository navigation

    Code
    Issues5 (5)
    Pull requests1 (1)
    Agents
    Actions
    Projects

Owner avatar
MCPEval
Public

SalesforceAIResearch/MCPEval
Name	Last commit message
	Last commit date
sfdc-ospo-bot
sfdc-ospo-bot
Upload required SECURITY.md file for compliance
70e1f90
 · 
Jun 2, 2026
.github/workflows
	
Add Phase 0+1 improvements: bug fixes, parallel execution, unified JS…
	
Apr 9, 2026
backend
	
Fix 9 Copilot round-2 review issues
	
Apr 11, 2026
benchmarks
	
updating scripts
	
Sep 22, 2025
bin
	
updating code
	
Jul 17, 2025
frontend
	
Bump to v1.1.0: update README with new features, add multi-turn simul…
	
Apr 11, 2026
mcp_clients/example_openai_client
	
updating code
	
Jul 17, 2025
mcp_servers
	
Add 5 new MCP servers for enterprise evaluation
	
Apr 9, 2026
page
	
updating name
	
Jul 19, 2025
scripts
	
updating code
	
Jul 17, 2025
sfrgateway
	
Fix 9 Copilot round-2 review issues
	
Apr 11, 2026
src/mcpeval
	
Fix 9 Copilot round-2 review issues
	
Apr 11, 2026
tests
	
Fix 7 Copilot review issues: security, compat, and correctness
	
Apr 11, 2026
.env.template
	
updating servers
	
Jul 19, 2025
.gitignore
	
Add 5 new MCP servers for enterprise evaluation
	
Apr 9, 2026
.python-version
	
customization of MCPEval with added http mcp add and ollama model int…
	
Jul 31, 2025
AI_ETHICS.md
	
updating AI ethics and readme
	
Jul 7, 2025
CLAUDE.md
	
Add SFRGateway proxy to make project self-contained
	
Apr 9, 2026
CODEOWNERS
	
updating code owners
	
Jul 7, 2025
CODE_OF_CONDUCT.md
	
Initial commit
	
Jul 3, 2025
CONTRIBUTING.md
	
updating contributing
	
Jul 7, 2025
LICENSE.txt
	
Initial commit
	
Jul 3, 2025
README.md
	
Bump to v1.1.0: update README with new features, add multi-turn simul…
	
Apr 11, 2026
ROADMAP.md
	
Add Phase 0+1 improvements: bug fixes, parallel execution, unified JS…
	
Apr 9, 2026
SECURITY.md
	
Upload required SECURITY.md file for compliance
	
Jun 2, 2026
pyproject.toml
	
Bump to v1.1.0: update README with new features, add multi-turn simul…
	
Apr 11, 2026
requirements.txt
	
updating code
	
Jul 17, 2025
setup.sh
	
updating code
	
Jul 17, 2025
uv.lock
	
Bump to v1.1.0: update README with new features, add multi-turn simul…
	
Apr 11, 2026
Repository files navigation

    README
    Code of conduct

MCPEval: Automatic MCP-based Deep Evaluation for AI Agent Models

arXiv Release Notes Python 3.12+ License GitHub star chart

Paper | Features | Installation | Usage | CLI | Development

A Model Context Protocol (MCP) based LLM deep evaluation framework.
Overview

This project provides a framework for evaluating Large Language Models using the Model Context Protocol. It enables automating end- to-end task generation and deep evaluation of LLM agents across diverse dimensions.
Demo

🎬 Watch Full Demo Video (with audio)

Click above to download and view the complete MCPEval demonstration with audio explanation
Architecture

MCP-based LLM Evaluation Pipeline

MCPEval system architecture showing the complete evaluation pipeline from task generation to analysis
Homepage

MCPEval Homepage

MCPEval web interface providing intuitive access to all evaluation features
News

    v1.1.0 — Multi-turn simulation web UI, conversation replay viewer, model comparison dashboard with statistical testing, SQLite persistence & v1 REST API, SFRGateway proxy, CI pipeline, and comprehensive test suite
    Supporting GPT-5
    Using model-config for using any model to generate and evaluate
    A new revalidation cli is released for generating high-quality data

Features

    🚀 Automated End-to-End Evaluation — Single-command pipeline from task generation to analysis with parallel execution
    🔧 MCP Protocol Integration — 15+ built-in MCP servers spanning enterprise, utility, and public API domains
    📊 Comprehensive Analysis & Insights — Statistical model comparison with bootstrap confidence intervals and paired tests
    💻 User-Friendly Web Interface — Conversation replay viewer, model comparison dashboard, and multi-turn simulation UI
    ⚡ Advanced CLI Commands — Generate, verify, evaluate, simulate, and judge with flexible model configuration
    🗄️ SQLite Persistence & REST API — Durable storage for evaluation runs with a v1 leaderboard and runs API
    🔬 Multi-Turn Simulation — LLM-as-user simulation with scenario generation, persona support, and 5-dimension LLM judging
    🌐 SFRGateway Proxy — Self-contained LLM inference via the Salesforce Research gateway (no direct API keys needed)
    ✅ CI & Test Suite — GitHub Actions pipeline with unit and integration tests

Citation

If you find our system or paper useful, please cite

@misc{liu2025mcpevalautomaticmcpbaseddeep,
      title={MCPEval: Automatic MCP-based Deep Evaluation for AI Agent Models}, 
      author={Zhiwei Liu and Jielin Qiu and Shiyu Wang and Jianguo Zhang and Zuxin Liu and Roshan Ram and Haolin Chen and Weiran Yao and Huan Wang and Shelby Heinecke and Silvio Savarese and Caiming Xiong},
      year={2025},
      eprint={2507.12806},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2507.12806}, 
}

Installation
Quick Setup (Recommended)

For complete setup including both CLI and Web UI:

# Clone the repository
git clone https://github.com/SalesforceAIResearch/MCPEval.git
cd MCPEval

# Run unified setup script (installs CLI, backend API, and frontend UI)
./setup.sh

This will set up:

    ✅ Core CLI evaluation framework
    ✅ Flask REST API backend
    ✅ React web interface
    ✅ All dependencies using uv package manager

CLI-Only Setup

For command-line usage only:

# Make sure uv is installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the package
uv sync
uv sync --extra dev

Environment Configuration

cp .env.template .env

Edit the .env file to add your OpenAI API key:

OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE

OR export the key in your terminal:

export OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE

SFRGateway Proxy (Optional)

For self-contained LLM inference without managing API keys directly, use the bundled SFRGateway proxy:

cd sfrgateway
cp .env.template .env   # edit .env with your X_API_KEY
PROXY_PORT=8008 uv run python server.py

Then point model configs at http://localhost:8008/v1 with "api_key": "dummy". See sfrgateway/README.md for details.
Usage
Web Interface (Recommended for New Users)

After running the setup script:

    Start the backend API:

    cd backend
    uv run app.py

Backend will run on http://localhost:22358

Start the frontend (in a new terminal):

cd frontend
npm start

    Frontend will run on http://localhost:22359

    Access the web application:
        Open http://localhost:22359 in your browser
        Use the intuitive interface to generate tasks, run evaluations, and view results
        Conversation Replay — Browse and inspect multi-turn conversations turn by turn
        Model Comparison — Side-by-side model comparison with statistical significance testing
        Multi-Turn Simulation — Generate scenarios, run user simulations, and evaluate conversations from the UI
        Real-time progress tracking for all operations

Note: The frontend automatically proxies API requests to the backend server (port 22358). No additional configuration is needed.
Command Line Interface

For advanced users and automation:
Example Usage

We provide an example about a special calculator MCP application. We define an example special calculator MCP server and use OpenAI client to interact with the server.

Quick start:

# Basic example with local MCP server
uv run mcp_clients/example_openai_client/client.py --servers mcp_servers/special_calculator/server.py

# Multiple servers with environment variables (use ^ for env vars)
uv run mcp_clients/example_openai_client/client.py --servers @modelcontextprotocol/server-sequential-thinking mcp-server-nationalparks^NPS_API_KEY=your-api-key-here

# Combined example with arguments and environment variables
uv run mcp_clients/example_openai_client/client.py --servers @openbnb/mcp-server-airbnb:--ignore-robots-txt mcp-server-nationalparks^NPS_API_KEY=your-api-key-here

For more details on the OpenAI client usage, see the OpenAI Client README.
Available MCP Servers

MCPEval includes a diverse set of MCP servers spanning enterprise domains, public APIs, and computation utilities. Each server exposes tools that LLM agents are evaluated against.
Self-Contained Servers (No Credentials Required)

These servers are fully deterministic with embedded data or pure computation — ideal for reproducible evaluation.
Server 	Tools 	Domain 	Description
hr_management 	10 	Enterprise 	Departments, employees, leave requests, performance reviews, org chart. Embedded SQLite with 70+ rows.
ecommerce 	11 	Enterprise 	Products, orders, customers, inventory, sales summaries. Embedded SQLite with 80+ rows.
datetime_tools 	7 	Utility 	Timezone conversion, date difference, business days, holiday support (US/UK/DE/FR/JP).
unit_converter 	6 	Utility 	Length, weight, temperature, volume, speed, data size conversion with strict enum schemas.
special_calculator 	4 	Demo 	Basic arithmetic with special transformations (add+double, subtract+halve, etc.).
sqlite 	8 	Database 	General-purpose SQLite operations — create tables, query, insert, with sample datasets.
filesystem 	14 	System 	Local file operations (read, write, search, directory listing). npm: @modelcontextprotocol/server-filesystem
memory 	9 	Knowledge 	Knowledge graph with entities, relations, and observations. npm: @modelcontextprotocol/server-memory
Public API Servers (Free, No Credentials)
Server 	Tools 	Domain 	Description
book 	8 	Library 	Open Library search — books by title/ISBN, authors, advanced search.
youtube 	4 	Media 	YouTube transcript extraction, search, and summarization.
healthcare 	5 	Medical 	FDA drug lookup, PubMed search, clinical trials, ICD-10 codes.
sports 	4 	Sports 	NBA, MLB, NFL teams, players, and game data via balldontlie.io.
Servers Requiring API Keys
Server 	Tools 	Domain 	Credentials
travel_assistant 	6 	Travel 	Flights, hotels, restaurants, local events. Requires SERPAPI_API_KEY, YELP_API_KEY.
airbnb 	2 	Travel 	Airbnb listing search and details. npm: @openbnb/mcp-server-airbnb
yfinance 	10 	Finance 	Stock prices, financials, options, analyst recommendations via Yahoo Finance.
national_park 	6 	Parks 	U.S. National Parks info, alerts, campgrounds, events. Requires NPS_API_KEY (free).
crm_bench 	11 	CRM 	Salesforce CRM operations (stub implementation for benchmarking).
Multi-Turn Simulation

MCPEval supports multi-turn user simulation where a simulator LLM plays the user role and an agent LLM is tested:

# Generate scenarios from verified tasks
mcp-eval generate-scenarios \
  --servers mcp_servers/hr_management/server.py \
  --output scenarios.jsonl \
  --num-scenarios 5

# Run multi-turn simulation
mcp-eval simulate \
  --servers mcp_servers/hr_management/server.py \
  --simulator-model-config simulator_model.json \
  --agent-model-config agent_model.json \
  --scenarios-file scenarios.jsonl \
  --output multiturn_results.jsonl

# Evaluate conversations with LLM judge
mcp-eval evaluate-multiturn \
  --input multiturn_results.jsonl \
  --output multiturn_evaluation.jsonl

The judge evaluates on 5 dimensions: clarification handling, context maintenance, tool usage efficiency, goal achievement, and response quality.
Quick Development Setup

# Complete development environment
./setup.sh

# Start backend API (Terminal 1)
cd backend && uv run app.py

# Start frontend UI (Terminal 2)  
cd frontend && npm start

# Access at http://localhost:22359

Contributing

For each benchmark contribution, please follow the following steps:

    Create a new directory in the benchmarks/your_benchmark_name folder.
    If you are developing a new MCP server, please create a new folder and add the server script in the mcp_servers folder.
    If you are developing a new MCP client, please create a new folder and add the client script in the mcp_clients folder.
    Add your benchmark scripts to the benchmarks/your_benchmark_name folder.

For web interface contributions:

    Frontend components: frontend/src/components/ and frontend/src/pages/
    Backend API endpoints: backend/app.py

Development Roadmap

See our detailed Development Roadmap for the current progress and planned features across all components.
MCPEval CLI Usage

The MCPEval CLI provides a comprehensive toolkit for managing MCP servers and evaluating LLMs. For detailed documentation, parameter descriptions, and advanced usage examples, see the CLI README.
Quick Start

Auto Workflow (Recommended) - Complete evaluation pipeline in one command:

# Automatically generate tasks, verify, evaluate, and analyze results
mcp-eval auto \
  --servers @openbnb/mcp-server-airbnb:--ignore-robots-txt \
  --working-dir evaluation_results/airbnb_eval \
  --task-model gpt-4o-2024-11-20 \
  --eval-model-configs benchmarks/airbnb/eval_models/gpt-4o.json \
  --num-tasks 50

Manual Workflow

For more control over each step:

# 1. Generate tasks
mcp-eval generate-tasks \
  --servers @openbnb/mcp-server-airbnb:--ignore-robots-txt \
  --model-config benchmarks/airbnb/eval_models/gpt-4o.json \
  --num-tasks 200 \
  --output data/airbnb/evaluation_tasks.jsonl

# 2. Verify tasks work correctly
mcp-eval verify-tasks \
  --servers @openbnb/mcp-server-airbnb:--ignore-robots-txt \
  --tasks-file data/airbnb/evaluation_tasks.jsonl \
  --output data/airbnb/evaluation_tasks_verified.jsonl

# 3. Revalidate task descriptions based on execution data (optional but recommended)
mcp-eval revalidate-tasks \
  --verified-tasks-file data/airbnb/evaluation_tasks_verified.jsonl \
  --model-config benchmarks/airbnb/eval_models/gpt-4o.json \
  --output data/airbnb/evaluation_tasks_final.jsonl

# 4. Evaluate model performance
mcp-eval evaluate \
  --servers @openbnb/mcp-server-airbnb:--ignore-robots-txt \
  --model-config benchmarks/airbnb/eval_models/gpt-4o.json \
  --tasks-file data/airbnb/evaluation_tasks_final.jsonl \
  --output benchmarks/airbnb/results/gpt4o_evaluation.json \
  --max-turns 30

# 5. Analyze results and generate reports
mcp-eval analyze \
  --predictions benchmarks/airbnb/results/gpt4o_evaluation.json \
  --ground-truth data/airbnb/evaluation_tasks_final.jsonl \
  --generate-report

# 6. Optional: Run LLM judge evaluation
mcp-eval judge \
  --input-file benchmarks/airbnb/results/gpt4o_evaluation.json \
  --output-dir benchmarks/airbnb/results \
  --model-config benchmarks/airbnb/eval_models/gpt-4o.json

# 7. Optional: Analyze LLM judgment results
mcp-eval judge-rubric \
  --trajectory-file benchmarks/airbnb/results/gpt4o_evaluation_trajectory.json \
  --completion-file benchmarks/airbnb/results/gpt4o_evaluation_completion.json \
  --output-dir benchmarks/airbnb/report

Note: The revalidation step (step 3) analyzes the actual tool conversations from verified tasks and improves task descriptions to be more accurate and specific. This leads to higher-quality evaluation datasets and better task clarity for subsequent evaluations.
Available Commands

    generate-tasks - Generate evaluation tasks for MCP servers
    verify-tasks - Verify tasks can be executed successfully
    revalidate-tasks - Improve task descriptions based on actual execution data
    evaluate - Evaluate models using MCP servers and tasks
    analyze - Analyze evaluation results and generate reports
    judge - Run LLM-based evaluation of execution trajectories
    judge-rubric - Analyze LLM judgment results
    generate-scenarios - Generate multi-turn scenarios from tasks or servers
    simulate - Run multi-turn user simulation conversations
    evaluate-multiturn - Evaluate multi-turn conversations with LLM judge
    convert-data - Convert data to different formats (e.g., XLAM)
    auto - Complete automated evaluation workflow

Model Configuration

Models are configured using JSON files. Examples:

{
  "model": "gpt-4o-2024-11-20",
  "temperature": 0.01,
  "max_tokens": 16384
}

For custom endpoints:

{
  "model": "mistral-24b",
  "api_key": "default",
  "temperature": 0.01,
  "max_tokens": 3000,
  "base_url": "http://<IP_Address>:<port>/v1"
}

Getting Help

# General help
mcp-eval --help

# Command-specific help
mcp-eval generate-tasks --help
mcp-eval evaluate --help

For comprehensive documentation, examples, and advanced usage patterns, see the Complete CLI Documentation.
License

This project is licensed under the Apache 2.0 License. See the LICENSE file for details.
Contact

For any questions or feedback, please contact Zhiwei Liu at zhiweiliu@salesforce.com.
About

MCP-based Agent Deep Evaluation System
Resources
Readme
License
Apache-2.0 license
Code of conduct
Code of conduct
Contributing
Contributing
Security policy
Security policy
Activity
Custom properties
Stars
151 stars
Watchers
2 watching
Forks
18 forks
Report repository
Releases 3
v1.1.0 Latest
Sep 25, 2025
+ 2 releases
Packages
No packages published
Contributors 4

    @JimSalesforce
    JimSalesforce
    @ImtiazKhanDS
    ImtiazKhanDS Imtiaz Khan
    @sfdc-ospo-bot
    sfdc-ospo-bot Salesforce OSPO Service Bot
    @sjswerdloff
    sjswerdloff Stuart J Swerdloff

Languages

Python 62.5%
TypeScript 27.8%

    Shell 9.7% 

Generated from salesforce/oss-template
Footer
© 2026 GitHub, Inc.
Footer navigation

    Terms
    Privacy
    Security
    Status
    Community
    Docs
    Contact


