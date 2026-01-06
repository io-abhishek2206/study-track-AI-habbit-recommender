import os
from google import genai
print("GEMINI_API_KEY =", os.getenv("GEMINI_API_KEY"))
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3-flash-preview"

def generate_student_feedback(study, work, play, sleep, marks, cluster):
    # Map the cluster ID to a readable word for the AI
    cluster_map = {0: "Average", 1: "Poor", 2: "Excellent"}
    cluster_desc = cluster_map.get(cluster, "Unknown")

    prompt = f"""
    You are a friendly academic mentor.
    Student Details:
    - Study Hours: {study}, Work Hours: {work}, Play: {play}, Sleep: {sleep}
    - Predicted Marks: {marks}, Performance Cluster: {cluster_desc}

    Write a short (4-6 lines) personalized, encouraging feedback. 
    Include one improvement and one practical suggestion.
    """

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"Error generating feedback: {e}"
