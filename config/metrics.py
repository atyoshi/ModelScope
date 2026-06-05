"""
Typed evaluation metric system.

Each metric has a `type` key that determines which assertion is run against
telemetry. The `params` dict holds type-specific configuration.

Inspired by:
  - lastmile-ai/mcp-eval   (Expect.tools / Expect.content / Expect.path / Expect.judge)
  - SalesforceAIResearch/MCPEval (tool accuracy, sequence, LLM judge dimensions)
"""
from __future__ import annotations

import re
from typing import Any


# ── Metric type registry ────────────────────────────────────────────────────────

METRIC_TYPES: dict[str, dict] = {
    # ── Task / validation ──────────────────────────────────────────────────────
    "task_completion": {
        "label": "Task Completion",
        "category": "Validation",
        "description": "Validation command exits 0 and no fail patterns match",
        "params": [],
    },

    # ── Tool assertions ────────────────────────────────────────────────────────
    "tool_called": {
        "label": "Tool Was Called",
        "category": "Tool",
        "description": "A specific tool was invoked at least once",
        "params": [
            {"name": "tool_name", "type": "str", "label": "Tool Name", "default": ""},
        ],
    },
    "tool_not_called": {
        "label": "Tool Not Called",
        "category": "Tool",
        "description": "A specific tool was never invoked",
        "params": [
            {"name": "tool_name", "type": "str", "label": "Tool Name", "default": ""},
        ],
    },
    "tool_sequence": {
        "label": "Tool Call Sequence",
        "category": "Tool",
        "description": "Tools were invoked in the specified order (as a subsequence)",
        "params": [
            {"name": "sequence", "type": "list[str]",
             "label": "Expected sequence (comma-separated)", "default": ""},
        ],
    },
    "tool_call_count": {
        "label": "Tool Call Count",
        "category": "Tool",
        "description": "Total tool calls ≤ N",
        "params": [
            {"name": "max_calls", "type": "int", "label": "Max calls", "default": 5},
        ],
    },
    "tool_success_rate": {
        "label": "Tool Success Rate",
        "category": "Tool",
        "description": "Fraction of tool calls that succeeded ≥ threshold",
        "params": [
            {"name": "min_rate", "type": "float", "label": "Min rate (0 – 1)", "default": 0.9},
        ],
    },
    "no_repeated_calls": {
        "label": "No Repeated Tool Calls",
        "category": "Tool",
        "description": "No tool was called twice with identical arguments",
        "params": [],
    },
    "tool_output_contains": {
        "label": "Tool Output Contains",
        "category": "Tool",
        "description": "The result from a specific tool contains a required string",
        "params": [
            {"name": "tool_name", "type": "str", "label": "Tool name", "default": ""},
            {"name": "text",      "type": "str", "label": "Required text", "default": ""},
        ],
    },

    # ── Content / response assertions ──────────────────────────────────────────
    "content_contains": {
        "label": "Response Contains",
        "category": "Content",
        "description": "Final LLM response contains a specific string",
        "params": [
            {"name": "text", "type": "str", "label": "Required text", "default": ""},
        ],
    },
    "content_not_contains": {
        "label": "Response Does Not Contain",
        "category": "Content",
        "description": "Final LLM response does NOT contain a specific string",
        "params": [
            {"name": "text", "type": "str", "label": "Forbidden text", "default": ""},
        ],
    },
    "content_regex": {
        "label": "Response Matches Regex",
        "category": "Content",
        "description": "Final LLM response matches a regular-expression pattern",
        "params": [
            {"name": "pattern", "type": "str", "label": "Regex pattern", "default": ""},
        ],
    },

    # ── Performance ────────────────────────────────────────────────────────────
    "latency": {
        "label": "Latency",
        "category": "Performance",
        "description": "Total wall-clock time < N seconds",
        "params": [
            {"name": "max_seconds", "type": "float", "label": "Max seconds", "default": 30.0},
        ],
    },
    "token_limit": {
        "label": "Token Limit",
        "category": "Performance",
        "description": "Total tokens (prompt + completion) < N",
        "params": [
            {"name": "max_tokens", "type": "int", "label": "Max tokens", "default": 2000},
        ],
    },
    "max_iterations": {
        "label": "Max LLM Iterations",
        "category": "Performance",
        "description": "Number of LLM round-trips ≤ N  (mcp-eval: Expect.performance.max_iterations)",
        "params": [
            {"name": "max_iter", "type": "int", "label": "Max iterations", "default": 3},
        ],
    },
    "tokens_per_second": {
        "label": "Tokens / Second",
        "category": "Performance",
        "description": "Generation throughput ≥ N tok/s",
        "params": [
            {"name": "min_tps", "type": "float", "label": "Min tok/s", "default": 5.0},
        ],
    },

    # ── Path / execution efficiency ────────────────────────────────────────────
    "path_efficiency": {
        "label": "Path Efficiency",
        "category": "Path",
        "description": (
            "Actual tool sequence matches the expected golden path "
            "(mcp-eval: Expect.path.efficiency)"
        ),
        "params": [
            {"name": "expected_sequence", "type": "list[str]",
             "label": "Expected tool sequence (comma-separated)", "default": ""},
            {"name": "allow_extra_steps", "type": "int",
             "label": "Extra steps allowed", "default": 0},
            {"name": "penalize_backtracking", "type": "bool",
             "label": "Fail on backtracking", "default": True},
        ],
    },

    # ── MCPEval multi-turn judge dimensions ────────────────────────────────────
    "goal_achievement": {
        "label": "Goal Achievement",
        "category": "Judge",
        "description": (
            "MCPEval dimension: did the agent fully achieve the stated goal? "
            "Evaluated from validation result + tool success."
        ),
        "params": [],
    },
    "tool_usage_efficiency": {
        "label": "Tool Usage Efficiency",
        "category": "Judge",
        "description": (
            "MCPEval dimension: did the agent use tools efficiently "
            "(minimal calls, no redundancy)?"
        ),
        "params": [
            {"name": "max_calls", "type": "int", "label": "Max tool calls", "default": 5},
        ],
    },
    "no_error_output": {
        "label": "No Error in Output",
        "category": "Judge",
        "description": (
            "AI inefficiency check: exit code = 0 but output does not contain "
            "error-indicating strings (false completion guard)."
        ),
        "params": [],
    },
}

# Ordered list of category names for display
CATEGORIES = ["Validation", "Tool", "Content", "Performance", "Path", "Judge"]


# ── Helper: build a metric dict ─────────────────────────────────────────────────

def make_metric(
    metric_id: str,
    name: str,
    type_key: str,
    enabled: bool = True,
    **params: Any,
) -> dict:
    return {
        "id":      metric_id,
        "name":    name,
        "type":    type_key,
        "enabled": enabled,
        "params":  params,
    }


# ── Criterion string (human-readable summary) ────────────────────────────────────

def format_criterion(metric: dict) -> str:
    t = metric.get("type", "")
    p = metric.get("params", {})

    if t == "task_completion":
        return "Validation exits 0, no fail patterns matched"
    if t == "tool_called":
        return f"'{p.get('tool_name','?')}' was invoked"
    if t == "tool_not_called":
        return f"'{p.get('tool_name','?')}' was NOT invoked"
    if t == "tool_sequence":
        return f"Sequence: [{p.get('sequence','?')}]"
    if t == "tool_call_count":
        return f"Total calls ≤ {p.get('max_calls', 5)}"
    if t == "tool_success_rate":
        rate = float(p.get("min_rate", 0.9)) * 100
        return f"Tool success rate ≥ {rate:.0f}%"
    if t == "no_repeated_calls":
        return "No duplicate tool+args pairs"
    if t == "tool_output_contains":
        return f"'{p.get('tool_name','?')}' result contains '{p.get('text','?')}'"
    if t == "content_contains":
        return f"Response contains '{p.get('text','?')}'"
    if t == "content_not_contains":
        return f"Response does NOT contain '{p.get('text','?')}'"
    if t == "content_regex":
        return f"Response matches /{p.get('pattern','?')}/"
    if t == "latency":
        return f"Latency < {p.get('max_seconds', 30)}s"
    if t == "token_limit":
        return f"Total tokens < {p.get('max_tokens', 2000)}"
    if t == "max_iterations":
        return f"LLM rounds ≤ {p.get('max_iter', 3)}"
    if t == "tokens_per_second":
        return f"Throughput ≥ {p.get('min_tps', 5)} tok/s"
    if t == "path_efficiency":
        seq   = p.get("expected_sequence", "?")
        extra = p.get("allow_extra_steps", 0)
        bt    = p.get("penalize_backtracking", True)
        return f"Path [{seq}] + ≤{extra} extra" + (", no backtrack" if bt else "")
    if t == "goal_achievement":
        return "Agent fully achieved the task goal"
    if t == "tool_usage_efficiency":
        return f"Tool use efficient (≤ {p.get('max_calls', 5)} calls, no redundancy)"
    if t == "no_error_output":
        return "No hidden errors in tool output (exit=0 not misleading)"

    # Fallback: old-style criterion string
    return metric.get("criterion", "")


# ── Evaluation logic ─────────────────────────────────────────────────────────────

def evaluate_metric(metric: dict, telemetry: dict) -> bool | None:
    """
    Evaluate one metric against a completed-run telemetry dict.
    Returns True (pass), False (fail), or None (not enough data).
    """
    t = metric.get("type", "")
    p = metric.get("params", {})

    # ── task_completion ────────────────────────────────────────────────────────
    if t == "task_completion":
        return telemetry.get("validation_passed")

    # ── tool_called ────────────────────────────────────────────────────────────
    if t == "tool_called":
        tool = p.get("tool_name", "")
        if not tool:
            return None
        return any(tc["tool"] == tool for tc in telemetry.get("tool_calls", []))

    # ── tool_not_called ────────────────────────────────────────────────────────
    if t == "tool_not_called":
        tool = p.get("tool_name", "")
        if not tool:
            return None
        return not any(tc["tool"] == tool for tc in telemetry.get("tool_calls", []))

    # ── tool_sequence ──────────────────────────────────────────────────────────
    if t == "tool_sequence":
        seq_str = p.get("sequence", "")
        expected = [s.strip() for s in seq_str.split(",") if s.strip()]
        if not expected:
            return None
        actual = [tc["tool"] for tc in telemetry.get("tool_calls", [])]
        # expected must appear as an ordered subsequence of actual
        idx = 0
        for tool in expected:
            while idx < len(actual) and actual[idx] != tool:
                idx += 1
            if idx >= len(actual):
                return False
            idx += 1
        return True

    # ── tool_call_count ────────────────────────────────────────────────────────
    if t == "tool_call_count":
        return len(telemetry.get("tool_calls", [])) <= int(p.get("max_calls", 5))

    # ── tool_success_rate ──────────────────────────────────────────────────────
    if t == "tool_success_rate":
        calls = telemetry.get("tool_calls", [])
        if not calls:
            return None
        successes = sum(1 for tc in calls if tc.get("exit_code", 0) == 0)
        rate = successes / len(calls)
        return rate >= float(p.get("min_rate", 0.9))

    # ── no_repeated_calls ──────────────────────────────────────────────────────
    if t == "no_repeated_calls":
        return len(telemetry.get("inefficiencies", [])) == 0

    # ── tool_output_contains ───────────────────────────────────────────────────
    if t == "tool_output_contains":
        tool   = p.get("tool_name", "")
        needle = p.get("text", "")
        if not tool or not needle:
            return None
        for tc in telemetry.get("tool_calls", []):
            if tc["tool"] == tool:
                result_str = str(tc.get("result", "")).lower()
                if needle.lower() in result_str:
                    return True
        return False

    # ── content_contains ──────────────────────────────────────────────────────
    if t == "content_contains":
        text = p.get("text", "")
        if not text:
            return None
        return text.lower() in telemetry.get("llm_response", "").lower()

    # ── content_not_contains ──────────────────────────────────────────────────
    if t == "content_not_contains":
        text = p.get("text", "")
        if not text:
            return None
        return text.lower() not in telemetry.get("llm_response", "").lower()

    # ── content_regex ──────────────────────────────────────────────────────────
    if t == "content_regex":
        pattern = p.get("pattern", "")
        if not pattern:
            return None
        try:
            return bool(re.search(pattern, telemetry.get("llm_response", "")))
        except re.error:
            return None

    # ── latency ────────────────────────────────────────────────────────────────
    if t == "latency":
        return telemetry.get("total_latency", 0) < float(p.get("max_seconds", 30))

    # ── token_limit ────────────────────────────────────────────────────────────
    if t == "token_limit":
        return telemetry.get("total_tokens", 0) < int(p.get("max_tokens", 2000))

    # ── max_iterations ────────────────────────────────────────────────────────
    if t == "max_iterations":
        return telemetry.get("llm_rounds", 0) <= int(p.get("max_iter", 3))

    # ── tokens_per_second ────────────────────────────────────────────────────
    if t == "tokens_per_second":
        tps = telemetry.get("tokens_per_second", 0.0)
        if tps == 0:
            return None
        return tps >= float(p.get("min_tps", 5.0))

    # ── path_efficiency ───────────────────────────────────────────────────────
    if t == "path_efficiency":
        expected_str = p.get("expected_sequence", "")
        expected     = [s.strip() for s in expected_str.split(",") if s.strip()]
        allow_extra  = int(p.get("allow_extra_steps", 0))
        penalize_bt  = bool(p.get("penalize_backtracking", True))
        actual       = [tc["tool"] for tc in telemetry.get("tool_calls", [])]

        if not expected:
            return None

        # Check extra steps
        if len(actual) > len(expected) + allow_extra:
            return False

        # Check ordered subsequence
        idx = 0
        for tool in expected:
            while idx < len(actual) and actual[idx] != tool:
                idx += 1
            if idx >= len(actual):
                return False
            idx += 1

        # Backtracking: tool appeared again after it was already "done"
        if penalize_bt:
            seen = set()
            for tool in actual:
                if tool in seen:
                    return False
                seen.add(tool)

        return True

    # ── goal_achievement ─────────────────────────────────────────────────────
    # Composite: task completed + no inefficiencies + tool success rate 100%
    if t == "goal_achievement":
        passed      = telemetry.get("validation_passed")
        calls       = telemetry.get("tool_calls", [])
        inefficient = telemetry.get("inefficiencies", [])
        all_ok      = all(tc.get("exit_code", 0) == 0 for tc in calls)
        if passed is None:
            return None
        return bool(passed and not inefficient and all_ok)

    # ── tool_usage_efficiency ─────────────────────────────────────────────────
    if t == "tool_usage_efficiency":
        calls       = telemetry.get("tool_calls", [])
        max_calls   = int(p.get("max_calls", 5))
        inefficient = telemetry.get("inefficiencies", [])
        return len(calls) <= max_calls and len(inefficient) == 0

    # ── no_error_output ───────────────────────────────────────────────────────
    if t == "no_error_output":
        _ERROR_STRINGS = ("error", "exception", "traceback", "failed", "not found",
                          "permission denied", "no such file")
        for tc in telemetry.get("tool_calls", []):
            if tc.get("exit_code", 0) == 0:
                out = str(tc.get("result", "")).lower()
                if any(e in out for e in _ERROR_STRINGS):
                    return False
        return True

    # ── legacy fallback: old criterion-string metrics ─────────────────────────
    return _eval_legacy(metric, telemetry)


def _eval_legacy(metric: dict, telemetry: dict) -> bool | None:
    """Evaluate an old-style metric that has no 'type', only a 'criterion' string."""
    name      = metric.get("name", "").lower()
    criterion = metric.get("criterion", "").lower()

    if "completion" in name or "task" in name:
        return telemetry.get("validation_passed")

    if "tool call" in name:
        count = len(telemetry.get("tool_calls", []))
        nums  = re.findall(r"\d+", criterion)
        return count <= int(nums[0]) if nums else None

    if "repeated" in name or "inefficien" in name:
        return len(telemetry.get("inefficiencies", [])) == 0

    if "token" in name:
        total = telemetry.get("total_tokens", 0)
        nums  = re.findall(r"\d+", criterion)
        return total < int(nums[0]) if nums else None

    if "latency" in name or "time" in name:
        lat  = telemetry.get("total_latency", 0.0)
        nums = re.findall(r"[\d.]+", criterion)
        return lat < float(nums[0]) if nums else None

    return None
