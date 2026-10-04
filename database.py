import sqlite3
import os
from dotenv import load_dotenv


load_dotenv()



def get_db_connection():
    conn = sqlite3.connect('ml_project.db')
    conn.row_factory = sqlite3.Row
    return conn

def insert_project(data):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO projects (startup_name, industry, business_model, target_market, budget, project_description)
        VALUES (?, ?, ?, ?, ?, ?)
        
    ''', (
        data['startup_name'],
        data['industry'],
        data['business_model'],
        data['target_market'],
        data['budget'],
        data['project_description']
    ))
    project_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    return project_id

def get_project(project_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM projects WHERE id = ?;', (project_id,))
    project = cur.fetchone()
    cur.close()
    conn.close()
    return project

def insert_swot_analysis(project_id, swot_data):
    conn = get_db_connection()
    cur = conn.cursor()

   
    strengths_list = swot_data.get('Strengths', [])
    weaknesses_list = swot_data.get('Weaknesses', [])
    opportunities_list = swot_data.get('Opportunities', [])
    threats_list = swot_data.get('Threats', [])

    strengths = ", ".join(strengths_list) if strengths_list else "N/A"
    weaknesses = ", ".join(weaknesses_list) if weaknesses_list else "N/A"
    opportunities = ", ".join(opportunities_list) if opportunities_list else "N/A"
    threats = ", ".join(threats_list) if threats_list else "N/A"

    cur.execute('''
        INSERT INTO swot_analysis (project_id, strengths, weaknesses, opportunities, threats)
        VALUES (?, ?, ?, ?, ?)
        RETURNING swot_id;
    ''', (project_id, strengths, weaknesses, opportunities, threats))

    swot_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return swot_id
def insert_risk_assessment(project_id, risk_category, risk_score, risk_description, priority_level):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO risk_assessments (project_id, risk_category, risk_score, risk_description, priority_level)
        VALUES (?, ?, ?, ?, ?)
        RETURNING risk_id;
    ''', (project_id, risk_category, risk_score, risk_description, priority_level))
    risk_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return risk_id
    
def insert_success_prediction(project_id, success_probability, overall_risk_score):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO success_predictions (project_id, success_probability, overall_risk_score)
        VALUES (?, ?, ?)
        RETURNING prediction_id;
    ''', (project_id, success_probability, overall_risk_score))
    
    prediction_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return prediction_id

def save_assessment(
    project_id,
    swot_data,
    risk_score,
    risk_status,
    success_probability,
    recommendations,
    mitigations,
    improvements
):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        strengths = ", ".join(swot_data.get("Strengths", [])) or "N/A"
        weaknesses = ", ".join(swot_data.get("Weaknesses", [])) or "N/A"
        opportunities = ", ".join(swot_data.get("Opportunities", [])) or "N/A"
        threats = ", ".join(swot_data.get("Threats", [])) or "N/A"

        # ---------------------------------------------------------
        # 1. Save SWOT Analysis
        # ---------------------------------------------------------
        cur.execute('''
            INSERT INTO swot_analysis (
                project_id,
                strengths,
                weaknesses,
                opportunities,
                threats
            )
            VALUES (?, ?, ?, ?, ?);
        ''', (
            project_id,
            strengths,
            weaknesses,
            opportunities,
            threats
        ))

        # ---------------------------------------------------------
        # 2. Save Risk Assessment
        # ---------------------------------------------------------
        cur.execute('''
            INSERT INTO risk_assessments (
                project_id,
                risk_category,
                risk_score,
                risk_description,
                priority_level
            )
            VALUES (?, ?, ?, ?, ?);
        ''', (
            project_id,
            "Overall",
            risk_score,
            f"Status: {risk_status}",
            "High" if risk_score > 60 else "Medium",
        ))

        # ---------------------------------------------------------
        # 3. Save Success Prediction
        # ---------------------------------------------------------
        cur.execute('''
            INSERT INTO success_predictions (
                project_id,
                success_probability,
                overall_risk_score
            )
            VALUES (?, ?, ?);
        ''', (
            project_id,
            success_probability,
            risk_score
        ))

        # ---------------------------------------------------------
        # 4. Save AI Recommendations
        # ---------------------------------------------------------
        for recommendation in recommendations:
            steps = recommendation.get("steps") or [
                recommendation.get("action", "")
            ]

            recommendation_text = " ".join(
                f"{index}. {step}"
                for index, step in enumerate(steps, start=1)
            )

            cur.execute('''
                INSERT INTO recommendations (
                    project_id,
                    category,
                    recommendation_text,
                    problem_risk,
                    why_it_matters,
                    recommended_action,
                    expected_risk_reduction,
                    priority
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            ''', (
                project_id,
                recommendation.get("category", ""),
                recommendation_text,
                recommendation.get("problem", ""),
                recommendation.get("explanation", ""),
                recommendation.get("action", ""),
                recommendation.get("risk_reduction", ""),
                recommendation.get("priority", "Medium"),
            ))

        # ---------------------------------------------------------
        # 5. Save Mitigation Strategies
        # ---------------------------------------------------------
        for mitigation in mitigations:
            cur.execute('''
                INSERT INTO mitigation_strategies (
                    project_id,
                    risk_name,
                    category,
                    description,
                    impact,
                    priority,
                    mitigation_strategy,
                    preventive_action,
                    contingency_action
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            ''', (
                project_id,
                mitigation.get("risk", ""),
                mitigation.get("category", ""),
                mitigation.get("description", ""),
                mitigation.get("impact", ""),
                mitigation.get("priority", "Medium"),
                mitigation.get("mitigation_strategy", ""),
                mitigation.get("preventive_action", ""),
                mitigation.get("contingency_action", ""),
            ))

        # ---------------------------------------------------------
        # 6. Save Improvement Plans
        # ---------------------------------------------------------
        for improvement in improvements:
            cur.execute('''
                INSERT INTO improvement_plans (
                    project_id,
                    category,
                    improvement,
                    reason,
                    expected_benefit,
                    priority
                )
                VALUES (?, ?, ?, ?, ?, ?);
            ''', (
                project_id,
                improvement.get("category", ""),
                improvement.get("title", ""),
                improvement.get("problem", ""),
                improvement.get("risk_reduction", ""),
                improvement.get("priority", "Medium"),
            ))

        # ---------------------------------------------------------
        # 7. Save Assessment Report
        # ---------------------------------------------------------
        cur.execute('''
            INSERT INTO assessment_reports (
                project_id,
                report_path
            )
            VALUES (?, ?);
        ''', (
            project_id,
            f"streamlit_assessment_{project_id}"
        ))

        # ---------------------------------------------------------
        # Commit everything
        # ---------------------------------------------------------
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()

def get_latest_project():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute('''
            SELECT
                id,
                startup_name,
                industry,
                business_model,
                target_market,
                budget,
                project_description,
                created_at
            FROM projects
            ORDER BY id DESC
            LIMIT 1
        ''')

        project = cur.fetchone()

        if project:
            return dict(project)

        return None

    finally:
        cur.close()
        conn.close()