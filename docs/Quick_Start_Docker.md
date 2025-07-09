# Docker Deployment Guide

## Overview

This document provides secure deployment instructions for the Trend Micro Cybersecurity Report QA API using Docker. The approach emphasizes a security-first mindset, ensuring that all containers are built, configured, and operated according to best practices for confidentiality, integrity, and availability.

---

## Prerequisites

- Docker Engine 20.10+ and Docker Compose 1.29+
- Python 3.10+ (for local validation scripts)
- A valid Google Gemini API key (see Environment Variables)
- Sufficient system resources (2+ CPU, 4GB+ RAM recommended)

---

## Secure Docker Build & Run Instructions

1. Clone the repository and navigate to the project root.
2. Review and, if necessary, edit `containerization/Dockerfile` and `containerization/docker-compose.yml` to match your environment and security requirements.
3. Build and start the containers:

   ```bash
   cd containerization
   docker-compose up -d --build
   ```

4. Verify the API is running securely:
   - API: http://localhost:8000/docs
   - Gradio Frontend: http://localhost:7860 (if enabled)

---

## Environment Variables & Secrets Management

- All sensitive configuration (API keys, model parameters) must be set via environment variables.
- Use `config/config.env` or a secure `.env` file. Never hardcode secrets in code or Dockerfiles.
- Required variables:
  - `GOOGLE_API_KEY` (Gemini API key)
  - `GEMINI_MODEL`, `GEMINI_TEMPERATURE`, `GEMINI_MAX_TOKENS` (model config)
  - `KNOWLEDGE_FILE` (knowledge base path, default: summary.txt)
- Example:

   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   GEMINI_MODEL=gemini-2.0-flash-lite
   GEMINI_TEMPERATURE=0.1
   GEMINI_MAX_TOKENS=200
   KNOWLEDGE_FILE=summary.txt
   ```

- Use Docker secrets or a secrets manager for production deployments.

---

## Security Best Practices

- **Container Hardening**:
  - Use official Python slim base images and minimize installed packages.
  - Remove build tools and caches after installation.
- **Least Privilege**:
  - Run containers as a non-root user.
  - Limit container capabilities and avoid privileged mode.
- **Read-Only Mounts**:
  - Mount knowledge base files and config as read-only.
  - Do not expose sensitive files or directories to the container.
- **Network Security**:
  - Expose only required ports (8000 for API, 7860 for Gradio if needed).
  - Use firewalls or Docker network policies to restrict access.
- **Environment Hygiene**:
  - Do not log secrets or sensitive data.
  - Mask API keys in logs and health checks.
- **Image Updates**:
  - Regularly update base images and dependencies to address vulnerabilities.
- **Monitoring & Auditing**:
  - Enable container logging and monitor for suspicious activity.
  - Use tools like Docker Bench for Security to validate your setup.

---

## Troubleshooting & Security Checks

- **Container Fails to Start**:
  - Check logs with `docker-compose logs` or `docker logs <container>`.
  - Ensure all required environment variables are set and valid.
- **API Key Not Detected**:
  - Confirm `GOOGLE_API_KEY` is set in the environment and not expired.
- **File Not Found Errors**:
  - Ensure `summary.txt` and other required files are present and mounted correctly.
- **Health Check Fails**:
  - Review `/health` endpoint for detailed component status.
- **Security Validation**:
  - Run `testing_tools/test_security.py` and `validate_project.py` for automated checks.

---

## References

- [Docker Official Documentation](https://docs.docker.com/)
- [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- [Google Gemini API Documentation](https://ai.google.dev/)
- [Trend Micro Cybersecurity Report QA Project Status](./PROJECT_STATUS.md)
