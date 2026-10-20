# Sprint 2 — CI/CD Security Testing

Configured a GitLab CI/CD pipeline to run security checks against OWASP Juice Shop. The pipeline includes:

- **SAST** with Semgrep.
- **Software Composition Analysis (SCA)** and SBOM generation with Trivy.
- **DAST** with OWASP ZAP.
- **Security gates** that fail the pipeline when findings meet configured severity thresholds.

Scanner reports, gate logs, and triage results are included in the repository.

## Detailed Report

See [report.md](report.md) for implementation details, configuration, and validation results.
