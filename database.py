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

def save_assessment(project_id, swot_data, risk_score, risk_status, success_probability, recommendations):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        strengths = ", ".join(swot_data.get("Strengths", [])) or "N/A"
        weaknesses = ", ".join(swot_data.get("Weaknesses", [])) or "N/A"
        opportunities = ", ".join(swot_data.get("Opportunities", [])) or "N/A"
        threats = ", ".join(swot_data.get("Threats", [])) or "N/A"

        cur.execute('''
            INSERT INTO swot_analysis (project_id, strengths, weaknesses, opportunities, threats)
            VALUES (?, ?, ?, ?, ?);
        ''', (project_id, strengths, weaknesses, opportunities, threats))

        cur.execute('''
            INSERT INTO risk_assessments (project_id, risk_category, risk_score, risk_description, priority_level)
            VALUES (?, ?, ?, ?, ?);
        ''', (
            project_id,
            "Overall",
            risk_score,
            f"Status: {risk_status}",
            "High" if risk_score > 60 else "Medium",
        ))

        cur.execute('''
            INSERT INTO success_predictions (project_id, success_probability, overall_risk_score)
            VALUES (?, ?, ?);
        ''', (project_id, success_probability, risk_score))

        for recommendation in recommendations:
            steps = recommendation.get("steps") or [recommendation.get("action", "")]
            recommendation_text = " ".join(
                f"{index}. {step}" for index, step in enumerate(steps, start=1)
            )
            cur.execute('''
                INSERT INTO recommendations (project_id, recommendation_text, risk_mitigation, priority)
                VALUES (?, ?, ?, ?);
            ''', (
                project_id,
                recommendation_text,
                recommendation.get("risk_reduction", ""),
                recommendation.get("priority", "Medium"),
            ))

        cur.execute('''
            INSERT INTO assessment_reports (project_id, report_path)
            VALUES (?, ?);
        ''', (project_id, f"streamlit_assessment_{project_id}"))

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()