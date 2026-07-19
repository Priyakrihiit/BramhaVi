# Test Suites & Quality Assurance Ledgers - BrahmaVidya Galaxy

This folder contains the automated verification framework for BrahmaVidya Galaxy, covering unit tests, integration pipelines, and end-to-end user validations.

## Directory Structure & Purpose

- **`unit/`**: Verifies isolated business functions (e.g., validating certificate SHA-256 signatures, checking JWT expirations, or parsing layout blocks).
- **`integration/`**: Tests multi-subsystem workflows (e.g., completing lesson tasks cascading to trigger progress percent changes and wallet payouts).
- **`performance/`**: Simulated request-load tests verifying latency standards under concurrent session spikes.
- **`mocks/`**: High-fidelity local database schemas and mock service objects simulating LLM APIs.

---

## Execution Standards
All test definitions must use isolated mock states to prevent writing corrupt transactional rows to live production databases.
