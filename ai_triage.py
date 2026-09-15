import os
import json
import sys
import google.generativeai as genai

# 1. Verify environment variable exists
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY environment variable is missing or empty.")
    sys.exit(1)

try:
    genai.configure(api_key=api_key)
    # Use updated model string syntax
    model = genai.GenerativeModel('gemini-1.5-flash')

    # 2. Check if Trivy results file exists
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

    response = model.generate_content(prompt)
    print("\n=== AI SECURITY SUMMARY ===")
    print(response.text)

except Exception as e:
    print(f"CRITICAL ERROR in AI Script: {str(e)}")
    sys.exit(1)