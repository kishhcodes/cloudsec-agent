```
╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                    CLOUD SECURITY ASSISTANT - UPDATED ARCHITECTURE                                                    ║
║                                          (Post Feature Implementation)                                                                  ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                           USER INTERFACE LAYER                                                                          │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                                          │
│    ┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐                          │
│    │   CLI Tool   │      │  REST API    │      │  Web         │      │  Slack Bot   │      │  Email       │                          │
│    │ (main_cli.   │      │  (FastAPI)   │      │  Dashboard   │      │  Integration │      │  Notifications                          │
│    │  py)         │      │  [NEW]       │      │  [NEW]       │      │  [NEW]       │      │  [NEW]       │                          │
│    └──────┬───────┘      └──────┬───────┘      └──────┬───────┘      └──────┬───────┘      └──────┬───────┘                          │
│           │                     │                     │                     │                     │                                    │
│           └─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┘                                    │
│                                               │                                                                                         │
└───────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────┘
                                                │
┌───────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    ORCHESTRATION & ROUTING LAYER                                                                       │
├───────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────┤
│                                               ▼                                                                                         │
│    ┌──────────────────────────────────────────────────────────────────────────────────┐                                               │
│    │          Cloud Assistant (main_cli.py)                                           │                                               │
│    │  ┌───────────────────────────────────────────────────────────────────────────┐   │                                               │
│    │  │ Natural Language Parser + Intent Detection                               │   │                                               │
│    │  │ ├─ AWS Keywords                                                          │   │                                               │
│    │  │ ├─ GCP Keywords                                                          │   │                                               │
│    │  │ ├─ Azure Keywords [PLANNED]                                             │   │                                               │
│    │  │ ├─ Audit Keywords ("Perform a full audit")  [NEW]                        │   │                                               │
│    │  │ └─ Report Keywords                                                       │   │                                               │
│    │  └───────────────────────────────────────────────────────────────────────────┘   │                                               │
│    │                                     │                                            │                                               │
│    │  ┌─────────────────────────────────────────────────────────────────────────────┐ │                                               │
│    │  │ Agent Router & State Manager                                              │ │                                               │
│    │  │ ├─ AgentMode.AWS_SECURITY                                                │ │                                               │
│    │  │ ├─ AgentMode.GCP_SECURITY                                                │ │                                               │
│    │  │ ├─ AgentMode.AZURE_SECURITY [PLANNED]                                   │ │                                               │
│    │  │ ├─ AgentMode.COMPLIANCE_BOT                                              │ │                                               │
│    │  │ └─ AgentMode.SECURITY_ANALYZER                                           │ │                                               │
│    │  └─────────────────────────────────────────────────────────────────────────────┘ │                                               │
│    └──────────────────────────────────────────────────────────────────────────────────┘                                               │
│                                     │                                                                                                  │
└─────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
┌───────▼────────────┐    ┌──────────▼──────────┐    ┌────────────▼────────────┐
│  AWS AGENT LAYER   │    │  GCP AGENT LAYER   │    │  AZURE AGENT LAYER      │
└───────┬────────────┘    └──────────┬──────────┘    └────────────┬────────────┘
        │                            │                            │
        │                            │                            │
        │                    ┌───────▼──────────┐                 │
        │                    │ [PLANNED]        │                 │
        │                    └──────────────────┘                 │


┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                      SECURITY AGENTS LAYER                                                                               │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                                            │
│  ┌─────────────────────────────┐    ┌──────────────────────────┐    ┌──────────────────────────┐                                       │
│  │   AWS Security Agent        │    │   GCP Security Agent     │    │   Azure Security Agent   │                                       │
│  │   (aws_security_agent.py)   │    │   (gcp_security/        │    │   [PLANNED]              │                                       │
│  │                             │    │    agent.py)            │    │                          │                                       │
│  ├─────────────────────────────┤    ├──────────────────────────┤    ├──────────────────────────┤                                       │
│  │ Security Analysis Methods:  │    │ Security Analysis:       │    │ Security Analysis:       │                                       │
│  │ • analyze_iam_security()    │    │ • analyze_iam_security() │    │ • Entra ID security     │                                       │
│  │ • analyze_storage_security()│    │ • analyze_storage_..()   │    │ • Azure RBAC audit      │                                       │
│  │ • analyze_compute_security()│    │ • analyze_compute_...()  │    │ • VM security review    │                                       │
│  │ • analyze_network_security()│    │ • analyze_network_...()  │    │ • SQL security          │                                       │
│  ├─────────────────────────────┤    ├──────────────────────────┤    └──────────────────────────┘                                       │
│  │                             │    │                          │                                                                        │
│  │ ▶ FULL AUDIT METHOD [NEW]   │    │ ▶ FULL AUDIT METHOD [NEW]                                                                       │
│  │   └─ perform_full_audit()   │    │   └─ perform_full_audit()                                                                        │
│  │      • EC2 security         │    │      • GCE security                                                                               │
│  │      • S3 security          │    │      • GCS security                                                                               │
│  │      • VPC analysis         │    │      • VPC analysis                                                                               │
│  │      • IAM security         │    │      • IAM security                                                                               │
│  │      └─ PDF Report Export   │    │      └─ PDF Report Export                                                                        │
│  └─────────────────────────────┘    └──────────────────────────┘                                                                        │
│           │                                  │                                                                                          │
└───────────┼──────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────┘
            │                                  │
            └──────────────────────────────────┘
                           │


┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    AUDIT & REPORTING MODULE [NEW]                                                                        │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                                          │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐                  │
│  │  Audit Report Generator (src/audit/audit_generator.py)                                                          │                  │
│  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤                  │
│  │                                                                                                                   │                  │
│  │  ┌────────────────────────────┐    ┌─────────────────────────────────────────────────────────────────────┐    │                  │
│  │  │ AuditReport (Base Class)   │    │ Report Components:                                                  │    │                  │
│  │  ├────────────────────────────┤    ├─────────────────────────────────────────────────────────────────────┤    │                  │
│  │  │ • add_iam_analysis()       │    │ • Title Page (Report ID, Date, Scope)                              │    │                  │
│  │  │ • add_storage_analysis()   │    │ • Executive Summary (Finding counts by severity)                  │    │                  │
│  │  │ • add_compute_analysis()   │    │ • Detailed Sections (IAM, Storage, Compute, Network)             │    │                  │
│  │  │ • add_network_analysis()   │    │ • Risk Assessment Matrix                                          │    │                  │
│  │  │ • generate_pdf()           │    │ • Remediation Roadmap (Immediate, Short, Medium, Long-term)     │    │                  │
│  │  │ • display_summary()        │    │ • Custom Header/Footer with branding                             │    │                  │
│  │  └────────────────────────────┘    └─────────────────────────────────────────────────────────────────────┘    │                  │
│  │           │                                                                                                      │                  │
│  │           ├── AWSAuditReport                                                                                    │                  │
│  │           │   └─ AWS-specific audit logic                                                                       │                  │
│  │           │                                                                                                      │                  │
│  │           └── GCPAuditReport                                                                                    │                  │
│  │               └─ GCP-specific audit logic                                                                       │                  │
│  │                                                                                                                   │                  │
│  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘                  │
│                                                                                                                          │               │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────┘
                                                                                                                           │


┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     NOTIFICATION & INTEGRATION LAYER [NEW]                                                               │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                                            │
│  ┌──────────────────────────┐  ┌──────────────────────────┐  ┌──────────────────────────┐  ┌──────────────────────────┐                │
│  │  Webhook Notifications   │  │  Report Exporters        │  │  Alert Aggregator        │  │  Integration Adapters    │                │
│  │  [NEW]                   │  │  [NEW]                   │  │  [NEW]                   │  │  [PLANNED]               │                │
│  ├──────────────────────────┤  ├──────────────────────────┤  ├──────────────────────────┤  ├──────────────────────────┤                │
│  │ • Slack Integration      │  │ • PDF (ReportLab)        │  │ • Finding Aggregation    │  │ • ServiceNow ITSM        │                │
│  │ • Teams Integration      │  │ • HTML Reports [PLANNED] │  │ • Severity Deduplication │  │ • Jira Integration       │                │
│  │ • Webhook Payloads       │  │ • JSON Export [PLANNED]  │  │ • Trend Analysis         │  │ • GitHub Issues          │                │
│  │ • Event-driven Alerts    │  │ • CSV Export [PLANNED]   │  │ • Email Summaries        │  │ • Webhook Endpoints      │                │
│  └──────────────────────────┘  └──────────────────────────┘  └──────────────────────────┘  └──────────────────────────┘                │
│           │                              │                              │                              │                              │
│           └──────────────────────────────┴──────────────────────────────┴──────────────────────────────┘                              │
│                                          │                                                                                              │
└──────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┘
                                           │


┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    CLOUD PROVIDER INTEGRATION LAYER                                                                       │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                                            │
│  ┌──────────────────────┐    ┌──────────────────────┐    ┌──────────────────────┐    ┌──────────────────────┐                        │
│  │      AWS             │    │      GCP             │    │    Azure             │    │   Monitoring Tools   │                        │
│  │   Services           │    │   Services           │    │   Services           │    │   [PLANNED]          │                        │
│  ├──────────────────────┤    ├──────────────────────┤    ├──────────────────────┤    ├──────────────────────┤                        │
│  │ • STS              │    │ • Projects API       │    │ • Microsoft Graph    │    │ • CloudWatch         │                        │
│  │ • IAM              │    │ • IAM Admin API      │    │ • Azure RBAC         │    │ • Cloud Logging      │                        │
│  │ • S3               │    │ • Storage API        │    │ • Storage API        │    │ • Prometheus [PLAN]  │                        │
│  │ • EC2              │    │ • Compute API        │    │ • Azure VMs          │    │ • Grafana [PLAN]     │                        │
│  │ • VPC/Security Grp │    │ • Network API        │    │ • Virtual Networks   │    │ • Splunk [PLAN]      │                        │
│  │ • MCP Server       │    │ • Resource Manager   │    │ • SQL Servers        │    │                      │                        │
│  └──────────────────────┘    └──────────────────────┘    └──────────────────────┘    └──────────────────────┘                        │
│           │                            │                           │                            │                                    │
└───────────┼────────────────────────────┼───────────────────────────┼────────────────────────────┼───────────────────────────────────┘
            │                            │                           │                            │
            │                            │                           │                            │
            └────────────────────────────┴───────────────────────────┴────────────────────────────┘
                                         │


┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                        DATA STORAGE & PERSISTENCE LAYER                                                                   │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                                            │
│  ┌──────────────────────────────────┐  ┌────────────────────────────────┐  ┌────────────────────────────────┐                          │
│  │  Local File System               │  │  Database (SQLite/PostgreSQL)  │  │  Cloud Storage                 │                          │
│  │  [Existing]                      │  │  [NEW - Optional]              │  │  [PLANNED]                     │                          │
│  ├──────────────────────────────────┤  ├────────────────────────────────┤  ├────────────────────────────────┤                          │
│  │ • /reports/                      │  │ • Audit Report History         │  │ • S3 Bucket (AWS Audits)      │                          │
│  │   - PDF Audit Reports [NEW]      │  │ • Finding Trends               │  │ • GCS Bucket (GCP Audits)     │                          │
│  │   - JSON Results [NEW]           │  │ • Risk Metrics                 │  │ • Azure Blob Storage [PLAN]   │                          │
│  │ • /data/                         │  │ • Compliance Status            │  │ • Automatic Retention Policies│                          │
│  │   - embeddings/                  │  │ • Scan History                 │  │                                │                          │
│  │   - processed/                   │  └────────────────────────────────┘  └────────────────────────────────┘                          │
│  │   - raw/                         │                                                                                                    │
│  │ • /config/                       │                                                                                                    │
│  │   - vertex.json                  │                                                                                                    │
│  └──────────────────────────────────┘                                                                                                    │
│                                                                                                                                            │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘


┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                            LLM & AI LAYER                                                                                 │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                                            │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐  ┌──────────────────────────────────────────────┐                   │
│  │  Gemini LLM Integration     │  │  Embedding Models           │  │  ML Capabilities [PLANNED]                   │                   │
│  │  (Gemini 2.5 Pro)           │  │  (embedding-002)            │  │                                              │                   │
│  ├─────────────────────────────┤  ├─────────────────────────────┤  ├──────────────────────────────────────────────┤                   │
│  │ • Query Understanding       │  │ • Document Embeddings       │  │ • Anomaly Detection                        │                   │
│  │ • Security Analysis         │  │ • Semantic Search           │  │ • Predictive Risk Scoring [PLANNED]        │                   │
│  │ • Recommendation Generation │  │ • Similarity Matching       │  │ • Compliance Pattern Recognition [PLAN]    │                   │
│  │ • Natural Language Queries  │  │ • Vector Storage            │  │ • Automated Threat Intelligence [PLAN]     │                   │
│  │ • Report Generation         │  │ • RAG Framework             │  │ • ML-driven Recommendations [PLANNED]      │                   │
│  └─────────────────────────────┘  └─────────────────────────────┘  └──────────────────────────────────────────────┘                   │
│           │                                  │                                        │                                                │
└───────────┼──────────────────────────────────┼────────────────────────────────────────┼────────────────────────────────────────────────┘
            │                                  │                                        │
            │ LangChain Integration             │                                        │
            │ (Prompt Templates, Chains)        │                                        │
            │                                  │                                        │
            └──────────────────────────────────┴────────────────────────────────────────┘
                           │
                           ▼
                    Google Generative AI
                    (API Endpoints)


═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

DATA FLOW - FULL AUDIT EXAMPLE:

User Input: "Perform a full audit"
            │
            ▼
    Natural Language Parser
            │
            ▼
    Route to AWS/GCP Agent
            │
            ├─────► Agent.perform_full_audit()
            │       │
            │       ├─► _audit_iam_security()        ──► AuditReport.add_iam_analysis()
            │       │
            │       ├─► _audit_storage_security()    ──► AuditReport.add_storage_analysis()
            │       │
            │       ├─► _audit_compute_security()    ──► AuditReport.add_compute_analysis()
            │       │
            │       └─► _audit_network_security()    ──► AuditReport.add_network_analysis()
            │
            ▼
    Generate PDF Report
            │
            ├─► Title Page
            ├─► Executive Summary
            ├─► Detailed Findings (with color-coded severity)
            ├─► Risk Assessment Matrix
            └─► Remediation Roadmap
            │
            ▼
    Save to /reports/
            │
            ├─► PDF file: {PROVIDER}-AUDIT-{TIMESTAMP}.pdf
            │
            └─► Display Summary to User
                └─► Return PDF path + Summary stats


═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

FEATURE IMPLEMENTATION STATUS:

┌─ CORE INFRASTRUCTURE ────────────────────────────────────────────┐
│ ✅ AWS Security Agent                                            │
│ ✅ GCP Security Agent                                            │
│ ✅ Natural Language Processing                                   │
│ ✅ LLM Integration (Gemini 2.5 Pro)                             │
│ ⏳ Azure Security Agent [In Planning]                           │
│ ⏳ Monitoring Dashboard [In Planning]                           │
└──────────────────────────────────────────────────────────────────┘

┌─ AUDIT & REPORTING ──────────────────────────────────────────────┐
│ ✅ Full Audit Framework (AWS & GCP)                             │
│ ✅ PDF Report Generation                                         │
│ ✅ IAM, Storage, Compute, Network Analysis                      │
│ ⏳ HTML Reports [Planned]                                       │
│ ⏳ JSON/CSV Export [Planned]                                    │
│ ⏳ Comparative Analysis [Planned]                               │
└──────────────────────────────────────────────────────────────────┘

┌─ NOTIFICATIONS & INTEGRATIONS ───────────────────────────────────┐
│ ⏳ Slack Integration [Planned]                                  │
│ ⏳ Teams Integration [Planned]                                  │
│ ⏳ Email Notifications [Planned]                                │
│ ⏳ ServiceNow/Jira [Planned]                                    │
│ ⏳ Webhook Endpoints [Planned]                                  │
└──────────────────────────────────────────────────────────────────┘

┌─ ADVANCED FEATURES ──────────────────────────────────────────────┐
│ ⏳ REST API [Planned]                                           │
│ ⏳ Web Dashboard [Planned]                                      │
│ ⏳ Database Storage [Planned]                                   │
│ ⏳ Compliance Monitoring [Planned]                              │
│ ⏳ ML-based Threat Detection [Planned]                          │
│ ⏳ Multi-cloud Environment Support [Planned]                    │
└──────────────────────────────────────────────────────────────────┘

Key: ✅ Complete  |  ⏳ Planned/In Progress
```
