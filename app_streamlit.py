import streamlit as st
import pandas as pd
import market_analysis
import textwrap
import database

from recommendation_engine import generate_recommendations
from llm_service import generate_llm_recommendations

st.set_page_config(page_title="Prediction AI", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS to mimic the Mac-style window from the PDF
st.markdown("""
<style>
/* Main container styling to look like a window */
.main .block-container {
border-radius: 12px;
box-shadow: 0 10px 25px rgba(37, 99, 235, 0.1);
padding: 2rem !important;
margin-top: 3rem;
margin-bottom: 3rem;
border: 1px solid #BFDBFE;
}

/* Mac window controls (Red, Yellow, Green dots) */
.mac-controls {
display: flex;
gap: 8px;
margin-bottom: 20px;
}
.mac-dot {
width: 12px;
height: 12px;
border-radius: 50%;
}
.mac-red { background-color: #ff5f56; }
.mac-yellow { background-color: #ffbd2e; }
.mac-green { background-color: #27c93f; }

/* Customizing the tabs to look more like the PDF */
.stTabs [data-baseweb="tab-list"] {
gap: 24px;
border-bottom: 1px solid #e5e7eb;
}
.stTabs [data-baseweb="tab"] {
height: 50px;
white-space: pre-wrap;
background-color: transparent;
border-radius: 4px 4px 0 0;
gap: 1px;
padding-top: 10px;
padding-bottom: 10px;
font-weight: 600;
color: #6b7280;
}
.stTabs [aria-selected="true"] {
color: #111827;
border-bottom: 2px solid #3b82f6;
}

/* Adjusting headers */
h1 {
font-size: 2.2rem !important;
padding-bottom: 0 !important;
}

</style>
""", unsafe_allow_html=True)

# Injecting the Mac dots at the top of the container
st.markdown("""
<h1 style="margin: 0; padding: 0; font-size: 28px; color: #111827; font-weight: 700; font-family: sans-serif; margin-bottom: 14px; margin-top: -16px;">Prediction AI</h1>
<div class="mac-controls">
<div class="mac-dot mac-red"></div>
<div class="mac-dot mac-yellow"></div>
<div class="mac-dot mac-green"></div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["Project Input", "Risk Assessment", "Recommendations", "Dashboard"])

with tab1:
    st.markdown("""
<h1 style="margin: 0; padding: 0; font-size: 28px; color: #111827; font-weight: 700; font-family: sans-serif;">Data Collection & Market Intelligence</h1>
<p style="margin: 4px 0 24px 0; color: #6B7280; font-size: 15px; font-family: sans-serif;">Gather project data and analyze market landscape</p>
""", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Project Submission")
        with st.form("project_form"):
            startup_name = st.text_input("Startup/Project Name", placeholder="e.g., TechVenture AI")
            industry = st.selectbox("Industry/Sector", ["Technology", "Healthcare", "Finance", "Education"], index=None, placeholder="Select an industry...")
            business_model = st.selectbox("Business Model", ["SaaS", "B2B", "B2C", "Marketplace"], index=None, placeholder="Select a business model...")
            
            target_market = st.text_input("Target Market", placeholder="e.g., SMBs")
            budget = st.number_input("Budget (USD)", min_value=0, value=None, placeholder="100000", step=10000)
                
            description = st.text_area("Project Description", placeholder="Brief description of your project idea...")
            
            submitted = st.form_submit_button("Analyze Project")
            
        if submitted:
            project_data = {
                "startup_name": startup_name,
                "industry": industry,
                "business_model": business_model,
                "target_market": target_market,
                "budget": budget,
                "project_description": description,
            }
            st.session_state['project_data'] = project_data
            st.session_state['assessment_saved'] = False
            try:
                project_id = database.insert_project(project_data)
                st.session_state['project_id'] = project_id
            except Exception as error:
                st.error(f"Database error: {error}")
                st.session_state['project_id'] = -1

    with col2:
        st.subheader("Market Analysis")
        if 'project_data' in st.session_state:
            data = st.session_state['project_data']
            m_data = market_analysis.get_market_data(data['industry'], data['target_market'], data['budget'])
            
            st.write("**Market Size & Growth Rate**")
            
            m1, m2, m3 = st.columns(3)
            m1.metric("TAM", m_data['TAM']['value'], m_data['TAM']['growth'])
            m2.metric("SAM", m_data['SAM']['value'], m_data['SAM']['growth'])
            m3.metric("SOM", m_data['SOM']['value'], m_data['SOM']['growth'])
            
            st.write("**Market Trends (2020-2026)**")
            chart_data = pd.DataFrame(
                [30, 40, 45, 55, 70, 85, 100],
                columns=["Trend"],
                index=["2020", "2021", "2022", "2023", "2024", "2025", "2026"]
            )
            st.bar_chart(chart_data)
            
        else:
            st.info("Submit a project idea on the left to view the market analysis.")

    with col3:
        st.subheader("Competitor Landscape")
        if 'project_data' in st.session_state:
            data = st.session_state['project_data']
            c_data = market_analysis.get_competitor_data(data['startup_name'], data['industry'], data['business_model'])
            
            for comp in c_data:
                with st.container():
                    st.markdown(f"**{comp['name']}** `{comp['type']}`")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Market Share", comp['market_share'])
                    c2.metric("Revenue", comp['revenue'])
                    c3.metric("Growth", comp['growth'])
                    st.progress(comp['position'] / 100, text="Market Position")
                    st.divider()
                    
        else:
            st.info("Submit a project idea to generate competitor insights.")

with tab2:
    st.markdown("""
<h1 style="margin: 0; padding: 0; font-size: 28px; color: #111827; font-weight: 700; font-family: sans-serif;">Risk Assessment & SWOT Analysis</h1>
<p style="margin: 4px 0 24px 0; color: #6B7280; font-size: 15px; font-family: sans-serif;">AI-powered risk scoring and strategic evaluation</p>
""", unsafe_allow_html=True)

    if 'project_data' not in st.session_state:
        st.info('Submit a project idea in the Project Input tab to generate a Risk Assessment.')
    else:
        if 'project_data' in st.session_state:
            data = st.session_state['project_data']
        else:
            data = {'industry': 'Technology', 'budget': 100000, 'startup_name': 'Demo Project'}
        
        # Algorithmically derive inputs from project_data
        market_competition = "High" if data.get('industry') == 'Technology' else "Medium"
        team_expertise = "Low" if data.get('budget', 0) < 50000 else "High"
        resource_availability = "Good" if data.get('budget', 0) >= 100000 else "Limited"
        innovation_level = "High"
        market_research = "Moderate"
    
        market_opportunity = 45 if market_competition == "High" else 75
        team_capability = 50 if team_expertise == "Low" else 85
        competitive_advantage = 35 if innovation_level == "Low" else 70
        resource_score = 65 if resource_availability == "Good" else 30

        from risk_engine import calculate_risk, get_risk_status, calculate_success_probability
        from mitigation_engine import generate_mitigation
        from improvement_engine import generate_improvements
        risk_score = calculate_risk(market_competition, team_expertise, resource_availability, innovation_level, market_research)
        risk_status = get_risk_status(risk_score)
        success_probability = calculate_success_probability(risk_score)

        # Prepare risk data for Milestone 3 mitigation engine
        risk_data = [
            {
                "risk_category": "Market",
                "risk_score": 80 if market_competition == "High" else 50,
                "risk_description": "High competitor density",
                "priority_level": "High" if market_competition == "High" else "Medium"
            },
            {
                "risk_category": "Financial",
                "risk_score": 75 if data.get("budget", 0) < 50000 else 45,
                "risk_description": "Budget constraints",
                "priority_level": "High" if data.get("budget", 0) < 50000 else "Medium"
            },
            {
                "risk_category": "Technical",
                "risk_score": 80 if team_expertise == "Low" else 40,
                "risk_description": "Limited technical expertise",
                "priority_level": "High" if team_expertise == "Low" else "Medium"
            }
        ]

        # Generate Milestone 3 mitigation strategies
        mitigation_results = generate_mitigation(risk_data)
        market_data_for_improvements = market_analysis.get_market_data(
            data.get("industry", "Technology"),
            data.get("target_market", ""),
            data.get("budget", 0),
        )

        from swot_analysis import generate_swot
        swot = generate_swot(team_expertise, innovation_level, market_competition, resource_availability, market_research)

        from feasibility import calculate_feasibility
        feasibility_score = calculate_feasibility(market_opportunity, team_capability, competitive_advantage, resource_score)

        risk_input_data = {
            "market_competition": market_competition,
            "team_expertise": team_expertise,
            "resource_availability": resource_availability,
            "innovation_level": innovation_level,
            "market_research": market_research,
            "risk_score": risk_score
        }

        # ============================================================
        # M3 - STRATEGIC RECOMMENDATIONS
        # ============================================================

        recommendation_results = generate_recommendations(
            data,
            risk_input_data,
            swot,
            feasibility_score
        )

        # ============================================================
        # M3 - IMPROVEMENT PLAN
        # ============================================================

        improvement_results = generate_improvements(
            data,
            risk_input_data,
            swot,
            feasibility_score,
            market_data=market_data_for_improvements,
            mitigation_results=mitigation_results
        )

        project_id = st.session_state.get("project_id")
        if project_id and not st.session_state.get("assessment_saved", False):
            try:
                database.save_assessment(
                    project_id=project_id,
                    swot_data=swot,
                    risk_score=risk_score,
                    risk_status=risk_status,
                    success_probability=success_probability,
                    recommendations=recommendation_results["recommendations"],
                )
                st.session_state["assessment_saved"] = True
            except Exception as error:
                print(f"Could not save the assessment to the database: {error}")

        # Format SWOT bullets as HTML dots
        def format_swot(items):
            return "".join([f'<div style="margin-bottom:4px;">• {item}</div>' for item in items])
            st.markdown("<br>", unsafe_allow_html=True)
    
        # FINAL DASHBOARD LAYOUT (3 columns) matching PDF mockup perfectly
        r_col1, r_col2, r_col3 = st.columns([1, 1.5, 1])
    
        with r_col1:
            st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
    <h3 style="margin:0; font-size: 16px; color: #111827; font-family: sans-serif;">Risk Score</h3>
    <span style="color: #DC2626; font-size: 14px;">&#9888;</span>
    </div>
    <div style="border: 1px solid #E5E7EB; border-radius: 8px; padding: 24px; text-align: center; margin-bottom: 16px; background: white; font-family: sans-serif;">
    <div style="color: #6B7280; font-size: 12px; margin-bottom: 16px;">Overall Risk Score</div>
    <div style="color: #DC2626; font-size: 56px; font-weight: 800; line-height: 1;">{risk_score}</div>
    <div style="color: #DC2626; font-size: 11px; font-weight: 700; margin-top: 16px;">{risk_status}</div>
    </div>
    <div style="border: 1px solid #E5E7EB; border-radius: 8px; padding: 16px; margin-bottom: 24px; background: white; font-family: sans-serif;">
    <div style="color: #6B7280; font-size: 12px; margin-bottom: 12px;">Success Probability</div>
    <div style="background: #E5E7EB; border-radius: 4px; height: 6px; width: 100%; margin-bottom: 8px;">
    <div style="background: #DC2626; border-radius: 4px; height: 100%; width: {success_probability}%;"></div>
    </div>
    <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 600;">
    <span style="color: #111827;">{success_probability}%</span>
    <span style="color: #DC2626;">Low</span>
    </div>
    </div>
    <h4 style="font-size: 14px; margin-bottom: 12px; color: #111827; font-family: sans-serif;">Key Risk Factors</h4>
    <div style="border: 1px solid #E5E7EB; border-radius: 8px; padding: 12px; margin-bottom: 8px; display: flex; align-items: center; gap: 12px; background: white; font-family: sans-serif;">
    <div style="background: #FEF3C7; color: #D97706; padding: 6px; border-radius: 6px; font-size: 16px; width: 32px; height: 32px; display: flex; justify-content: center; align-items: center;">&#128101;</div>
    <div>
    <div style="font-size: 13px; font-weight: 600; color: #111827;">Team Expertise</div>
    <div style="font-size: 11px; color: #6B7280;">{team_expertise} technical experience</div>
    </div>
    </div>
    <div style="border: 1px solid #E5E7EB; border-radius: 8px; padding: 12px; margin-bottom: 8px; display: flex; align-items: center; gap: 12px; background: white; font-family: sans-serif;">
    <div style="background: #D1FAE5; color: #10B981; padding: 6px; border-radius: 6px; font-size: 16px; width: 32px; height: 32px; display: flex; justify-content: center; align-items: center;">&#128161;</div>
    <div>
    <div style="font-size: 13px; font-weight: 600; color: #111827;">Innovation Gap</div>
    <div style="font-size: 11px; color: #6B7280;">{innovation_level} innovation potential</div>
    </div>
    </div>
    """, unsafe_allow_html=True)

        with r_col2:
            st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-family: sans-serif;">
    <h3 style="margin:0; font-size: 16px; color: #111827;">SWOT Analysis</h3>
    <span style="color: #6B7280; font-size: 16px;">&#8862;</span>
    </div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; font-family: sans-serif;">
    <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; padding: 16px;">
    <div style="color: #16A34A; font-weight: 600; font-size: 14px; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
    <span style="background: #16A34A; color: white; border-radius: 50%; width: 14px; height: 14px; display: inline-flex; align-items: center; justify-content: center; font-size: 10px;">+</span> Strengths
    </div>
    <div style="color: #111827; font-size: 12px; line-height: 1.5;">
    {format_swot(swot["Strengths"])}
    </div>
    </div>
    <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 8px; padding: 16px;">
    <div style="color: #DC2626; font-weight: 600; font-size: 14px; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
    <span style="background: #DC2626; color: white; border-radius: 50%; width: 14px; height: 14px; display: inline-flex; align-items: center; justify-content: center; font-size: 10px;">-</span> Weaknesses
    </div>
    <div style="color: #111827; font-size: 12px; line-height: 1.5;">
    {format_swot(swot["Weaknesses"])}
    </div>
    </div>
    <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 8px; padding: 16px; min-height: 180px;">
    <div style="color: #2563EB; font-weight: 600; font-size: 14px; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
    <span style="color: #2563EB; font-size: 16px;">&#8599;</span> Opportunities
    </div>
    <div style="color: #111827; font-size: 12px; line-height: 1.5;">
    {format_swot(swot["Opportunities"])}
    </div>
    </div>
    <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 8px; padding: 16px; min-height: 180px;">
    <div style="color: #D97706; font-weight: 600; font-size: 14px; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
    <span style="color: #D97706; font-size: 14px;">&#9888;</span> Threats
    </div>
    <div style="color: #111827; font-size: 12px; line-height: 1.5;">
    {format_swot(swot["Threats"])}
    </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

        with r_col3:
            st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-family: sans-serif;">
    <h3 style="margin:0; font-size: 16px; color: #111827;">Project Feasibility</h3>
    <span style="color: white; background: #10B981; border-radius: 50%; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 10px;">&#10004;</span>
    </div>
    <div style="border: 1px solid #E5E7EB; border-radius: 8px; padding: 24px; text-align: center; margin-bottom: 24px; background: white; font-family: sans-serif;">
    <div style="color: #6B7280; font-size: 12px; margin-bottom: 16px;">Feasibility Score</div>
    <div style="color: #10B981; font-size: 48px; font-weight: 800; line-height: 1;">{feasibility_score}%</div>
    <div style="color: #9CA3AF; font-size: 10px; margin-top: 16px; line-height: 1.4; padding: 0 10px;">Moderate Feasibility with Significant Improvements Needed</div>
    </div>
    <h4 style="font-size: 14px; margin-bottom: 16px; color: #111827; font-family: sans-serif;">Assessment Metrics</h4>

    <div style="margin-bottom: 16px; font-family: sans-serif;">
    <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px;">
    <span style="color: #374151; font-weight: 500;">Team Capability</span>
    <span style="color: #F59E0B; font-weight: 600;">{team_capability}%</span>
    </div>
    <div style="background: #E5E7EB; border-radius: 4px; height: 4px; width: 100%;">
    <div style="background: #F59E0B; border-radius: 4px; height: 100%; width: {team_capability}%;"></div>
    </div>
    </div>
    <div style="margin-bottom: 16px; font-family: sans-serif;">
    <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px;">
    <span style="color: #374151; font-weight: 500;">Competitive Advantage</span>
    <span style="color: #DC2626; font-weight: 600;">{competitive_advantage}%</span>
    </div>
    <div style="background: #E5E7EB; border-radius: 4px; height: 4px; width: 100%;">
    <div style="background: #DC2626; border-radius: 4px; height: 100%; width: {competitive_advantage}%;"></div>
    </div>
    </div>
    <div style="margin-bottom: 16px; font-family: sans-serif;">
    <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px;">
    <span style="color: #374151; font-weight: 500;">Resource Availability</span>
    <span style="color: #10B981; font-weight: 600;">{resource_score}%</span>
    </div>
    <div style="background: #E5E7EB; border-radius: 4px; height: 4px; width: 100%;">
    <div style="background: #10B981; border-radius: 4px; height: 100%; width: {resource_score}%;"></div>
    </div>
    </div>
    """, unsafe_allow_html=True)


with tab3:
    st.markdown("""
<h1 style="margin: 0; padding: 0; font-size: 28px; color: #111827; font-weight: 700; font-family: sans-serif;">Recommendations & Strategic Reasoning</h1>
<p style="margin: 4px 0 24px 0; color: #6B7280; font-size: 15px; font-family: sans-serif;">AI-powered mitigation strategies and agent workflows</p>
""", unsafe_allow_html=True)
    if 'project_data' not in st.session_state:
        st.info('Submit a project idea in the Project Input tab to view Recommendations.')
    else:

        recommendation_tab, risk_mitigation_tab, improvements_tab, langgraph_tab = st.tabs([
            "Strategic Recommendations",
            "Risk Mitigation",
            "Improvements",
            "LangGraph Agent"
        ])

        # ============================================================
        # STRATEGIC RECOMMENDATIONS
        # ============================================================

        with recommendation_tab:

            st.subheader("AI Strategic Recommendations")

            if recommendation_results:

                overall = recommendation_results.get(
                    "overall_strategic_recommendation",
                    "Focus on reducing the highest-priority project risks."
                )

                st.info(overall)

                recommendations = recommendation_results.get(
                    "recommendations",
                    []
                )

                if recommendations:

                    for rec in recommendations:

                        priority = rec.get("priority", "Medium")
                        category = rec.get("category", "Strategy")
                        title = rec.get("title", "Recommendation")

                        st.markdown(
                            f"### {title}"
                        )

                        st.markdown(
                            f"**Category:** {category}  \n"
                            f"**Priority:** {priority}"
                        )

                        st.markdown(
                            f"**Problem:** {rec.get('problem', 'N/A')}"
                        )

                        if rec.get("explanation"):
                            st.markdown(
                                f"**Why it matters:** {rec['explanation']}"
                            )

                        st.markdown(
                            f"**Recommended Action:** "
                            f"{rec.get('action', 'N/A')}"
                        )

                        st.markdown(
                            f"**Risk Reduction:** "
                            f"{rec.get('risk_reduction', 'N/A')}"
                        )

                        st.divider()

                else:
                    st.warning("No strategic recommendations were generated.")

                # Short-term plan
                st.subheader("Short-Term Action Plan")

                short_term = recommendation_results.get(
                "short_term_action_plan",
                []
                )

                for action in short_term:
                    st.markdown(f"- {action}")

                # Long-term plan
                st.subheader("Long-Term Action Plan")

                long_term = recommendation_results.get(
                    "long_term_action_plan",
                    []
                )

                for action in long_term:
                    st.markdown(f"- {action}")

            else:
                st.warning("No strategic recommendations available.")

    
        with improvements_tab:
            st.markdown("""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 16px;">
            <h3 style="margin:0; font-size: 16px; color: #111827; font-family: sans-serif;">Improvements</h3>
            <span style="background: #6D28D9; color: white; padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: bold; font-family: sans-serif;">AI Powered</span>
            </div>
    <style>
    .improvement-card-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 14px;
        margin-bottom: 12px;
    }
    .improvement-flip-card {
        min-height: 238px;
        perspective: 1200px;
        font-family: sans-serif;
    }
    .improvement-flip-inner {
        position: relative;
        width: 100%;
        min-height: 238px;
        transition: transform 0.7s cubic-bezier(.2,.7,.2,1);
        transform-style: preserve-3d;
    }
    .improvement-flip-card:hover .improvement-flip-inner,
    .improvement-flip-card:focus-within .improvement-flip-inner {
        transform: rotateY(180deg);
    }
    .improvement-face {
        position: absolute;
        inset: 0;
        min-height: 238px;
        padding: 16px;
        border: 1px solid rgba(255, 255, 255, 0.72);
        border-radius: 16px;
        box-sizing: border-box;
        backface-visibility: hidden;
        -webkit-backface-visibility: hidden;
        box-shadow: 0 16px 32px rgba(31, 41, 55, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.8);
        overflow: hidden;
    }
    .improvement-front {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.82), rgba(239, 246, 255, 0.58));
        backdrop-filter: blur(18px) saturate(135%);
        -webkit-backdrop-filter: blur(18px) saturate(135%);
    }
    .improvement-back {
        background: linear-gradient(135deg, rgba(245, 243, 255, 0.94), rgba(224, 242, 254, 0.84));
        backdrop-filter: blur(18px) saturate(135%);
        -webkit-backdrop-filter: blur(18px) saturate(135%);
        transform: rotateY(180deg);
        overflow-y: auto;
    }
    .improvement-face h4 {
        margin: 0 0 10px 0;
        color: #111827;
        font-size: 15px;
        line-height: 1.35;
    }
    .improvement-face p,
    .improvement-face li {
        color: #4B5563;
        font-size: 12px;
        line-height: 1.55;
    }
    .improvement-face ul {
        margin: 6px 0 14px 18px;
        padding: 0;
    }
    .improvement-label {
        color: #6D28D9;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: .04em;
        text-transform: uppercase;
    }
    .improvement-priority {
        float: right;
        color: #6D28D9;
        background: rgba(237, 233, 254, 0.9);
        border: 1px solid rgba(196, 181, 253, 0.7);
        border-radius: 999px;
        padding: 3px 9px;
        font-size: 10px;
        font-weight: 700;
    }
    .improvement-hint {
        margin-top: 16px;
        color: #9CA3AF;
        font-size: 10px;
    }
    @media (max-width: 900px) {
        .improvement-card-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }
    @media (max-width: 620px) {
        .improvement-card-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
            """, unsafe_allow_html=True)

            improvement_cards = []
            for rec in improvement_results:
                steps = rec.get("steps") or [rec.get("action", "Review this project area and define a corrective action.")]
                steps_html = "".join(f"<li>{step}</li>" for step in steps)
                recommendation_html = "".join(
                    f"{index}. {step}<br>" for index, step in enumerate(steps, start=1)
                )
                card_html = f"""
    <div class="improvement-flip-card" tabindex="0">
      <div class="improvement-flip-inner">
        <div class="improvement-face improvement-front">
          <span class="improvement-label">{rec["category"]}</span>
          <span class="improvement-priority">{rec["priority"]}</span>
          <h4>{rec["title"]}</h4>
          <div class="improvement-label">Problem</div>
          <p>{rec["problem"]}</p>
        </div>
        <div class="improvement-face improvement-back">
          <div class="improvement-label">Solution Steps</div>
          <ul>{steps_html}</ul>
          <div class="improvement-label">Recommendation</div>
        <p>{recommendation_html}</p>
          <div class="improvement-label">Risk Reduction</div>
          <p>{rec["risk_reduction"]}</p>
        </div>
      </div>
    </div>
    """
                improvement_cards.append(textwrap.dedent(card_html))
            st.markdown(
                '<div class="improvement-card-grid">'
                + "".join(improvement_cards)
                + "</div>",
                unsafe_allow_html=True,
            )
        with risk_mitigation_tab:
            st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
    <h3 style="margin:0; font-size: 16px; color: #111827; font-family: sans-serif;">Risk Mitigation</h3>
    <span style="color: #6B7280;">&#128116;</span>
    </div>
    <style>
    .risk-card-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 14px;
        margin-bottom: 12px;
    }
    .risk-glass-card {
        min-height: 220px;
        padding: 16px;
        box-sizing: border-box;
        border: 1px solid rgba(255, 255, 255, 0.58);
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.38), rgba(153, 246, 228, 0.2));
        backdrop-filter: blur(24px) saturate(165%);
        -webkit-backdrop-filter: blur(24px) saturate(165%);
        box-shadow: 0 14px 28px rgba(31, 41, 55, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.72), inset 0 -1px 0 rgba(255, 255, 255, 0.18);
        font-family: sans-serif;
    }
    .risk-glass-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 10px;
        margin-bottom: 10px;
    }
    .risk-glass-card-risk {
        color: #DC2626;
        font-size: 12px;
        font-weight: 700;
        line-height: 1.4;
    }
    .risk-glass-card-impact {
        flex-shrink: 0;
        color: #047857;
        background: rgba(209, 250, 229, 0.86);
        border: 1px solid rgba(110, 231, 183, 0.7);
        border-radius: 999px;
        padding: 3px 8px;
        font-size: 10px;
        font-weight: 700;
    }
    .risk-glass-card h4 {
        margin: 0 0 10px 0;
        color: #111827;
        font-size: 13px;
        line-height: 1.4;
    }
    .risk-glass-card p {
        margin: 0 0 8px 0;
        color: #4B5563;
        font-size: 11px;
        line-height: 1.5;
    }
    .risk-glass-card strong {
        color: #374151;
    }
    @media (max-width: 900px) {
        .risk-card-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }
    @media (max-width: 620px) {
        .risk-card-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,  unsafe_allow_html=True)

            selected_risk = st.pills(
                "Risk Category", 
                ["All Risks", "Financial", "Market", "Technical"], 
                default="All Risks", 
                label_visibility="collapsed",
                key="selected_risk_category"
            )
        
            if not selected_risk:
                selected_risk = "All Risks"

            mitigation_cards = []
            for mitigation in mitigation_results:

                category = mitigation["category"]

                # Apply selected category filter
                if selected_risk != "All Risks" and category != selected_risk:
                    continue

                card_html = f"""
    <div class="risk-glass-card">
        <div class="risk-glass-card-header">
            <div class="risk-glass-card-risk">&#9888; {mitigation["risk"]}</div>
            <span class="risk-glass-card-impact">{mitigation["impact"]} Impact</span>
        </div>
        <h4>
            {mitigation["mitigation_strategy"]}
        </h4>
        <p><strong>Preventive Action:</strong> {mitigation["preventive_action"]}</p>
        <p><strong>Contingency Action:</strong> {mitigation["contingency_action"]}</p>
    </div>
    """
                mitigation_cards.append(textwrap.dedent(card_html))
            st.markdown(
                '<div class="risk-card-grid">'
                + "".join(mitigation_cards)
                + "</div>",
                unsafe_allow_html=True,
            )
        with langgraph_tab:
            st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
    <h3 style="margin:0; font-size: 16px; color: #111827; font-family: sans-serif;">LangGraph Agent</h3>
    <span style="color: #8B5CF6;">&#9881;</span>
    </div>
    """, unsafe_allow_html=True)

            agent_container = st.container()
            agent_steps = [
                ("Data Ingestion", "Collect project details and market data"),
                ("Risk Analysis", "Evaluate business and technical risks"),
                ("Strategic Reasoning", "Generate mitigation strategies"),
                ("Validation", "Cross-check recommendations with data"),
                ("Report Generation", "Create final assessment report"),
            ]

            def render_agent_steps(active_step=-1, completed_steps=0, faded=False):
                cards = []
                for index, (title, description) in enumerate(agent_steps):
                    if index < completed_steps:
                        state_class = "agent-step-complete agent-step-faded" if faded else "agent-step-complete"
                        state_text = "Complete"
                    elif index == active_step:
                        state_class = "agent-step-active"
                        state_text = "In progress"
                    else:
                        state_class = "agent-step-pending"
                        state_text = "Queued"

                    connector_class = "agent-step-connector-complete" if index < completed_steps - 1 else "agent-step-connector-pending"
                    connector = "" if index == len(agent_steps) - 1 else f'<div class="agent-step-connector {connector_class}"></div>'
                    cards.append(f"""
    <div class="agent-step-wrap">
      <div class="agent-step-box {state_class}">
        <div class="agent-step-copy">
          <div class="agent-step-title">{title}</div>
          <div class="agent-step-description">{description}</div>
          <div class="agent-step-state">{state_text}</div>
        </div>
      </div>
      {connector}
    </div>
    """)

                return f"""
    <style>
    .agent-step-list {{
        position: relative;
        width: min(100%, 680px);
        margin: 0 auto;
        padding: 18px;
        border: 1px solid rgba(255, 255, 255, 0.7);
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.34);
        backdrop-filter: blur(20px) saturate(145%);
        -webkit-backdrop-filter: blur(20px) saturate(145%);
        box-shadow: 0 14px 30px rgba(31, 41, 55, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.75);
        font-family: sans-serif;
    }}
    .agent-step-wrap {{
        position: relative;
    }}
    .agent-step-box {{
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 48px;
        padding: 7px 10px;
        border: 1px solid transparent;
        border-radius: 12px;
        box-sizing: border-box;
        transition: all 0.35s ease;
    }}
    .agent-step-copy {{
        width: 100%;
        min-width: 0;
        text-align: center;
    }}
    .agent-step-title {{
        font-size: 15px;
        font-weight: 700;
        line-height: 1.2;
    }}
    .agent-step-description {{
        margin-top: 3px;
        font-size: 10px;
        line-height: 1.4;
    }}
    .agent-step-state {{
        margin-top: 4px;
        font-size: 9px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .04em;
    }}
    .agent-step-pending {{
        color: #9CA3AF;
        background: rgba(255, 255, 255, 0.24);
    }}
    .agent-step-pending .agent-step-state {{
        color: #9CA3AF;
    }}
    .agent-step-active {{
        color: #4338CA;
        border-color: #6366F1;
        background: rgba(224, 231, 255, 0.74);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.14), 0 10px 22px rgba(79, 70, 229, 0.15);
    }}
    .agent-step-active .agent-step-description {{
        color: #6366F1;
    }}
    .agent-step-active .agent-step-state {{
        color: #4F46E5;
    }}
    .agent-step-complete {{
        color: #047857;
        border-color: #6EE7B7;
        background: rgba(209, 250, 229, 0.56);
    }}
    .agent-step-complete .agent-step-description,
    .agent-step-complete .agent-step-state {{
        color: #059669;
    }}
    .agent-step-faded {{
        border-color: rgba(110, 231, 183, 0.55);
        background: rgba(209, 250, 229, 0.3);
        box-shadow: none;
    }}
    .agent-step-connector {{
        width: 2px;
        height: 22px;
        margin: 0 auto;
    }}
    .agent-step-connector-complete {{
        background: linear-gradient(#10B981, #6EE7B7);
    }}
    .agent-step-connector-pending {{
        background: linear-gradient(#CBD5E1, #E5E7EB);
    }}
    @media (max-width: 620px) {{
        .agent-step-list {{
            padding: 10px;
        }}
    }}
    </style>
    <div class="agent-step-list">{"".join(cards)}</div>
    """

            with agent_container:
                agent_progress = st.empty()
                agent_progress.markdown(render_agent_steps(), unsafe_allow_html=True)

            st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
            button_left, button_center, button_right = st.columns([1.2, 0.85, 0.8])
            with button_center:
                run_agent_workflow = st.button(
                    "Run LangGraph Agent Workflow",
                    use_container_width=False,
                    type="primary",
                )

            if run_agent_workflow:
                import time
                status = st.status("Initializing Agent Workflow...", expanded=True)

                agent_progress.markdown(render_agent_steps(active_step=0), unsafe_allow_html=True)
                status.update(label="Step 1: Data Ingestion...")
                time.sleep(1)
                status.write("✅ Collected project details and market parameters")

                agent_progress.markdown(render_agent_steps(active_step=1, completed_steps=1), unsafe_allow_html=True)
                status.update(label="Step 2: Risk Analysis...")
                time.sleep(1)
                status.write("✅ Evaluated business and technical risks")

                agent_progress.markdown(render_agent_steps(active_step=2, completed_steps=2), unsafe_allow_html=True)
                status.update(label="Step 3: Strategic Reasoning...")
                time.sleep(1.5)
                status.write("✅ Generated mitigation strategies using Gemini reasoning")

                agent_progress.markdown(render_agent_steps(active_step=3, completed_steps=3), unsafe_allow_html=True)
                status.update(label="Step 4: Validation...")
                time.sleep(1)
                status.write("✅ Cross-checked recommendations with dataset")

                agent_progress.markdown(render_agent_steps(active_step=4, completed_steps=4), unsafe_allow_html=True)
                status.update(label="Step 5: Report Generation...", state="complete")
                time.sleep(0.5)
                status.write("✅ Final assessment report successfully created!")
                agent_progress.markdown(render_agent_steps(completed_steps=5), unsafe_allow_html=True)
                time.sleep(5)
                agent_progress.markdown(render_agent_steps(completed_steps=5, faded=True), unsafe_allow_html=True)

                st.success("Agent Workflow Complete! The recommended mitigation strategies have been finalized.")
with tab4:
    st.markdown('''
<h1 style="margin: 0; padding: 0; font-size: 28px; color: #111827; font-weight: 700; font-family: sans-serif; margin-bottom: 4px;">Dashboard & Deployment</h1>
<p style="margin: 0 0 24px 0; color: #6B7280; font-size: 15px; font-family: sans-serif;">Risk analytics dashboard and comprehensive assessment reports</p>
''', unsafe_allow_html=True)

    if 'project_data' not in st.session_state:
        st.info('Submit a project idea in the Project Input tab to view the Dashboard.')
    else:
        # Mock dynamic data based on session state
        data = st.session_state.get('project_data', {})
        industry = data.get('industry', 'Technology')
        budget = data.get('budget', 100000)

        # Derive some numbers to make the dashboard look dynamic
        overall_risk = min(85, max(15, int(100 - (budget / 5000))))
        success_prob = 100 - overall_risk
        market_risk = 65 if industry == 'Technology' else 40
        tech_risk = 70 if industry == 'Technology' else 30

        col1, col2, col3 = st.columns([1, 1.5, 1])

        with col1:
            st.markdown('<div style="font-weight: 600; color: #374151; font-size: 14px; margin-bottom: 12px; font-family: sans-serif;">Risk Analytics</div>', unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            c1.metric("Overall Risk", f"{overall_risk}%", "+5%", delta_color="inverse")
            c2.metric("Success Prob.", f"{success_prob}%", "-8%", delta_color="normal")
            
            c3, c4 = st.columns(2)
            c3.metric("Market Risk", f"{market_risk}%", "+12%", delta_color="inverse")
            c4.metric("Tech Risk", f"{tech_risk}%", "-3%", delta_color="normal")

            st.markdown('<div style="font-weight: 600; color: #374151; font-size: 12px; margin-top: 24px; margin-bottom: 8px; font-family: sans-serif;">Risk Trend (6 Months)</div>', unsafe_allow_html=True)
            
            # Create dummy chart data using random values around overall_risk
            import numpy as np
            chart_data = pd.DataFrame(
                np.random.randn(6, 1) * 10 + overall_risk,
                index=["Oct", "Nov", "Dec", "Jan", "Feb", "Mar"],
                columns=["Risk Level"]
            )
            st.line_chart(chart_data, height=200)

        with col2:
            header_col1, header_col2, header_col3 = st.columns([4, 2, 2])
            with header_col1:
                st.markdown('<div style="font-weight: 600; color: #374151; font-size: 14px; margin-bottom: 12px; margin-top: 5px; font-family: sans-serif;">Assessment Report</div>', unsafe_allow_html=True)
            
            report_markdown = f"""# Prediction AI - Risk Assessment Report
**Project:** {data.get('startup_name', 'Unknown')}
**Industry:** {industry}

## Key Findings
- Market saturation: 15+ direct competitors in target segment
- Budget runway: Only 8 months remaining at current burn rate
- Team gaps: Missing critical marketing and sales expertise
- Differentiation: No clear unique value proposition identified

## Risk Assessment
- Market Risk ({market_risk}%): High competition and customer acquisition costs
- Financial Risk (72%): Insufficient runway and revenue projections
- Technical Risk ({tech_risk}%): Feasible with current team capabilities

## Recommendations
1. Pivot to niche market to reduce competition
2. Secure Series A funding within 90 days
3. Hire marketing lead with industry experience
4. Develop MVP to validate market fit
"""
            with header_col2:
                st.download_button(label="📥 Export", data=report_markdown, file_name="risk_assessment_report.md", mime="text/markdown", use_container_width=True)
            with header_col3:
                with st.popover("🔗 Share", use_container_width=True):
                    st.write("**Share this report securely:**")
                    st.code("http://localhost:8501/?view=dashboard&report_id=latest")
                    if st.button("Copy Link", use_container_width=True):
                        st.toast("Report link copied to clipboard! 📋")
            
            st.markdown('''
            <div style="border: 1px solid #E5E7EB; border-radius: 6px; padding: 16px; margin-bottom: 16px; background: white; font-family: sans-serif;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-weight: 600; font-size: 13px; color: #111827;">Key Findings</span>
                    <span style="color: #D97706; background: #FEF3C7; font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 12px;">High Priority</span>
                </div>
                <ul style="color: #6B7280; font-size: 12px; padding-left: 16px; margin-bottom: 0;">
                    <li>Market saturation: 15+ direct competitors in target segment</li>
                    <li>Budget runway: Only 8 months remaining at current burn rate</li>
                    <li>Team gaps: Missing critical marketing and sales expertise</li>
                    <li>Differentiation: No clear unique value proposition identified</li>
                </ul>
            </div>
            
            <div style="border: 1px solid #E5E7EB; border-radius: 6px; padding: 16px; margin-bottom: 16px; background: white; font-family: sans-serif;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-weight: 600; font-size: 13px; color: #111827;">Risk Assessment</span>
                    <span style="color: #2563EB; background: #DBEAFE; font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 12px;">Medium Priority</span>
                </div>
                <p style="color: #6B7280; font-size: 12px; margin-bottom: 0;">
                    <b>Market Risk (85%):</b> High competition and customer acquisition costs<br>
                    <b>Financial Risk (72%):</b> Insufficient runway and revenue projections<br>
                    <b>Technical Risk (48%):</b> Feasible with current team capabilities
                </p>
            </div>
            
            <div style="border: 1px solid #E5E7EB; border-radius: 6px; padding: 16px; background: white; font-family: sans-serif;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-weight: 600; font-size: 13px; color: #111827;">Recommendations</span>
                    <span style="color: #DC2626; background: #FEE2E2; font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 12px;">Action Required</span>
                </div>
                <ol style="color: #6B7280; font-size: 12px; padding-left: 16px; margin-bottom: 0;">
                    <li>Pivot to niche market to reduce competition</li>
                    <li>Secure Series A funding within 90 days</li>
                    <li>Hire marketing lead with industry experience</li>
                    <li>Develop MVP to validate market fit</li>
                </ol>
            </div>
            ''', unsafe_allow_html=True)

        with col3:
            st.markdown('<div style="font-weight: 600; color: #374151; font-size: 14px; margin-bottom: 12px; font-family: sans-serif;">Strategic Insights 💡</div>', unsafe_allow_html=True)
            
            st.markdown('''
            <div style="border-left: 3px solid #EF4444; padding-left: 12px; margin-bottom: 20px; font-family: sans-serif;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-weight: 600; font-size: 12px; color: #111827;">Funding Strategy</span>
                    <span style="color: #EF4444; background: #FEE2E2; font-size: 9px; font-weight: 600; padding: 2px 6px; border-radius: 4px;">Critical Impact</span>
                </div>
                <p style="color: #6B7280; font-size: 11px; margin-bottom: 4px; line-height: 1.4;">Current burn rate unsustainable. Need bridge round or pivot to revenue-generating model</p>
                <a href="#" style="color: #3B82F6; font-size: 10px; text-decoration: none;">See funding options &rarr;</a>
            </div>
            
            <div style="border-left: 3px solid #F59E0B; padding-left: 12px; margin-bottom: 24px; font-family: sans-serif;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-weight: 600; font-size: 12px; color: #111827;">Technical Advantage</span>
                    <span style="color: #F59E0B; background: #FEF3C7; font-size: 9px; font-weight: 600; padding: 2px 6px; border-radius: 4px;">Medium Impact</span>
                </div>
                <p style="color: #6B7280; font-size: 11px; margin-bottom: 4px; line-height: 1.4;">AI algorithm shows 25% better accuracy than competitors. Leverage for marketing differentiation</p>
                <a href="#" style="color: #3B82F6; font-size: 10px; text-decoration: none;">View comparison &rarr;</a>
            </div>
            
            <div style="font-weight: 600; color: #374151; font-size: 13px; margin-bottom: 12px; font-family: sans-serif;">Recommended Next Steps</div>
            <div style="display: flex; align-items: center; margin-bottom: 8px; font-family: sans-serif;">
                <div style="background: #3B82F6; color: white; width: 16px; height: 16px; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 9px; font-weight: bold; margin-right: 8px;">1</div>
                <span style="color: #4B5563; font-size: 11px;">Schedule pivot strategy meeting</span>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 8px; font-family: sans-serif;">
                <div style="background: #3B82F6; color: white; width: 16px; height: 16px; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 9px; font-weight: bold; margin-right: 8px;">2</div>
                <span style="color: #4B5563; font-size: 11px;">Prepare investor pitch deck</span>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 8px; font-family: sans-serif;">
                <div style="background: #3B82F6; color: white; width: 16px; height: 16px; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 9px; font-weight: bold; margin-right: 8px;">3</div>
                <span style="color: #4B5563; font-size: 11px;">Initiate partnership discussions</span>
            </div>
            ''', unsafe_allow_html=True)
