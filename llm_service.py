import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

_client = None

if GEMINI_API_KEY:
    try:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception:
        _client = None


def is_llm_available():
    """Return True when Gemini is configured and available."""
    return _client is not None


# ============================================================
# GEMINI JSON GENERATION
# ============================================================

def _generate_json(prompt, schema):
    """
    Send a prompt to Gemini and return structured JSON.

    Returns:
        dict | None
    """

    if not _client:
        return None

    try:
        response = _client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                temperature=0.4,
            ),
        )

        if not response.text:
            return None

        return json.loads(response.text)

    except Exception as error:
        print(f"Gemini API error: {error}")
        return None


# ============================================================
# PROJECT ANALYSIS
# ============================================================

def generate_project_analysis(project_data):
    """
    Generate an AI-based high-level analysis of the submitted project.

    This is used during project submission and provides:
    - project summary
    - market considerations
    - competitive considerations
    - initial risk observations
    """

    if not is_llm_available():
        return {
            "mode": "DEMO",
            "project_summary": (
                f"{project_data.get('startup_name', 'Project')} "
                f"is a {project_data.get('business_model', 'business')} "
                f"project operating in the "
                f"{project_data.get('industry', 'technology')} sector."
            ),
            "market_observations": [
                "Validate target customer demand before major investment.",
                "Assess the size and growth potential of the target market.",
                "Monitor competitor positioning and differentiation."
            ],
            "initial_risk_observations": [
                "Market acceptance risk",
                "Competitive risk",
                "Resource and execution risk"
            ]
        }

    schema = {
        "type": "object",
        "properties": {
            "project_summary": {
                "type": "string"
            },
            "market_observations": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "initial_risk_observations": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        },
        "required": [
            "project_summary",
            "market_observations",
            "initial_risk_observations"
        ]
    }

    prompt = f"""
You are an expert startup and project risk analyst.

Analyze the following project.

PROJECT DATA:
{json.dumps(project_data, indent=2, default=str)}

Provide:
1. A concise project summary.
2. Important market observations.
3. Initial risk observations.

Do not invent specific market statistics or competitor numbers.
Base the analysis only on the information provided.
"""

    result = _generate_json(prompt, schema)

    if result is None:
        return {
            "mode": "DEMO",
            "project_summary": "AI analysis unavailable.",
            "market_observations": [],
            "initial_risk_observations": []
        }

    result["mode"] = "GEMINI"

    return result


# ============================================================
# M3 STRATEGIC RECOMMENDATIONS
# ============================================================

def generate_llm_recommendations(
    project_data,
    risk_input_data,
    swot,
    feasibility_score,
    market_data=None,
    risk_data=None,
    base_recommendations=None
):
    """
    Generate M3 strategic recommendations using Gemini.

    The output structure intentionally matches the existing
    recommendation/dashboard structure.
    """

    # --------------------------------------------------------
    # DEMO MODE
    # --------------------------------------------------------

    if not is_llm_available():

        if base_recommendations:
            result = dict(base_recommendations)
            result["mode"] = "DEMO"
            return result

        return {
            "mode": "DEMO",
            "overall_strategic_recommendation": (
                "Address the highest-priority risks first, "
                "validate market demand, strengthen execution "
                "capability, and control resource allocation."
            ),
            "recommendations": [],
            "short_term_action_plan": [
                "Validate the target customer problem.",
                "Review the highest-priority project risks.",
                "Validate budget and resource assumptions."
            ],
            "long_term_action_plan": [
                "Build sustainable competitive differentiation.",
                "Scale only after validating product-market fit.",
                "Establish continuous risk monitoring."
            ]
        }

    # --------------------------------------------------------
    # GEMINI SCHEMA
    # --------------------------------------------------------

    schema = {
        "type": "object",
        "properties": {
            "overall_strategic_recommendation": {
                "type": "string"
            },

            "recommendations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string"
                        },
                        "category": {
                            "type": "string"
                        },
                        "priority": {
                            "type": "string"
                        },
                        "problem": {
                            "type": "string"
                        },
                        "explanation": {
                            "type": "string"
                        },
                        "action": {
                            "type": "string"
                        },
                        "risk_reduction": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "title",
                        "category",
                        "priority",
                        "problem",
                        "explanation",
                        "action",
                        "risk_reduction"
                    ]
                }
            },

            "short_term_action_plan": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },

            "long_term_action_plan": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        },
        "required": [
            "overall_strategic_recommendation",
            "recommendations",
            "short_term_action_plan",
            "long_term_action_plan"
        ]
    }

    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are the AI Strategic Recommendation Engine for a
Startup & Project Risk Analyzer.

Your job is to analyze the project and produce practical,
risk-linked strategic recommendations.

IMPORTANT:
- Do not invent facts.
- Use the supplied project information.
- Recommendations must be directly connected to identified risks.
- Every recommendation must explain:
  1. the problem/risk,
  2. why it matters,
  3. what should be done,
  4. how the action reduces risk.
- Prioritize the most important risks.
- Be practical and specific.
- Avoid generic motivational advice.
- Do not claim certainty about business success.

PROJECT INFORMATION:
{json.dumps(project_data, indent=2, default=str)}

RISK INPUTS:
{json.dumps(risk_input_data, indent=2, default=str)}

OVERALL RISK SCORE:
{json.dumps({
    "risk_score": risk_input_data.get("risk_score"),
    "feasibility_score": feasibility_score
}, indent=2, default=str)}

SWOT:
{json.dumps(swot, indent=2, default=str)}

MARKET DATA:
{json.dumps(market_data or {}, indent=2, default=str)}

IDENTIFIED RISKS:
{json.dumps(risk_data or [], indent=2, default=str)}

EXISTING BASELINE RECOMMENDATIONS:
{json.dumps(base_recommendations or {}, indent=2, default=str)}

Generate:

A. Overall Strategic Recommendation

B. Strategic Recommendations

Each recommendation must contain:
- title
- category
- priority
- problem
- explanation
- action
- risk_reduction

Categories may include:
- Risk
- Market
- Technical
- Financial
- Operational
- Product
- Marketing

C. Short-Term Action Plan

D. Long-Term Action Plan

Return ONLY the requested structured JSON.
"""

    result = _generate_json(prompt, schema)

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    if result is None:

        if base_recommendations:
            fallback = dict(base_recommendations)
            fallback["mode"] = "FALLBACK"
            return fallback

        return {
            "mode": "FALLBACK",
            "overall_strategic_recommendation": (
                "Review the highest-priority risks and implement "
                "targeted mitigation actions before scaling."
            ),
            "recommendations": [],
            "short_term_action_plan": [],
            "long_term_action_plan": []
        }

    result["mode"] = "GEMINI"

    return result