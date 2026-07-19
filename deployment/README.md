# Deployment & Dev-Ops Configurations - BrahmaVidya Galaxy

This folder contains container blueprints, reverse proxy rules, and CI/CD workflow files to support blue-green zero-downtime deployment strategies.

## Directory Structure & Purpose

- **`docker/`**: Multi-stage Dockerfiles optimizing image size and separating build pipelines from runtime execution states.
- **`nginx/`**: Security-hardened reverse proxy configuration files setting security headers, SSL parameters, and CORS Whitelisting rules.
- **`kubernetes/`**: Declarative state files managing replication factors, service node bindings, and autoscaling thresholds.
- **`ci-cd/`**: Automated test automation workflows running linter tools and compiling binaries prior to release commits.

---

## Security Compliance
Production secrets, private keys, and live database credentials must **never** be hardcoded in these templates. They are injected at container boot using secure runtime environments.
