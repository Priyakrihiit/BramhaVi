# Database Architecture Directory - BrahmaVidya Galaxy

This directory houses the PostgreSQL relational and document-extended database architecture specifications for **BrahmaVidya Galaxy**.

## Contents

- **[Database Design Specifications (`database_design.md`)](./database_design.md)**: A comprehensive architecture manual covering the entity-relationship mapping, naming conventions, primary/foreign key strategies, UUID schemes, audit rules, soft delete designs, schema versioning, and high-performance indexing strategies.

---

## Architectural Philosophy
The storage engine uses PostgreSQL to guarantee ACID transactional safety for user profiles, access control rights (RBAC), certificates, and financial ledgers. It leverages JSONB document types for flexible CMS layout grids and LMS multi-tier syllabus paths, combining the advantages of relational consistency and document flexibility.
