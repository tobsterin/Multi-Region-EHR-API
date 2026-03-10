# Multi Region EHR API (Prototype)

A cross border health record prototype designed to respect **GDPR** and **NHS DSPT** requirements. It follows simplified **FHIR R4 structures** and uses **SNOMED CT codes** where relevant.  
The aim is to demonstrate how a federated model can allow clinicians in the UK, Germany, and France to locate and view records without centralising clinical data.

---

## 1. Overview

Sharing healthcare data across countries is complicated. This project takes a practical approach: **keep data in the patient’s home region**, while allowing clinicians to locate and view records when needed.

* **Federated Master Patient Index (MPI):** Links the same person across regions without exposing raw identifiers.
* **Serverless Architecture:** Built fully on AWS (Lambda, API Gateway, DynamoDB).
* **Data Residency:** Regional DynamoDB tables store medical data; the Global MPI stores *only* pseudonymized pointers.
* **Transient Access:** Data is merged **in memory only** during a session and never persisted cross‑border.

---

## 2. Core Architectural Strategy

* **Regional Vaults:** Each country (UK/DE/FR) has its own DynamoDB tables for Patient, Encounter, and Observation resources.  
* **Master Patient Index (MPI):** DynamoDB Global Table storing only pseudonymised pointers (hashes + UUIDs).  
* **Secure Linking:** Lambda functions hash national IDs using a salt stored in **AWS Secrets Manager**.  
* **Network Security:** All service calls flow through **VPC Endpoints (PrivateLink)**. Each region runs inside its own VPC with private subnets.
* **Access Control:** DynamoDB access is strictly limited via IAM Policies and VPC Endpoint policies (no public internet access).

---

## 3. Main Technologies

### Authentication & Access Control
* **Amazon Cognito:** User Pools with RBAC (Groups: Clinician, Auditor, Admin). MFA enforced for clinicians.

### Edge Layer
* **Amazon CloudFront + AWS WAF:** Geo-blocking and protection for the frontend/API.

### API Layer
* **Amazon API Gateway:** Regional REST APIs with Cognito authorizers.

### Compute
* **Search Service:** Lambda (Python) for ID hashing and MPI lookup.
* **CRUD Services:** Lambdas for Patient, Encounter, and Observation operations.
* **Analysis Service:** Triggered by DynamoDB Streams (stubbed for Comprehend Medical).

### Storage
* **DynamoDB Regional Tables:** Stores clinical data (encrypted with regional CMKs).
* **DynamoDB Global Table:** Stores the MPI (pseudonymized).

### Security
* **AWS KMS:** Regional Customer Managed Keys (CMKs) for encryption at rest.
* **AWS Secrets Manager:** Secure storage for salts and API tokens.

### Logging & Audit
* **Amazon S3:** Centralized log storage with Object Lock for immutability.
* **AWS CloudTrail:** Full API auditing with 7–10 year retention policies.

---

## 4. Data Flow (Clinic Visit)

1.  **Patient Identification:** Patient arrives and informs the clinician of records in another country.
2.  **Search:** Clinician enters the foreign National Health ID.
3.  **Hash & Lookup:** Search Lambda retrieves the salt, hashes the ID, and queries the MPI.
4.  **Federated Retrieval:** If a match is found, the system fetches relevant clinical data from that specific country’s regional table.
5.  **Aggregation:** Records are merged **in memory** and displayed to the clinician. **Nothing is written centrally.**
6.  **Analysis:** New notes trigger DynamoDB Streams → Analysis Lambda → Coded insights.
7.  **Visualization:** Frontend aggregates insights into a clinical timeline (browser-side only).
8.  **Creation:** New records are stored only in the region where they are created, maintaining strict data sovereignty.
9.  **Audit:** Logs are stored in both the requesting region (access) and the source region (data retrieval).

---

## 5. Project Structure

.
├── terraform/         # Infrastructure as Code (multi‑region setup)
├── data/              # Sample FHIR JSON records
├── dynamodb/          # Table schema definitions (JSON)
├── lambda/            # Python handler code
├── api-gateway/       # OpenAPI specifications
├── secrets/           # Placeholder salt (replaced by Secrets Manager in prod)
├── diagrams/          # Architecture diagrams
└── README.md          # Project overview & compliance notes

---

## 6. Development & Operations

* **Infrastructure as Code:** Terraform manages all resources.
* **CI/CD Pipeline:** GitHub Actions for automated testing and deployment.
* **Monitoring:** CloudWatch Metrics/Logs and CloudTrail.
* **Integration Tests:** Validates logic using mock FHIR data.
* **Policy Enforcement:** Deny-by-default IAM policies; every read/write action logs "Purpose of Use".

---

## 7. Production Readiness

**Multi Account Strategy (AWS Organizations):**
* **Security OU:** GuardDuty, Security Hub, Incident Response environments.
* **Log/Archive OU:** Immutable storage for CloudTrail & Config archives.
* **Workloads OU:** Isolated Production accounts for UK, FR, and DE (Strict Data Residency).
* **Research OU:** De identified data lake for population health analytics.

**Application Hardening:**
* **Resilience:** SQS Dead Letter Queues (DLQs) and automated retry policies.
* **Performance:** Provisioned Concurrency for search Lambdas to reduce cold starts.
* **Protection:** Rate limiting, request validation, and strict payload size limits.

---

## 8. Compliance Features

* **Data Isolation:** Separate databases and keys per region.
* **Cross Border Access:** Federated API only; no raw data is stored globally.
* **Immutable Auditing:** CloudTrail + S3 Object Lock (WORM).
* **Encryption:** Customer Managed Keys (CMK) per region; TLS 1.2+ in transit.
* **Right to Erasure:** Automated workflows to delete patient data upon request.
* **SNOMED + FHIR:** Structured resources, coded entries  
* **Admin access:** Strict IAM roles, MFA enforced  
* **UK vs EU Nuance:**
    * **UK (NHS DSPT):** Focus on "Zero Trust," strict auditing, and data minimization.
    * **EU (GDPR):** Focus on "Right to be Forgotten" and data residency.

---

## 9. Threat Model

This prototype follows a **Zero Trust** approach and assumes that every identity, device, and network path may be compromised unless explicitly verified.
Key threats and mitigations:
* **Unauthorized Access to Clinical Data**
       Mitigation: IAM least privilege, Cognito MFA, role based access (clinician vs auditor vs receptionist).
* **Cross Region Data Leakage**
       Mitigation: No raw data stored globally; only pseudonymised MPI pointers cross borders; data decrypted only in its home region.
* **Account or Credential Compromise**
       Mitigation: CloudTrail auditing, S3 Object Lock, automated alerts (SNS/SQS), and Lambda workflows to revoke access.
* **Lateral Movement Across Regions**
       Mitigation: Separate VPCs (prototype) or separate AWS accounts (production), no direct cross account access, private API Gateway endpoints only.
* **Service Exposure to the Public Internet**
       Mitigation: Lambdas run in private subnets, DynamoDB/S3 accessed only via VPC Endpoints, API Gateway protected by WAF and Cognito.
* **Data Tampering or Loss**
       Mitigation: KMS encryption per region, DynamoDB point in time recovery, immutable audit logs.

---

## 10. Future Work

* **Expanded FHIR Support:** Condition, Consent, MedicationRequest resources.
* **Clinical Coding:** Real SNOMED CT examples (Asthma, MRI codes).
* **Analytics:** QuickSight dashboards for anonymized population health trends.
* **Alerting:** EventBridge/SNS notifications for critical observation values.
* **Frontend:** A clinician-facing UI (S3 + CloudFront + Cognito).
* **AI Integration:** The long term goal is to provide clinicians with **on demand clinical insights**, not just raw records. This includes:
    * **Longitudinal Pattern Detection:** Identify recurring issues (e.g., repeated respiratory complaints over several years) and highlight trends that may influence diagnosis.
    * **Cross Border Clinical Context: ** Use Comprehend Medical to extract conditions, symptoms, medications, and procedures from foreign language notes, reducing language barriers and improving continuity of care.
    * **Symptom Correlation & Risk Flags: ** Detect combinations of symptoms or historical events that may indicate alternative diagnoses or require urgent attention.
    * **Visual Clinical Timeline: ** Provide a timeline view (QuickSight or custom frontend) showing encounters, observations, medications, and major events across regions.
    * **On Demand Summaries:** Generate concise summaries of the patient’s history to reduce clinician workload and avoid missed details.


---

## 11. License
MIT