# Enterprise Semantic RAG Knowledge Base — Thematic Taxonomy & Sample Catalog

- **Database Location**: `./data/knowledge_base.db` (Portable SQLite + FTS5 Full-Text Search)
- **CLI Search Tool**: `./search_kb.py`
- **Static Explorer Preview**: `./kb_explorer.html`
- **Full Interactive Web UI**: `./webapp/app.py` (`http://localhost:8080`)
- **Sample Dataset Summary**:
  - **Primary Sample Files**: 12
  - **Sample Indexed Emails (`.eml`)**: 2
  - **Sample CMDB Records**: 8 across 8 structured tables
  - **Sample Client Organizations**: 5 (`ACME`, `GLBX`, `INIT`, `WAYN`, `STRK`)

---

## 1. Thematic Taxonomy & Distribution (Sample Dataset)

| Primary Thematic Domain | Total Items | Docs & Scripts | Emails | Top Sub-Themes |
| :--- | ---: | ---: | ---: | :--- |
| **Backup & Disaster Recovery (BCDR)** | 3 | 2 | 1 | Veeam Backup & Replication (2), Acronis Cyber Protect (1), NAS & Storage Infrastructure (1) |
| **Cybersecurity, Identity & Network Security** | 3 | 2 | 1 | Firewalls, VPN & Perimeter (2), MFA, Zero-Trust & Identity Security (2), Microsoft 365 & Exchange Online (1) |
| **Cloud, Virtualization & Core Infrastructure** | 2 | 2 | 0 | VMware vSphere, ESXi & vCenter (1), Microsoft Azure & Cloud Infrastructure (1) |
| **RMM, Automation & Endpoint Management** | 1 | 1 | 0 | PowerShell, Bash & CLI Scripting (1), Certificates, Encryption & BitLocker (1) |
| **MSP Operations, NOC & Service Delivery** | 1 | 1 | 0 | Standard Operating Procedures (SOPs) & Tutorials (1), Centralized Services & NOC Operations (1), PSA & Service Management (1) |
| **Documentation & CMDB Configuration Management** | 1 | 1 | 0 | Documentation Exports & Runbooks (1), Licensing, Domains & Asset Inventory (1), Automated Documentation (1) |
| **Training, Certifications & Professional Notes** | 1 | 1 | 0 | Technical Certifications (1), Linux, Docker & SQL Databases (1) |

---

## 2. Sample Organizations

| Code | Organization Name | Status | Sample Files | CMDB Configs | CMDB Backups | CMDB Servers |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `ACME` | **Acme Corporation** | Active | 3 | 2 | 1 | 1 |
| `GLBX` | **Globex Corporation** | Active | 2 | 2 | 1 | 1 |
| `INIT` | **Initech Systems** | Active | 2 | 2 | 1 | 1 |
| `WAYN` | **Wayne Enterprises** | Active | 1 | 1 | 1 | 1 |
| `STRK` | **Stark Industries** | Active | 1 | 1 | 1 | 1 |

---

## 3. Sample Artifacts by Domain

### Backup & Disaster Recovery (BCDR)
- `Documents/Clients/ACME/ACME_Veeam_BDR_Retention_Runbook.docx` — **Acme Corp — Veeam Backup & Disaster Recovery Runbook** (`ACME`)
- `Documents/Clients/ACME/ACME_Acronis_Cloud_Cutover_Checklist.xlsx` — **Acme Corp — Acronis Cyber Protect Cloud Cutover Schedule** (`ACME`)
- `Emails/Client/ACME_Veeam_Restore_Verification.eml` — **Completed Quarterly Veeam SureBackup DR Test for ACME-DC01** (`ACME`)

### Cybersecurity, Identity & Network Security
- `Documents/Clients/GLBX/GLBX_SonicWall_HA_VPN_Architecture.pdf` — **Globex Corporation — SonicWall NSA 2700 High-Availability & SAML VPN Design** (`GLBX`)
- `Documents/Clients/STRK/STRK_M365_Conditional_Access_GDAP_Baseline.pdf` — **Stark Industries — Microsoft 365 Zero-Trust Conditional Access & DMARC/DKIM Baseline** (`STRK`)
- `Emails/Client/GLBX_SonicWall_Firmware_Maintenance.eml` — **Scheduled SonicOS 7.1 HA Maintenance Window Confirmation** (`GLBX`)

### Cloud, Virtualization & Core Infrastructure
- `Documents/Clients/INIT/INIT_VMware_vSphere8_Cluster_Upgrade_Plan.md` — **Initech Systems — VMware vCenter 8.0U3 & ESXi Rolling Host Upgrade Plan** (`INIT`)
- `Documents/Clients/WAYN/WAYN_Azure_Virtual_WAN_ExpressRoute_SOP.docx` — **Wayne Enterprises — Azure Virtual WAN & BGP Site-to-Site Failover Runbook** (`WAYN`)

### RMM, Automation & Endpoint Management
- `Documents/Scripting/Invoke-BitLockerKeyEscrowAudit.ps1` — **PowerShell Automation — BitLocker Recovery Key Escrow & AD Verification** (`INIT`)

### MSP Operations, CMDB & Engineering Notes
- `Documents/Internal/NOC_Alert_Triage_And_Escalation_Matrix_SOP.docx` — **Global NOC — RMM Alert Triage, Backup Verification & Escalation Matrix SOP**
- `Documents/Internal/CMDB_Quarterly_Asset_Reconciliation_Guide.md` — **CMDB Configuration Management — Quarterly Asset & SSL/Domain Expiration Audit**
- `Documents/Trainings/Cloud_Security_And_Kubernetes_Architecture_Notes.md` — **Engineering Study Notes — Container Hardening, Zero-Trust Networking & AZ-104**
