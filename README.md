How the Pipeline Works:

- Continuous Scanning: Automatically scans container base images using Aqua Security Trivy on every push.
- AI Security Triage: Uses a custom Python runner to query Google Gemini APIs, turning raw JSON vulnerability dumps into prioritised, actionable remediation steps.
- Automated Remediation: Integrates Dependabot to automatically submit patch PRs (e.g., upgrading base images like node:14-alpine to secure releases).

Tech Stack: GitHub Actions | Aqua Trivy | Google Gemini API | Python | Dependabot | Docker
