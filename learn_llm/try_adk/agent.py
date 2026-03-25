"""Main agent definition for the ADK application."""

import os
import dotenv

from google.adk.agents import Agent

from skills_loader import get_default_skill_toolset
from tools import run_python_code, run_python_file


dotenv.load_dotenv()

# Model configuration from environment
# Default to DashScope model if available, otherwise Gemini
DASHSCOPE_MODEL = os.getenv("DASHSCOPE_MODEL")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if DASHSCOPE_MODEL and DASHSCOPE_API_KEY:
    MODEL = DASHSCOPE_MODEL
    from google.adk.models.lite_llm import LiteLlm

    model_instance = LiteLlm(
        model=MODEL,
        base_url=os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        api_key=DASHSCOPE_API_KEY,
    )
    # DashScope models don't support BuiltInCodeExecutor, use our tools instead
    code_executor = None
elif GOOGLE_API_KEY:
    MODEL = os.getenv("MODEL", "gemini-3-flash-preview")
    model_instance = MODEL
    code_executor = None  # Will use built-in executor by default
else:
    # Default for local testing without API keys
    MODEL = os.getenv("MODEL", "gemini-3-flash-preview")
    model_instance = MODEL
    code_executor = None

# Load skills from the skills folder
skill_toolset = get_default_skill_toolset(code_executor=code_executor)

# Build skill descriptions for the agent instruction
from google.adk.skills.models import Skill
skill_descriptions = []
for skill in skill_toolset._skills.values():  # type: ignore
    if isinstance(skill, Skill):
        skill_descriptions.append(f"- **{skill.name}**: {skill.description}")
skill_descriptions_text = "\n".join(skill_descriptions) if skill_descriptions else "No skills loaded."

# Create the root agent with custom tools
root_agent = Agent(
    model=model_instance,
    name="root_agent",
    description="A helpful assistant that can execute Python code and manage skills.",
    instruction=f"""You are a helpful AI assistant with the ability to execute Python code and manage skills.

## Capabilities

1. **Answer Questions**: Provide helpful answers to user questions based on your knowledge.

2. **Execute Python Code**: You have a tool called `run_python_code` that allows you to execute Python code. Use this when:
   - Playing the role of a Python interpreter
   - Running calculations or data processing
   - Testing code snippets
   - Performing computations

   Example usage pattern:
   - For simple code: use `run_python_code` directly
   - For multi-line code, use triple quotes
   - Import necessary modules (os, sys, json, etc. are available)

3. **Skill Management**: You can manage and document skills in the skills folder.

## Rules

- Always provide clear explanations of what your code does
- Use meaningful variable names
- Handle errors gracefully in your code
- Report the output and any errors from code execution clearly

## Available Tools

- `run_python_code(code)`: Execute Python code and return results
- `run_python_file(filename)`: Run a Python script file from the project directory

## Available Skills

You can use skills from the skills folder. Available skills:
{skill_descriptions_text}

When a skill seems relevant, use `load_skill` to read its full instructions
and `run_skill_script` to execute scripts from the skill's scripts/ directory.
""",
    # Tools for code execution and skills
    tools=[run_python_code, run_python_file, skill_toolset],
    # Code executor (disabled for non-Gemini models like DashScope)
    code_executor=code_executor,
)
