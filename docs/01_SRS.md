# Software Requirement Specification (SRS) - BrahmaVidya Galaxy

## 1. Introduction
This document outlines the software requirements for **BrahmaVidya Galaxy**, a next-generation Enterprise Educational Platform operating as a hybrid Dynamic Content Management System (CMS) and Learning Management System (LMS). 

### 1.1 Purpose
The purpose of this SRS is to establish a clear, unambiguous specification of the behavioral and operational constraints of the BrahmaVidya Galaxy application. It serves as the single source of truth for engineering, product, and QA stakeholders.

### 1.2 System Scope
BrahmaVidya Galaxy employs a **Content-Agnostic Engine Architecture**. No curriculum structures, landing page designs, site navigation, user privileges, or layouts are hardcoded in the application. The system consists of:
1. **Dynamic Rendering Core**: A client-side browser application that consumes structural and stylistic configurations from the backend and renders them in real time.
2. **Dynamic Admin Control Center**: A centralized dashboard that provides visual interfaces to manipulate layout blocks, navigation menus, access lists, dynamic certifications, and AI endpoints.
3. **Enterprise Backend Services**: A decoupled backend architecture managing API routes, AI gateways, database operations, and secure operations.

---

## 2. Overall Description

### 2.1 Product Perspective
BrahmaVidya Galaxy acts as a sovereign educational canvas. Unlike standard systems (Moodle, Blackboard), this platform separates the visual framework entirely from the content structure. Dynamic JSON layout payloads dictate page contents, and dynamic course-node structures dictate the LMS paths.

```
+--------------------------------------------------------------------------+
|                        BRAHMAVIDYA GALAXY APPLICATION                     |
|                                                                          |
|   +---------------------------------+  API  +------------------------+   |
|   |   React SPA Render Engine       | <===> |  Unified API Gateway   |   |
|   |  - Dynamic Navigation UI        |       |  - Auth / Session Svc  |   |
|   |  - JSON Layout Page Renderer    |       |  - CMS Layout Manager  |   |
|   |  - Multi-Portal Student LMS     |       |  - LMS Path Broker     |   |
|   |  - Interactive AI Assistant     |       |  - Vidya AI Connector  |   |
|   +---------------------------------+       +------------------------+   |
|                                                          ||              |
|                                                          v               |
|                                               +------------------------+ |
|                                               |  Enterprise DB Engine  | |
|                                               +------------------------+ |
+--------------------------------------------------------------------------+
```

### 2.2 Product Functions
- **Autonomous Page Generation**: Dynamically serves routes like `/p/:slug` utilizing schema-validated JSON layout blocks.
- **Hierarchical Course Builder**: Dynamic recursion supporting Programs, Degrees, Courses, Modules, Lessons, and Tasks.
- **Cryptographic Certificate Verification**: Visual certification generator with dynamic QR codes verifying authenticity via high-integrity ledger checks.
- **Vidya AI Gateway**: Unified backend gateway linking LLM providers (Gemini, etc.) for curricular generation, evaluation, and student assistant chat.
- **Granular RBAC Engine**: Customizable role mapping to API endpoints and UI pathways.

### 2.3 User Classes and Characteristics
- **Platform Admins (Superusers)**: Full structural control over the platform, system integrations, database migration logs, and global configuration.
- **School Operators**: Institutional managers mapping regional courses, pricing structures, teacher validations, and enrollment ledgers.
- **Instructors / Teachers**: Educators creating modular contents, tracking student progress metrics, and monitoring wallet analytics.
- **Students / Learners**: End-users studying materials, completing quizzes, tracking progress, and verifying achievements.

### 2.4 Design and Implementation Constraints
- **State Management**: Zero global client state for layouts; layout configurations must be retrieved on route navigation and cached efficiently.
- **Database Modularity**: Storage systems must maintain strict 3rd Normal Form for identity structures while supporting JSONB schemas for dynamic blocks.
- **Security Compliance**: Enforced HttpOnly, secure cookie-based JWT sessions with token-rotation, and absolute sanitization of markdown inputs to prevent XSS.

---

## 3. Specific Requirements

### 3.1 External Interface Requirements
- **User Interfaces**: Highly responsive layouts, customized dark theme matching a "Cosmic Slate" palette, complete with subtle, purposeful transitions.
- **Software Interfaces**: Native integration with Google GenAI SDK for server-side LLM processing and localized DB storage scripts.

### 3.2 System Features
- **Dynamic Routing**: Automatic hook creation on route registry changes.
- **Interactive AI Helper**: Live chat drawer offering instant curriculum parsing and quiz creations.
- **Verification Engine**: Verification endpoint `/verify/:hash` querying database ledgers for unique certificate cryptographic hashes.

### 3.3 Assumptions and Dependencies
- **Availability of LLM Credentials**: The server must lazy-initialize the Gemini client to avoid crashes if API keys are temporarily unconfigured.
- **Local Persistence Reliability**: Local database storage files (such as JSON models) must be synchronized safely to prevent multi-write corruption.
