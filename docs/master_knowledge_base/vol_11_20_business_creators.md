# BrahmaVidya Galaxy - Master Knowledge Base V2.0
## Volumes 11 to 20: Digital Publishing, Creator Economy, & SaaS tenancies

---

## Volume 11 - Publishing Galaxy

### 11.1 Business Objective
Empower authors to draft, peer-review, format, and distribute books natively on the bookstore.

### 11.2 Database Design (Publishing Assets)
```sql
-- Editorial Review Pipeline
CREATE TABLE editorial_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id UUID REFERENCES publishing_books(id) ON DELETE CASCADE,
    reviewer_id UUID REFERENCES users(id) ON DELETE RESTRICT,
    review_notes TEXT,
    decision VARCHAR(50) NOT NULL CHECK (decision IN ('APPROVED', 'CHANGES_REQUESTED', 'REJECTED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 11.3 Validation Rules
* **ISBN Format**: Must match standard ISBN-13 format structures (`^(?:97[89])?\d{9}[\dxX]$`).
* **Royalties**: Individual split percentages cannot exceed 100% total allocation.

---

## Volume 12 - Book Store Galaxy

### 12.1 Purchasing & Inventory Mechanics
* **Digital Files**: Served securely via pre-signed storage links.
* **Printed Inventories**: Integrated with logistics partners APIs to fetch real-time shipping costs.

---

## Volume 13 - Creator Economy

### 13.1 Mentor Scheduling Modules
```sql
-- Mentor booking availabilities
CREATE TABLE mentor_availability (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mentor_id UUID REFERENCES users(id) ON DELETE CASCADE,
    day_of_week INTEGER CHECK (day_of_week BETWEEN 1 AND 7),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    hourly_rate DECIMAL(10, 2) NOT NULL
);

-- Active scheduled sessions
CREATE TABLE mentor_bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    availability_id UUID REFERENCES mentor_availability(id) ON DELETE RESTRICT,
    client_id UUID REFERENCES users(id) ON DELETE RESTRICT,
    booking_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED')),
    payment_status VARCHAR(50) DEFAULT 'UNPAID' CHECK (payment_status IN ('UNPAID', 'PAID', 'REFUNDED'))
);
```

---

## Volume 14 - Professional Services

### 14.1 Enterprise Client AMCs
Tracks Annual Maintenance Contracts (AMC) and custom application consulting tasks. Payments are processed in milestones using dynamic escrows in user wallets.

---

## Volume 15 - Marketplace

### 15.1 SaaS Plugin Licensing APIs
* **Activate License Key**:
  * `POST /api/v1/marketplace/licenses/activate/`
  * Request payload: `{"license_key": "<string>", "domain": "client-site.com"}`
  * Response: `{"success": true, "status": "ACTIVE", "expires_at": "2027-07-08T12:00:00Z"}`

---

## Volume 16 - Portfolio Builder

### 16.1 Custom Domain Mapping Engine
* **DNS Resolution Checks**: The web app periodically runs DNS lookup queries (e.g. searching for target CNAME pointing records) prior to finalizing domain activations.

---

## Volume 17 - Resume Builder

### 17.1 Resume Analytics Database
```sql
CREATE TABLE resume_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id UUID NOT NULL,
    views_count INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0,
    ats_score INTEGER CHECK (ats_score BETWEEN 0 AND 100),
    last_viewed_at TIMESTAMP WITH TIME ZONE
);
```

---

## Volume 18 - Career Galaxy

### 18.1 AI Interview Preparation Agent
* **Workflows**: Students record responses to system questions. The AI parses the transcript, evaluates confidence, identifies weak responses, and scores the performance.

---

## Volume 19 - Organization Galaxy

### 19.1 School & University tenancies
Allows educational campuses to register student rosters in batches and manage classrooms under specific custom subdomains (`tenant-name.brahmavidya.galaxy`).

---

## Volume 20 - Business SaaS

### 20.1 SME CRM & Accounting Modules
Includes sales opportunity logs, custom client pipelines, corporate invoice builders, and basic payroll models with tax compliance checks.
