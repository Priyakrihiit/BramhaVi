# BrahmaVidya Galaxy - Enterprise Educational Platform
## Comprehensive Specification & Architecture Blueprint

This document serves as the Enterprise Software Requirement Specification (SRS), Business Requirement Document (BRD), and System Architecture Design for the **BrahmaVidya Galaxy** platform.

---

## 1. Business Requirement Document (BRD)

### 1.1 Executive Summary
**BrahmaVidya Galaxy** is a next-generation, enterprise-grade Software-as-a-Service (SaaS) Educational Platform. It is designed to act as a hybrid Content Management System (CMS) and Learning Management System (LMS) for global scale operations. Unlike typical consumer LMS systems, BrahmaVidya Galaxy is built with a **Content-Agnostic Engine Architecture** where no educational structures, page contents, navigation, roles, or layouts are hardcoded in the codebase. The entire platform operates as a dynamic canvas controlled completely by an administrative **Control Center**.

### 1.2 Business Objectives
1. **Zero-Code Operational Agility**: Empower administrators and editors to configure all public-facing structures, navigation, courses, and localized pricing without requiring developer cycles or redeployments.
2. **Multi-Tenant / Enterprise RBAC**: Secure multi-role workflows enabling distinct portals for Platform Admins, School Operators, Teachers, Content Inspectors, and Students.
3. **Sovereign Content Ownership**: Ensure hierarchical course building, modular AI service abstractions (Vidya AI), and custom certificate generation with digital QR verifiability.
4. **Global Monetization Engine**: Facilitate dynamic transaction splitting, automated invoicing, coupons, platform-commission routing, and student wallet infrastructure.

### 1.3 Key Stakeholders
- **Platform Administrators (System Admins)**: Superusers who control global configuration, page templates, dynamic menu hierarchies, and security parameters.
- **Instructors / Teachers**: Subject matter experts who register, undergo verification, build custom courses, track student analytics, and withdraw revenue shares.
- **Students / Learners**: Global users who register, enroll in dynamic courses, complete interactive tasks, earn certificates, and participate in community threads.
- **Auditors & Compliance Officers**: Security and finance operators reviewing security audit logs and transaction details.

---

## 2. Enterprise Software Requirement Specification (SRS)

### 2.1 Functional Requirements (FR)

#### FR1: Core Configuration & CMS Engine (Dynamic Page Builder)
- **FR1.1**: The system must provide a Page Builder supporting JSON-configured dynamic layout structures.
- **FR1.2**: Administrators can create, publish, schedule, or duplicate pages with dynamic routes (e.g., `/p/about`, `/p/terms`).
- **FR1.3**: The UI must dynamically render layout components (e.g., hero widgets, statistics grids, features blocks) based on layout JSON responses.

#### FR2: Dynamic Menu Management
- **FR2.1**: Support unlimited recursive navigation nodes (menus, submenus, mega menus) defined completely by DB models.
- **FR2.2**: Menus must support condition-based visibility (e.g., only visible to logged-in users or specific roles).

#### FR3: Dynamic Role-Based Access Control (RBAC)
- **FR3.1**: Dynamically declared permissions mapping HTTP methods and system resource domains.
- **FR3.2**: Custom role definition interfaces with custom granular permission checklists.

#### FR4: Dynamic Course & Content Engine
- **FR4.1**: Hierarchical curriculum definition: Programs → Degrees/Paths → Courses → Modules → Lessons → Tasks.
- **FR4.2**: Rich modular media types (Video streaming, Rich Text, Interactive markdown, Downloads).

#### FR5: Vidya AI Abstraction Gateway
- **FR5.1**: Provide a unified AI gateway API wrapping Gemini, OpenAI, Claude, and local models.
- **FR5.2**: Core capabilities: Dynamic course structure planning, student quiz generation, writing refinement, and automatic categorization of community discussions.

#### FR6: Teacher Verification & Revenue Sharing
- **FR6.1**: KYC verification pipeline for registered instructors with approval workflow.
- **FR6.2**: Automated ledger splitting: Student payment splits between platform commissions (fixed/%) and Teacher wallets.

#### FR7: Certificate Engine with QR Cryptographic Verification
- **FR7.1**: Fully customizable visual templates (dynamic margins, backgrounds, border designs).
- **FR7.2**: QR code generation pointing to a public, high-integrity verification route (`/verify/:id`) checking the database ledger for unique certificate hashes.

### 2.2 Non-Functional Requirements (NFR)
- **Performance**: Page load under 1.5 seconds under 10k concurrent users using edge caching.
- **Security**: Double JWT auth tokens (Access + HttpOnly Refresh Cookie), secure CSRF, rate-limited public APIs, and complete data masking of secret inputs.
- **Scale**: Designed for horizontal backend scaling, Postgres read replicas, and caching layer separation.
- **Accessibility**: Conform to Web Content Accessibility Guidelines (WCAG 2.1) AA standards, including strict contrast ratio boundaries and keyboard navigability.

---

## 3. Complete System Architecture

```
                                 [ BrahmaVidya Galaxy Gateway ]
                                                |
                 +------------------------------+------------------------------+
                 |                                                             |
         [ Public Portal ]                                             [ Control Center ]
                 |                                                             |
   - Dynamic Navigation Menus                                    - Dynamic Menu Management
   - Rendered Layout Components                                  - Page Layout & Block Builders
   - Enrollment & Learning View                                  - Dynamic RBAC & Custom Roles
   - Certificate Verification Screen                             - Course & Curriculum Designer
   - Vidya AI Assistant Chat                                     - Ledger & Wallet Oversight
                 |                                                             |
                 +------------------------------+------------------------------+
                                                |
                                    [ Unified Express API ]
                                                |
                     +--------------------------+--------------------------+
                     |                          |                          |
               [ Auth/RBAC ]              [ Content CMS ]            [ Vidya AI API ]
                     |                          |                          |
                     v                          v                          v
             [ PostgreSQL / DB ]        [ JSON Store ]             [ Google GenAI SDK ]
```

### 3.1 Architectural Pillars
1. **Strict Content Decoupling**: The React application acts as an empty, metadata-driven UI renderer. The Express server provides system parameters, menu definitions, layout nodes, and authentication filters.
2. **Unified API Contract**: Standardized payloads returning `{ success: boolean, data: T, meta?: pagination }` for clean consumption.
3. **Modular Gateway for Vidya AI**: High-level provider wrappers. Switching from Gemini to Claude requires zero frontend changes—only an admin dropdown configuration update.

---

## 4. Database Architecture (PostgreSQL Schema Design)

Below is the normalized database schema mapping the dynamic operational needs of BrahmaVidya Galaxy:

```sql
-- 1. Identity & RBAC Core
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(100) UNIQUE NOT NULL, -- e.g., "COURSE_CREATE", "MENU_WRITE"
    description TEXT
);

CREATE TABLE role_permissions (
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role_id UUID REFERENCES roles(id),
    status VARCHAR(50) DEFAULT 'ACTIVE', -- 'ACTIVE', 'PENDING', 'SUSPENDED'
    avatar_url TEXT,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Menu & Navigation Engine
CREATE TABLE navigation_menus (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID REFERENCES navigation_menus(id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL,
    url VARCHAR(255) NOT NULL,
    icon VARCHAR(100), -- Lucide-react key string
    display_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    required_permission VARCHAR(100), -- Nullable, checks access
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Dynamic Page Builder
CREATE TABLE pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    layout_data JSONB NOT NULL, -- Core UI layout structure (JSON of widgets/blocks)
    seo_title VARCHAR(255),
    seo_description TEXT,
    is_published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Dynamic LMS / Course Builder
CREATE TABLE course_structures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID REFERENCES course_structures(id) ON DELETE CASCADE, -- Hierarchical recursion
    type VARCHAR(50) NOT NULL, -- 'PROGRAM', 'SUBJECT', 'COURSE', 'MODULE', 'LESSON'
    title VARCHAR(255) NOT NULL,
    description TEXT,
    metadata JSONB, -- Dynamic attributes (hours, difficulty, requirements)
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_learning_progress (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    structure_id UUID REFERENCES course_structures(id) ON DELETE CASCADE,
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    status VARCHAR(50) DEFAULT 'NOT_STARTED', -- 'IN_PROGRESS', 'COMPLETED'
    last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, structure_id)
);

-- 5. Digital Certificate Engine
CREATE TABLE certificates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_id UUID REFERENCES users(id) ON DELETE CASCADE,
    course_id UUID REFERENCES course_structures(id) ON DELETE CASCADE,
    certificate_hash VARCHAR(64) UNIQUE NOT NULL,
    qr_code_url TEXT,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB -- Dynamic branding, template parameters
);
```

---

## 5. Development Roadmap & Implementation Plan

### Milestone 1: Foundations & Backend Infrastructure
- Establish full-stack Node.js Express server (`server.ts`) integrating Vite middleware on port `3000`.
- Create a complete in-memory Database service that models the full PostgreSQL schema (enabling real-time updates and persistence in our preview environment).
- Set up secure modular API routing (`/api/auth`, `/api/menu`, `/api/pages`, `/api/rbac`, `/api/courses`, `/api/ai`).

### Milestone 2: The Portal UI Renderer
- Build the dynamic, slate-gold themed React rendering engine.
- Implement dynamic recursive navigation menus driven by the API.
- Create the page rendering manager that parses JSON-based structures into layouts automatically.
- Setup authentication frameworks with persistent simulated sessions.

### Milestone 3: The Unified Control Center (The Heart)
- Build the full Management Panel UI featuring:
  - **Menu Management**: Visual tree builder to add, remove, and reorder menus.
  - **Page Layout Builder**: JSON block composer to control public site sections.
  - **RBAC Matrix Editor**: Custom roles and real-time permission configuration.
  - **Course Builder**: Hierarchical course and curriculum designer.
  - **Certificates Dashboard**: Verification and template parameters.

### Milestone 4: Vidya AI Gateway & Integration
- Integrate `@google/genai` on the server using `gemini-3.5-flash`.
- Formulate specialized AI assist features:
  - Automated Curriculum Outlining (inputting a title generates full Course Builder JSON).
  - Assessment Generator (dynamic quiz builder for lessons).
  - Custom system response mapping.

### Milestone 5: Verification & Launch
- Perform full linting and verification compilation (`npm run build`).
- Embed comprehensive developer documentation within the app's secondary view for active verification.

---

*End of Specification Document.*
