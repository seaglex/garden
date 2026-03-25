"""Custom tools for the ADK agent."""

import subprocess
import sys
from typing import Annotated

from google.adk.tools import ToolContext


def run_python_code(
    code: Annotated[str, "Python code to execute. Should be valid Python code."],
    tool_context: ToolContext,
) -> dict:
    """Execute Python code using subprocess and return the result.

    This tool runs Python code in a subprocess with the current working directory
    set to the project root. It captures stdout, stderr, and the return code.

    Args:
        code: Valid Python code to execute.
        tool_context: ADK tool context for accessing state and actions.

    Returns:
        dict with keys:
            - status: "success" or "error"
            - stdout: Captured standard output
            - stderr: Captured standard error
            - return_code: Process exit code
            - message: Human-readable summary

    Raises:
        ValueError: If code is empty or too long.
    """
    if not code.strip():
        return {
            "status": "error",
            "stdout": "",
            "stderr": "Error: No code provided",
            "return_code": 1,
            "message": "Failed: Empty code",
        }

    # Limit code length to prevent abuse
    if len(code) > 10000:
        return {
            "status": "error",
            "stdout": "",
            "stderr": "Error: Code exceeds 10000 character limit",
            "return_code": 1,
            "message": "Failed: Code too long",
        }

    try:
        # Run Python code in subprocess
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout
        )

        output = result.stdout.strip()
        error = result.stderr.strip()

        if result.returncode == 0:
            return {
                "status": "success",
                "stdout": output,
                "stderr": "",
                "return_code": 0,
                "message": f"Success: Code executed, output length: {len(output)} chars",
            }
        else:
            return {
                "status": "error",
                "stdout": output,
                "stderr": error,
                "return_code": result.returncode,
                "message": f"Failed: {error[:200]}...",
            }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "stdout": "",
            "stderr": "Error: Execution timed out after 30 seconds",
            "return_code": -1,
            "message": "Failed: Timeout",
        }

    except Exception as e:
        return {
            "status": "error",
            "stdout": "",
            "stderr": str(e),
            "return_code": -1,
            "message": f"Failed: {str(e)[:200]}...",
        }


def run_python_file(
    filename: Annotated[str, "Filename of the Python script to run"],
    tool_context: ToolContext,
) -> dict:
    """Execute a Python script file and return the result.

    This tool runs a Python script file from the project directory using subprocess.

    Args:
        filename: Name of the Python script file to execute.
        tool_context: ADK tool context for accessing state and actions.

    Returns:
        dict with keys:
            - status: "success" or "error"
            - stdout: Captured standard output
            - stderr: Captured standard error
            - return_code: Process exit code
            - message: Human-readable summary
    """
    import os
    from pathlib import Path

    # Get the project root directory
    project_root = Path(__file__).parent
    file_path = project_root / filename

    if not file_path.exists():
        return {
            "status": "error",
            "stdout": "",
            "stderr": f"Error: File not found: {filename}",
            "return_code": 1,
            "message": f"Failed: File not found: {filename}",
        }

    if not file_path.suffix == ".py":
        return {
            "status": "error",
            "stdout": "",
            "stderr": f"Error: Not a Python file: {filename}",
            "return_code": 1,
            "message": f"Failed: Not a Python file: {filename}",
        }

    try:
        result = subprocess.run(
            [sys.executable, str(file_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        output = result.stdout.strip()
        error = result.stderr.strip()

        if result.returncode == 0:
            return {
                "status": "success",
                "stdout": output,
                "stderr": "",
                "return_code": 0,
                "message": f"Success: {filename} executed, output length: {len(output)} chars",
            }
        else:
            return {
                "status": "error",
                "stdout": output,
                "stderr": error,
                "return_code": result.returncode,
                "message": f"Failed: {error[:200]}...",
            }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "stdout": "",
            "stderr": "Error: Execution timed out after 30 seconds",
            "return_code": -1,
            "message": "Failed: Timeout",
        }

    except Exception as e:
        return {
            "status": "error",
            "stdout": "",
            "stderr": str(e),
            "return_code": -1,
            "message": f"Failed: {str(e)[:200]}...",
        }
