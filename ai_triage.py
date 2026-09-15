import os, json
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

with open('trivy-results.json') as f:
    scan_data = json.load(f)

prompt = f"Analyze these container CVEs and give 2 critical remediation steps:\n{json.dumps(scan_data)[:2000]}"
response = model.generate_content(prompt)

print("\n=== AI SECURITY SUMMARY ===")
print(response.text)