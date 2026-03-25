"""Skills loader for loading skills from the skills folder.

This module provides utilities to load skills from a local directory
and register them with the ADK agent using SkillToolset.

Example usage:

    from skills_loader import get_default_skill_toolset, load_all_skills

    # Get the default skill toolset (cached)
    toolset = get_default_skill_toolset()

    # Load all skills manually
    skills = load_all_skills("/path/to/skills")

    # Get available skill names and descriptions
    skills_info = get_available_skills()
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Sequence

from google.adk.skills import load_skill_from_dir
from google.adk.skills.models import Skill
from google.adk.tools.skill_toolset import SkillToolset

from tools import run_python_code, run_python_file

logger = logging.getLogger(__name__)

__all__ = [
    "load_all_skills",
    "create_skill_toolset",
    "get_available_skills",
    "get_default_skill_toolset",
    "reset_default_skill_toolset",
    "DEFAULT_SKILLS_DIR",
]

# Default skills directory relative to project root
DEFAULT_SKILLS_DIR = Path(__file__).parent / "skills"

# Patterns for directories to skip when listing skills
_SKIP_DIRS = {".adk", "__pycache__", ".git", ".venv", "venv", ".DS_Store"}


def _is_valid_skill_dir(dir_path: Path) -> bool:
    """Check if a directory is a valid skill directory (contains SKILL.md)."""
    if not dir_path.is_dir():
        return False
    # Skip hidden directories and common non-skill directories
    if dir_path.name.startswith('.') or dir_path.name in _SKIP_DIRS:
        return False
    # Check for SKILL.md or skill.md
    return (dir_path / "SKILL.md").exists() or (dir_path / "skill.md").exists()


def load_all_skills(skills_dir: str | Path | None = None) -> list[Skill]:
    """Load all skills from the skills directory.

    Args:
        skills_dir: Path to the skills directory. Defaults to the 'skills'
                    folder in the project root.

    Returns:
        List of loaded Skill objects.
    """
    if skills_dir is None:
        skills_dir = DEFAULT_SKILLS_DIR

    skills_path = Path(skills_dir).resolve()

    if not skills_path.exists():
        logger.warning(
            "Skills directory not found at %s. No skills will be loaded.",
            skills_path,
        )
        return []

    if not skills_path.is_dir():
        logger.error(
            "Skills path is not a directory: %s. No skills will be loaded.",
            skills_path,
        )
        return []

    # Scan directory for valid skill directories
    skill_dirs = [d for d in skills_path.iterdir() if _is_valid_skill_dir(d)]

    if not skill_dirs:
        logger.debug(
            "No valid skills found in %s. Make sure skill folders contain a valid SKILL.md file.",
            skills_path,
        )
        return []

    # Load each skill
    skills: list[Skill] = []
    for skill_dir in skill_dirs:
        try:
            skill = load_skill_from_dir(skill_dir)
            skills.append(skill)
            logger.info("Loaded skill: %s (%s)", skill.name, skill.description)
        except Exception as e:
            logger.error(
                "Failed to load skill %s: %s",
                skill_dir.name,
                e,
            )

    logger.info("Successfully loaded %d skills", len(skills))
    return skills


def create_skill_toolset(
    skills_dir: str | Path | None = None,
    code_executor: object = None,
) -> SkillToolset:
    """Create a SkillToolset from skills in the skills directory.

    Args:
        skills_dir: Path to the skills directory. Defaults to the 'skills'
                    folder in the project root.
        code_executor: Optional code executor for script execution. If None,
                       the agent's default code executor will be used.

    Returns:
        A SkillToolset containing all loaded skills.
    """
    skills = load_all_skills(skills_dir)
    return SkillToolset(skills=skills, code_executor=code_executor)


def get_available_skills(skills_dir: str | Path | None = None) -> dict[str, str]:
    """Get a dictionary of available skill names and descriptions.

    Args:
        skills_dir: Path to the skills directory.

    Returns:
        Dictionary mapping skill names to their descriptions.
    """
    skills = load_all_skills(skills_dir)
    return {skill.name: skill.description for skill in skills}


# Default skill toolset instance
_default_skill_toolset: SkillToolset | None = None


def get_default_skill_toolset(
    skills_dir: str | Path | None = None,
    code_executor: object = None,
) -> SkillToolset:
    """Get or create the default skill toolset.

    This function creates a cached instance of the skill toolset
    to avoid reloading skills on each call.

    Args:
        skills_dir: Path to the skills directory.
        code_executor: Optional code executor for script execution.

    Returns:
        The default SkillToolset instance.
    """
    global _default_skill_toolset

    if _default_skill_toolset is None:
        _default_skill_toolset = create_skill_toolset(
            skills_dir=skills_dir, code_executor=code_executor
        )

    return _default_skill_toolset


def reset_default_skill_toolset() -> None:
    """Reset the cached default skill toolset.

    This allows skills to be reloaded on the next call to
    get_default_skill_toolset().
    """
    global _default_skill_toolset
    _default_skill_toolset = None
