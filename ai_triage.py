import os
import json
import sys
import time
from google import genai

# 1. Retrieve API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY environment variable is missing or empty.")
    sys.exit(1)

try:
    # 2. Instantiate GenAI Client
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

    # 4. Dynamically list all available models for your API key
    print("Fetching list of available models for your account...")
    available_models = []
    
    for m in client.models.list():
        # Clean model name string (strip 'models/' prefix if present)
        model_id = m.name.replace("models/", "") if hasattr(m, "name") else str(m)
        # Filter for text/flash/generate content models
        if "flash" in model_id or "pro" in model_id or "gemini" in model_id:
            available_models.append(model_id)

    # Prioritize flash models first for fast execution
    available_models.sort(key=lambda x: ("flash" not in x, x))
    
    print(f"Discovered {len(available_models)} model candidates: {available_models}")

    response = None
    successful_model = None

    # 5. Loop through all discovered models
    for model_name in available_models:
        print(f"\n---> Trying model: {model_name}")
        for attempt in range(2):
            try:
                res = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if res and res.text:
                    response = res
                    successful_model = model_name
                    break
            except Exception as err:
                err_msg = str(err)
                if "503" in err_msg or "UNAVAILABLE" in err_msg:
                    print(f"  [503 Busy] Retrying {model_name} in 3 seconds...")
                    time.sleep(3)
                else:
                    print(f"  [Skipped] {model_name} failed: {err_msg[:100]}...")
                    break
        
        if response:
            break

    # 6. Print Output
    if response:
        print(f"\n==========================================")
        print(f" SUCCESSFUL MODEL: {successful_model}")
        print(f"==========================================")
        print("\n=== AI SECURITY SUMMARY ===")
        print(response.text)
    else:
        print("\nCRITICAL ERROR: None of the available models were able to complete the request.")
        sys.exit(1)

except Exception as e:
    print(f"CRITICAL ERROR in AI Script: {str(e)}")
    sys.exit(1)