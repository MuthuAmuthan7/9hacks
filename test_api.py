"""
Example script demonstrating how to use the Medical AI Consultation API.
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_api():
    """Test the API with a complete workflow."""
    
    print("=" * 60)
    print("Medical AI Consultation System - API Test")
    print("=" * 60)
    
    # Check health
    print("\n1. Checking API health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.json()['status']}")
    except requests.exceptions.ConnectionError:
        print("   ERROR: Cannot connect to API. Make sure it's running on http://localhost:8000")
        return
    
    # Start a new case
    print("\n2. Starting a new medical case...")
    try:
        response = requests.post(f"{BASE_URL}/start_case")
        response.raise_for_status()
        case_data = response.json()
        case_id = case_data["case_id"]
        print(f"   Case ID: {case_id}")
        print(f"   Initial Message: {case_data['initial_message']}")
    except Exception as e:
        print(f"   ERROR: {str(e)}")
        return
    
    # Simulate doctor-patient conversation
    print("\n3. Simulating doctor-patient conversation...")
    
    # Sample doctor questions
    questions = [
        "How long have you had these symptoms?",
        "Do you have a cough?",
        "Have you experienced any shortness of breath?",
        "Do you have any fever?",
        "Have you traveled recently or been around sick people?",
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n   Question {i}: Doctor asks: '{question}'")
        
        try:
            response = requests.post(
                f"{BASE_URL}/doctor_input",
                json={
                    "case_id": case_id,
                    "doctor_text": question
                }
            )
            response.raise_for_status()
            
            result = response.json()
            patient_response = result["patient_response"]
            print(f"   Patient responds: '{patient_response}'")
            
            # Small delay between requests
            time.sleep(0.5)
        
        except Exception as e:
            print(f"   ERROR: {str(e)}")
            break
    
    # Evaluate the doctor
    print("\n4. Evaluating doctor's performance...")
    try:
        response = requests.post(
            f"{BASE_URL}/evaluate",
            json={"case_id": case_id}
        )
        response.raise_for_status()
        
        evaluation = response.json()
        
        print("\n" + "=" * 60)
        print("EVALUATION RESULTS")
        print("=" * 60)
        print(f"Disease: {evaluation['disease_revealed']}")
        
        scores = evaluation['evaluation']
        print(f"\nScores:")
        print(f"  Diagnostic Questions: {scores['diagnostic_score']:.1f}/10")
        print(f"  Symptom Understanding: {scores['symptom_understanding_score']:.1f}/10")
        print(f"  Treatment Accuracy: {scores['treatment_score']:.1f}/10")
        print(f"  Communication Skills: {scores['communication_score']:.1f}/10")
        print(f"  Overall Score: {scores['overall_score']:.1f}/100")
        
        print(f"\nFeedback:")
        print(f"  {scores['feedback']}")
        
        if scores['missing_questions']:
            print(f"\nMissing Questions (Should Have Asked):")
            for q in scores['missing_questions']:
                print(f"  - {q}")
        
        print("\n" + "=" * 60)
        print("Test completed successfully!")
        print("=" * 60)
    
    except Exception as e:
        print(f"   ERROR: {str(e)}")
        return


if __name__ == "__main__":
    print("\nMake sure the API is running:")
    print("  - With Docker: docker-compose up --build")
    print("  - Locally: uvicorn main:app --reload")
    print("\nStarting tests in 2 seconds...")
    time.sleep(2)
    
    test_api()
