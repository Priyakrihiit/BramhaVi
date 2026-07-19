# Operational Scripts & Administrative Seeders - BrahmaVidya Galaxy

This directory houses command-line scripts, database initialization seeders, certificate signature generators, and dev operations helpers.

## Directory Structure & Purpose

- **`database/`**: SQL migration trackers and data seeders populating global parameters (roles, permissions, core metadata templates).
- **`cryptography/`**: Offline command-line tools validating certificate signatures or generating master platform salts.
- **`maintenance/`**: Automated scripts monitoring log directories or flushing expired cache values (e.g., Redis entries).

---

## Execution Constraints
Scripts in this folder are restricted to administrative tasks and must not run inside the standard client request-response cycles.
