import os
import json
import sys
import time
from google import genai

# 1. Retrieve environment variable
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY environment variable is missing or empty.")
    sys.exit(1)

try:
    # 2. Instantiate Client
    client = genai.Client(api_key=api_key)

    # 3. Verify scan results exist
    if not os.path.exists('trivy-results.json'):
        print("ERROR: trivy-results.json not found!")
        sys.exit(1)

    with open('trivy-results.json', 'r') as f:
        scan_data = json.load(f)

    prompt = f"""
    You are a DevSecOps AI Assistant. Analyze this vulnerability report and summarize:
    1. Top 2 critical vulnerabilities we MUST fix immediately.
    2. Recommended fix actions for the developer.

    Report Data: {json.dumps(scan_data)[:2000]}
    """

    # 4. List of candidate models to try
    models_to_try = ['gemini-2.5-flash', 'gemini-1.5-flash']
    response = None

    for model_name in models_to_try:
        # Retry loop for capacity/503 issues
        for attempt in range(3):
            try:
                print(f"Attempting triage with model: {model_name} (Attempt {attempt + 1})...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response:
                    break
            except Exception as err:
                if "503" in str(err) or "UNAVAILABLE" in str(err):
                    print(f"Server busy (503). Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    # If model not found or another error, break to try next model
                    print(f"Notice for {model_name}: {str(err)}")
                    break
        if response:
            break

    if response:
        print("\n=== AI SECURITY SUMMARY ===")
        print(response.text)
    else:
        print("CRITICAL ERROR: All AI model endpoints were unavailable.")
        sys.exit(1)

except Exception as e:
    print(f"CRITICAL ERROR in AI Script: {str(e)}")
    sys.exit(1)