"""
A smolagents agent with pluggable backends (currently only OPENAI is implemented).

Usage:
    python agent.py  # Uses OPENAI by default with the built-in prompt
    python agent.py --no-plan  # Skip the planning step (go straight to execution)
"""

import argparse
import os
import sys

from dotenv import load_dotenv
from smolagents import CodeAgent, LiteLLMModel, PlanningStep
from smolagents.utils import AgentError

from tools import (
    check_data,
    get_catalog_column_names,
    get_cluster_coordinates,
    get_cluster_in_range,
    get_mass_unit,
    get_matching_cluster_names,
)

# Load environment variables from .env file
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_ID = "openai/openai/gpt-5.4-nano-2026-03-17"

API_BASE_OPENAI = "http://131.220.150.238:8080"

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not found. " "Create a .env file with: OPENAI_API_KEY=your-key-here")


# Backend registry – maps CLI names to LiteLLMModel constructors
def _build_model(backend: str) -> LiteLLMModel:
    """Return a LiteLLMModel for the given backend name."""
    backends = {
        "openai": lambda: LiteLLMModel(
            model_id=OPENAI_MODEL_ID,
            api_key=OPENAI_API_KEY,
            api_base=API_BASE_OPENAI,
        ),
    }
    if backend not in backends:
        raise ValueError(f"Unknown backend '{backend}'. Choose from: {', '.join(backends)}")
    return backends[backend]()


# Planner agent — creates a plan/task list before execution, with user approval
def on_plan_created(memory_step, agent):
    """Step callback: fired after the planner creates a plan.
    Displays the plan and asks the user to approve or cancel."""
    if isinstance(memory_step, PlanningStep):
        plan = memory_step.plan
        print("\n" + "=" * 60)
        print("📋  PLAN")
        print("=" * 60)
        print(plan)
        print("=" * 60)

        # Ask user for approval
        while True:
            choice = input("\nApprove this plan? [Y/n]: ").strip().lower()
            if choice in ("", "y", "yes"):
                print("✅ Plan approved. Executing…\n")
                return  # let the agent continue
            elif choice in ("n", "no"):
                print("❌ Execution cancelled by user.")
                raise AgentError("Plan rejected by user.", agent.logger)
            print("Please enter Y or N.")


TOOLS = [
    check_data,
    get_catalog_column_names,
    get_mass_unit,
    get_cluster_coordinates,
    get_cluster_in_range,
    get_matching_cluster_names,
]

AUTHORIZED_IMPORTS = [
    "astropy",
    "numpy",
    "datetime",
    "pathlib",
    "matplotlib",
]


def _make_code_agent(model: LiteLLMModel, with_planning: bool = True, max_steps: int = 15) -> CodeAgent:
    """Create a CodeAgent, optionally with planning."""
    kwargs: dict = dict(
        tools=TOOLS,
        model=model,
        additional_authorized_imports=AUTHORIZED_IMPORTS,
        stream_outputs=True,
        max_steps=max_steps,
    )
    if with_planning:
        kwargs["planning_interval"] = 1000  # plan on step 1 only
        kwargs["step_callbacks"] = {PlanningStep: on_plan_created}
    return CodeAgent(**kwargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A smolagents agent implementation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default="Give me 5 names from clusters in one catalog that appear also in the second catalog together with "
        "masses. Use a tolerance of 1 arcmin. Submodules are not allowed to be directly imported so you need to "
        "address them via the core module, e.g. import astropy and use astropy.io.fits explicitly.",
        help="The task for the agent to perform.",
    )
    parser.add_argument(
        "--backend",
        choices=["openai"],
        default="openai",
        help="LLM backend to use (default: %(default)s).",
    )
    parser.add_argument(
        "--no-plan",
        action="store_true",
        help="Skip the planning step entirely (run CodeAgent directly).",
    )
    args = parser.parse_args()

    # Build the model for the chosen backend
    model = _build_model(args.backend)
    print(f"🤖 Using backend: {args.backend}\n")

    # Pick the agent to run
    if args.no_plan:
        runner = _make_code_agent(model, with_planning=False, max_steps=20)
        print("⚡ Planner skipped — running CodeAgent directly.\n")
    else:
        runner = _make_code_agent(model, with_planning=True, max_steps=15)

    try:
        result = runner.run(args.prompt)
        print(f"\n🎉 Agent result: {result}")
    except Exception as e:
        if "interrupted" in str(e).lower():
            print("\n🛑 Agent was interrupted by user.")
            sys.exit(0)
        raise
