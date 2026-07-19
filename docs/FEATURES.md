# BrahmaVidya Galaxy: Complete Planned Features Matrix
## Comprehensive System Feature Catalog

This document details every planned, in-progress, and completed feature across the **BrahmaVidya Galaxy** ecosystem, grouped by their respective operational modules.

---

## 1. Identity, Access, & Authentication Module

### Feature: JWT Authentication
- **Module**: Authentication
- **Description**: Secure, stateless user sessions governed by 15-minute Access Tokens and 7-day Refresh Tokens.
- **Status**: **Completed**

### Feature: Dynamic Role Gating (RBAC)
- **Module**: Authentication
- **Description**: System access gates verifying permission codenames recursively inherited via dynamic roles database mappings.
- **Status**: **Completed**

### Feature: Multi-Device Verification
- **Module**: Authentication
- **Description**: Authorized devices registration mapping pushing notifications tokens for system security alerts.
- **Status**: **Completed**

### Feature: Secure Sign-Up & Password Hashing
- **Module**: Authentication
- **Description**: High-entropy password storage using bcrypt and standard email verification workflows.
- **Status**: **Completed**

---

## 2. Learning Management System (LMS) Module

### Feature: Hierarchical 6-Tier Curriculum
- **Module**: LMS
- **Description**: Recursive course syllabus structure containing Programs, Subjects, Courses, Chapters, Topics, Subtopics, and Lessons.
- **Status**: **Completed**

### Feature: Soft-Delete with Restoration
- **Module**: LMS
- **Description**: Safe resource deletion with Teacher/Admin restore capabilities via customized API endpoints.
- **Status**: **Completed**

### Feature: Assignment Submissions & Feedback
- **Module**: LMS
- **Description**: Multi-format file uploads and essay prompts with custom feedback text and score records.
- **Status**: **Completed**

### Feature: Central Question Bank
- **Module**: LMS
- **Description**: Shared database of questions supporting various formats (multiple-choice, matching, short answer) across courses.
- **Status**: **Completed**

### Feature: Practice Session Mock Tests
- **Module**: LMS
- **Description**: Dynamic, untimed mock testing for students with immediate answer verification.
- **Status**: **Completed**

### Feature: Capstone Projects
- **Module**: LMS
- **Description**: Comprehensive real-world projects with specific criteria grids and file submission workflows.
- **Status**: **Completed**

### Feature: Milestone Exams
- **Module**: LMS
- **Description**: Timed, grading-threshold assessments gating graduation.
- **Status**: **Planned**

### Feature: Interactive Learning Progress
- **Module**: LMS
- **Description**: Unified completion percentages updated automatically upon completing lessons.
- **Status**: **Planned**

### Feature: Cryptographic Certificates
- **Module**: LMS
- **Description**: SHA-256 secure, publicly verifiable course graduation certificates.
- **Status**: **Planned** (Database schema structure completed)

### Feature: Achievement Gamification (Badges)
- **Module**: LMS
- **Description**: Achievement milestones automatically awarded upon streak thresholds.
- **Status**: **Planned** (Database schema structure completed)

---

## 3. Content Management System (CMS) Module

### Feature: Dynamic Page Builder
- **Module**: CMS
- **Description**: Assembly of rich landing pages via GIN-indexed custom layout blocks JSON payloads.
- **Status**: **Completed**

### Feature: Interactive Platform Tutorials
- **Module**: CMS
- **Description**: Markdown guides for platform onboarding and system tool execution.
- **Status**: **Completed**

### Feature: Adaptive Navigation Menus
- **Module**: CMS
- **Description**: RBAC-gated header and sidebar navigation nodes updated dynamically.
- **Status**: **Completed**

### Feature: Multi-State Editorial Workflow
- **Module**: CMS
- **Description**: Standard publication status lifecycle (Draft, Under Review, Approved, Published).
- **Status**: **Planned**

---

## 4. Blogs Module

### Feature: Blog Publications Engine
- **Module**: Blogs
- **Description**: Rich educational and scientific updates posting, complete with draft toggling and slug indexing.
- **Status**: **Completed**

### Feature: Nested Comment Loops
- **Module**: Blogs
- **Description**: Threaded discussion comments underneath articles with user-identity handles.
- **Status**: **Planned** (Database schemas completed)

---

## 5. Community & Collaboration Module

### Feature: Structural Forums Boards
- **Module**: Community
- **Description**: Modular discussion boards mapping topics to specific course syllabus blocks.
- **Status**: **Planned**

### Feature: Thread Reaction Indicators
- **Module**: Community
- **Description**: Quick reactions on comments and discussions.
- **Status**: **Planned** (Database schemas completed)

### Feature: Content Moderation Reports
- **Module**: Community
- **Description**: Reporting ticket pipelines feeding straight into Moderator and Support queues.
- **Status**: **Planned** (Database schemas completed)

---

## 6. Portfolio Builder Module

### Feature: AI-Powered Website Construction
- **Module**: Portfolio Builder
- **Description**: A no-code AI-powered website builder that enables users to create professional websites without writing code.
  
  **Supported website types include:**
  - Personal Portfolio
  - Resume Website
  - Business Website
  - Manufacturer Website
  - Company Website
  - Startup Website
  - Shop
  - Mart
  - Restaurant
  - School
  - College
  - Coaching Institute
  - Hospital
  - Clinic
  - Artist
  - Photographer
  - Designer
  - Blogger
  - NGO
  - Event Website
  - Product Catalogue
  - Any custom website

  **Features:**
  - Drag & Drop Builder
  - AI Website Generator
  - Templates
  - Navigation Builder
  - Header Builder
  - Footer Builder
  - Sections Builder
  - Gallery
  - Contact Forms
  - Blog
  - SEO
  - Analytics
  - Custom Domain
  - Responsive Design

  **Subscription Plan:**
  - ₹99/month

- **Status**: **Planned**

---

## 7. Vidya AI (Intelligence) Module

### Feature: Context-Aware Chatbot
- **Module**: Vidya AI
- **Description**: Chat assistant utilizing Gemini Pro via server-side proxying for personalized student conversations.
- **Status**: **Planned** (Thread and messages schemas completed)

### Feature: AI Subject Tutor
- **Module**: Vidya AI
- **Description**: System prompts establishing customized AI personas (ancient philosophy scholars, physics mentors, engineering experts).
- **Status**: **Planned**

### Feature: AI Career Resume Synthesizer
- **Module**: Vidya AI
- **Description**: AI generation of student resume documents dynamically tracking learning progress and capstone completions.
- **Status**: **Planned**

---

## 8. Wallet Module

### Feature: Points Ledger Audit Lists
- **Module**: Wallet
- **Description**: Double-entry bookkeeping ledger logs preventing concurrent point manipulation or double-spending.
- **Status**: **Planned** (Models and database tables completed)

### Feature: Peer Point Transfers
- **Module**: Wallet
- **Description**: Instant peer-to-peer rewards points transfers between student wallets.
- **Status**: **Planned**

---

## 9. Payments Module

### Feature: Stripe & Razorpay Checkout Gateways
- **Module**: Payments
- **Description**: Secure, short-lived payment gateways generating transactional invoices upon checkout.
- **Status**: **Planned** (Database invoice structures completed)

### Feature: Tiered Subscriptions Management
- **Module**: Payments
- **Description**: Dynamic user subscriptions tier checking, automatically validating premium LMS content access.
- **Status**: **Planned**

---

## 10. Analytics & Telemetry Module

### Feature: High-Velocity Event Tracker
- **Module**: Analytics
- **Description**: Append-only clickstream logging compiling video playback and hover metrics.
- **Status**: **Planned** (Database telemetry models completed)

### Feature: Educational Dashboard Reporting
- **Module**: Analytics
- **Description**: Graphical charts illustrating course completion progress and test statistics.
- **Status**: **Planned**

---

## 11. Control Center Module

### Feature: Live Platform Settings
- **Module**: Control Center
- **Description**: JSON-backed administrative flags managing system configurations at runtime.
- **Status**: **Planned** (Database tables completed)

### Feature: Dynamic Theme Builder
- **Module**: Control Center
- **Description**: Dynamic customization of frontend theme palettes.
- **Status**: **Planned** (Database tables completed)

---

## 12. Frontend (React Client) Module

### Feature: Responsive Landing Space
- **Module**: Frontend
- **Description**: Fluid, responsive grids optimized for desktop dashboards and mobile workspaces.
- **Status**: **Planned**

### Feature: Focus-Mode Overlays
- **Module**: Frontend
- **Description**: Smooth UI transitions allowing distraction-free reading environments.
- **Status**: **Planned**

---

## 13. Admin Panel Module

### Feature: Integrated RBAC Clearance Console
- **Module**: Admin Panel
- **Description**: Interactive user permissions editing dashboards enabling roles assignment.
- **Status**: **Planned**

### Feature: Dynamic Page Construction Portal
- **Module**: Admin Panel
- **Description**: Administrative layout designer generating custom layout block configurations.
- **Status**: **Planned**
