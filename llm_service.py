import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None


def build_prompt(project_data, risk_data, swot_data, feasibility_score):
    prompt = f"""
You are a startup risk advisor. Based on the following project data, generate 3 to 5 actionable recommendations.

Project Name: {project_data.get('startup_name', 'Unknown')}
Industry: {project_data.get('industry', 'Unknown')}

Risk Factors:
- Market Competition: {risk_data.get('market_competition', 'Unknown')}
- Team Expertise: {risk_data.get('team_expertise', 'Unknown')}
- Resource Availability: {risk_data.get('resource_availability', 'Unknown')}
- Innovation Level: {risk_data.get('innovation_level', 'Unknown')}
- Market Research: {risk_data.get('market_research', 'Unknown')}
- Overall Risk Score: {risk_data.get('risk_score', 'Unknown')}

Feasibility Score: {feasibility_score}

SWOT Summary:
Strengths: {swot_data.get('strengths', [])}
Weaknesses: {swot_data.get('weaknesses', [])}
Opportunities: {swot_data.get('opportunities', [])}
Threats: {swot_data.get('threats', [])}

Return ONLY valid JSON, no extra text, no markdown formatting, in this exact format:
[
  {{
    "category": "Market",
    "title": "short title",
    "priority": "Critical" or "High" or "Medium",
    "problem": "one line problem statement",
    "action": "1-2 sentence concrete action",
    "risk_reduction": "1 sentence on how this action reduces risk"
  }}
]
"""
    return prompt


def generate_llm_recommendations(project_data, risk_data, swot_data, feasibility_score):
    if client is None:
        return None

    prompt = build_prompt(project_data, risk_data, swot_data, feasibility_score)
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )
        text = response.text.strip()

        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:]

        recommendations = json.loads(text)
        return recommendations

    except Exception as e:
        print("LLM recommendation generation failed:", e)
        return Noneimport os
import json
import re
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

def parse_dashboard_markdown(md_text):
    data = {
        "overall_risk": 50, "success_prob": 50, "market_risk": 50, 
        "financial_risk": 50, "tech_risk": 50,
        "key_findings": [], "risk_assessment": [], "recommendations": [],
        "funding_strategy": "N/A", "tech_advantage": "N/A", "next_steps": []
    }
    m = re.search(r'\*\*Overall Risk Score:\*\*\s*(\d+)', md_text)
    if m: data["overall_risk"] = int(m.group(1))
    m = re.search(r'\*\*Success Probability:\*\*\s*(\d+)', md_text)
    if m: data["success_prob"] = int(m.group(1))
    m = re.search(r'\*\*Market Risk:\*\*\s*(\d+)', md_text)
    if m: data["market_risk"] = int(m.group(1))
    m = re.search(r'\*\*Financial Risk:\*\*\s*(\d+)', md_text)
    if m: data["financial_risk"] = int(m.group(1))
    m = re.search(r'\*\*Technical Risk:\*\*\s*(\d+)', md_text)
    if m: data["tech_risk"] = int(m.group(1))
    findings_match = re.search(r'### Key Findings \(High Priority\)(.*?)(?=---|###)', md_text, re.DOTALL)
    if findings_match:
        items = re.findall(r'-\s*\*\*(.*?)\*\*\s*(.*)', findings_match.group(1))
        data["key_findings"] = [{"title": k.strip(': '), "desc": v.strip()} for k, v in items]
    risk_match = re.search(r'### Detailed Risk Assessment(.*)(?=---|###)', md_text, re.DOTALL)
    if risk_match:
        items = re.findall(r'-\s*\*\*(.*?)\*\*\s*(.*)', risk_match.group(1))
        data["risk_assessment"] = [{"title": k.strip(': '), "desc": v.strip()} for k, v in items]
    rec_match = re.search(r'### Strategic Recommendations \(Action Required\)(.*?)(?=---|###)', md_text, re.DOTALL)
    if rec_match:
        items = re.findall(r'\d+\.\s*(.*)', rec_match.group(1))
        data["recommendations"] = [item.strip() for item in items]
    insight_match = re.search(r'### Strategic Insights(.*?)(?=---|###)', md_text, re.DOTALL)
    if insight_match:
        f_match = re.search(r'\*\*Funding Strategy[^:]*:\*\*\s*(.*)', insight_match.group(1))
        if f_match: data["funding_strategy"] = f_match.group(1).strip()
        t_match = re.search(r'\*\*Technical Advantage[^:]*:\*\*\s*(.*)', insight_match.group(1))
        if t_match: data["tech_advantage"] = t_match.group(1).strip()
    next_match = re.search(r'### Recommended Next Steps(.*)', md_text, re.DOTALL)
    if next_match:
        items = re.findall(r'\d+\.\s*(.*)', next_match.group(1))
        data["next_steps"] = [item.strip() for item in items]
    return data

def generate_dashboard_report(project_data):
    if client is None:
        return None
    prompt = f"""
You are an expert Startup & Project Risk Analytics Engine. Your objective is to perform a rigorous, data-driven evaluation of a given project based on the user's input, calculate risk metrics, identify critical bottlenecks, and generate an actionable Executive Assessment Report.

### INPUT DATA PROVIDED:
- Project Name: {project_data.get('startup_name', 'Unknown')}
- Project Description: {project_data.get('project_description', 'Unknown')}
- Financial Data (Burn rate, runway, funding): Budget is ${project_data.get('budget', 0)}
- Market & Competitor Data: Target Market is {project_data.get('target_market', 'Unknown')}, Industry is {project_data.get('industry', 'Unknown')}
- Business Model: {project_data.get('business_model', 'Unknown')}

### INSTRUCTIONS:
Analyze the input data holistically and compute/generate the following sections:
1. METRICS & RISK SCORES
2. KEY FINDINGS (High Priority)
3. DETAILED RISK ASSESSMENT
4. STRATEGIC RECOMMENDATIONS (Action Required)
5. STRATEGIC INSIGHTS
6. RECOMMENDED NEXT STEPS

### OUTPUT FORMAT:
Return the assessment strictly structured in the following Markdown format:

## Dashboard & Deployment Assessment Report

### Risk Analytics Summary
* **Overall Risk Score:** {{OVERALL_RISK_PERCENT}}%
* **Success Probability:** {{SUCCESS_PROBABILITY_PERCENT}}%
* **Market Risk:** {{MARKET_RISK_PERCENT}}%
* **Financial Risk:** {{FINANCIAL_RISK_PERCENT}}%
* **Technical Risk:** {{TECHNICAL_RISK_PERCENT}}%

---

### Key Findings (High Priority)
- **Market Saturation:** [Summary of market competition and saturation threat]
- **Budget Runway:** [Current runway estimate and burn rate status]
- **Team Gaps:** [Key missing skill sets or domain expertise]
- **Differentiation:** [Unique Value Proposition assessment]

---

### Detailed Risk Assessment
- **Market Risk ({{MARKET_RISK_PERCENT}}%):** [Breakdown of CAC, market size, and adoption barriers]
- **Financial Risk ({{FINANCIAL_RISK_PERCENT}}%):** [Breakdown of financial runway, cash projections, and capital requirements]
- **Technical Risk ({{TECHNICAL_RISK_PERCENT}}%):** [Breakdown of tech feasibility and engineering capacity]

---

### Strategic Recommendations (Action Required)
1. [Recommendation 1 - Niche focus / Market strategy]
2. [Recommendation 2 - Capital / Revenue strategy]
3. [Recommendation 3 - Team / Talent acquisition strategy]
4. [Recommendation 4 - MVP / Product validation milestone]

---

### Strategic Insights
* **Funding Strategy (Critical Impact):** [Funding or revenue strategy insight]
* **Technical Advantage (Medium Impact):** [Core technical differentiator or moat leverage]

---

### Recommended Next Steps
1. [Immediate step 1]
2. [Immediate step 2]
3. [Immediate step 3]
"""
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )
        text = response.text.strip()
        parsed = parse_dashboard_markdown(text)
        return parsed
    except Exception as e:
        print("Dashboard generation failed:", e)
        return None

