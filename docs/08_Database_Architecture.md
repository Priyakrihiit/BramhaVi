# Database Architecture - BrahmaVidya Galaxy

## 1. Relational Database Schema Design
BrahmaVidya Galaxy uses a normalized PostgreSQL schema designed to guarantee transactional consistency for core metrics while allowing JSONB scalability for modular content blocks.

```
       +-------------------+               +-------------------+
       |       roles       | <-----------+ |  role_permissions |
       +-------------------+               +-------------------+
                 ^                                   |
                 |                                   v
                 |                         +-------------------+
                 |                         |    permissions    |
                 |                         +-------------------+
                 |
       +-------------------+               +-------------------+
       |       users       | <-----------+ | navigation_menus  |
       +-------------------+               +-------------------+
                 ^
                 |
         +-------+-------+
         |               |
         v               v
   +-----------+   +-----------+           +-------------------+
   | wallets   |   |  ledger_  | <=======> |   certificates    |
   |           |   |  entries  |           +-------------------+
   +-----------+   +-----------+                     ^
         ^               ^                           |
         |               |                           |
         v               v                           |
   +---------------------------+                     |
   |     course_structures     | +-------------------+
   | (6-Tier Recursive Node)   |
   +---------------------------+
                 ^
                 |
                 v
   +---------------------------+
   |   learning_progress       |
   +---------------------------+
```

---

## 2. Table Schemas & Constraints

### 2.1 Identity & Access Control (RBAC)
- **`roles`**: Models discrete user tiers.
  - `id` (UUID, Primary Key)
  - `name` (VARCHAR, Unique, e.g., "PLATFORM_ADMIN")
  - `description` (TEXT)
- **`permissions`**: Granular feature checkpoints.
  - `id` (UUID, Primary Key)
  - `code` (VARCHAR, Unique, e.g., "COURSE_CREATE")
  - `description` (TEXT)
- **`role_permissions`**: Many-to-Many junction table linking roles and permissions.
  - `role_id` (UUID, Foreign Key referencing `roles.id`)
  - `permission_id` (UUID, Foreign Key referencing `permissions.id`)
- **`users`**: Secure account details.
  - `id` (UUID, Primary Key)
  - `email` (VARCHAR, Unique, Indexed)
  - `password_hash` (VARCHAR)
  - `role_id` (UUID, Foreign Key referencing `roles.id`)
  - `status` (VARCHAR, e.g., "ACTIVE", "PENDING", "SUSPENDED")

### 2.2 Navigation and Content Engine (CMS)
- **`navigation_menus`**: Recursive site-wide links.
  - `id` (UUID, Primary Key)
  - `parent_id` (UUID, Nullable, Foreign Key referencing `navigation_menus.id` on delete cascade)
  - `title` (VARCHAR)
  - `url` (VARCHAR)
  - `icon` (VARCHAR, Lucide key)
  - `display_order` (INTEGER)
  - `required_permission` (VARCHAR, Nullable, reference to `permissions.code`)
- **`pages`**: Custom layout builder files.
  - `id` (UUID, Primary Key)
  - `title` (VARCHAR)
  - `slug` (VARCHAR, Unique, Indexed)
  - `layout_data` (JSONB) -- Models dynamic blocks (Hero, Stats, etc.)
  - `seo_title` (VARCHAR)
  - `seo_description` (TEXT)
  - `keywords` (TEXT) -- Comma-separated SEO tags
  - `is_published` (BOOLEAN)

### 2.3 Curricula & Academic Progress (LMS)
- **`course_structures`**: Recursive 6-Tier Academic Map.
  - `id` (UUID, Primary Key)
  - `parent_id` (UUID, Nullable, Foreign Key referencing `course_structures.id` on delete cascade)
  - `type` (VARCHAR, Enum: "PROGRAM", "DEGREE", "COURSE", "MODULE", "LESSON", "TASK")
  - `title` (VARCHAR)
  - `description` (TEXT)
  - `metadata` (JSONB) -- Custom configs: timing, video details, task types
- **`learning_progress`**: Tracks learner checkpoints.
  - `user_id` (UUID, Foreign Key referencing `users.id`)
  - `structure_id` (UUID, Foreign Key referencing `course_structures.id`)
  - `progress_percentage` (DECIMAL)
  - `status` (VARCHAR, Enum: "NOT_STARTED", "IN_PROGRESS", "COMPLETED")
  - `last_accessed` (TIMESTAMP)

### 2.4 Certification & Finance Ledgers
- **`certificates`**: Public verification records.
  - `id` (UUID, Primary Key)
  - `recipient_id` (UUID, Foreign Key referencing `users.id`)
  - `course_id` (UUID, Foreign Key referencing `course_structures.id`)
  - `certificate_hash` (VARCHAR, Unique, SHA-256 Signature)
  - `metadata` (JSONB) -- Template values
  - `issued_at` (TIMESTAMP)
- **`wallets`**: Balances for financial transactions.
  - `id` (UUID, Primary Key)
  - `user_id` (UUID, Foreign Key referencing `users.id`)
  - `balance` (DECIMAL, default 0.00)
- **`ledger_entries`**: Immutable ledger trail.
  - `id` (UUID, Primary Key)
  - `from_wallet_id` (UUID, Nullable)
  - `to_wallet_id` (UUID, Nullable)
  - `amount` (DECIMAL)
  - `transaction_type` (VARCHAR, e.g., "COURSE_PURCHASE", "WITHDRAWAL")
  - `created_at` (TIMESTAMP)

---

## 3. Database Indexing & JSONB Optimization

### 3.1 Standard Indexing Strategy
To guarantee low latency during spikes, indices are created for heavy filter pathways:
- `CREATE INDEX idx_users_email ON users(email);`
- `CREATE INDEX idx_pages_slug ON pages(slug);`
- `CREATE INDEX idx_course_recursive ON course_structures(parent_id, type);`

### 3.2 JSONB Querying & Indexing (GIN)
Since layout metadata and block lists are stored in JSONB columns, we configure Generalized Inverted Indexes (GIN) to enable fast searching inside nesting properties:
- `CREATE INDEX idx_pages_layout_gin ON pages USING gin (layout_data);`
- This index speeds up queries searching for pages utilizing specific components (e.g., finding pages with `CurriculumExplorerBlock`).
