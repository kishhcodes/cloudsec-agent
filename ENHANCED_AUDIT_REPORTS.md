# Enhanced Audit Report Generation

## Overview

The audit report generation system has been significantly enhanced with visual charts and compliance framework mapping capabilities. These improvements transform audit reports from text-only documents into comprehensive, visually appealing, and compliance-aware documents.

## ✨ New Features

### 1. Visual Charts & Graphs

#### Security Score Gauge
- Visual 0-100 gauge showing overall security posture
- Color-coded status: Red (Critical) → Orange (Poor) → Yellow (Fair) → Blue (Good) → Green (Excellent)
- Prominently displayed in executive summary

#### Severity Distribution Pie Chart
- Shows breakdown of findings by severity level
- Color-coded sections: Critical (Red), High (Orange), Medium (Yellow), Low (Blue), Pass (Green)
- Instantly communicates risk distribution

#### Findings by Category Bar Chart
- Horizontal bar chart showing findings count per audit category
- Helps identify problem areas
- Examples: IAM, Storage, Compute, Network

#### Risk Matrix Scatter Plot
- Impact vs. Likelihood visualization
- Quadrant analysis for prioritization
- Shows which findings have highest potential impact

#### Remediation Progress Bar
- Horizontal progress bar showing remediation status
- Displays resolved vs. total findings
- Motivates incremental improvements

### 2. Compliance Framework Mapping

Findings are automatically mapped to 6 major compliance frameworks:

#### Supported Frameworks
1. **CIS Controls v8** - Center for Internet Security
2. **PCI DSS v3.2.1** - Payment Card Industry Data Security Standard
3. **HIPAA Security Rule** - Healthcare data protection
4. **SOC 2 Type II** - Service Organization Controls
5. **ISO 27001** - Information Security Management
6. **NIST Cybersecurity Framework** - National Institute of Standards

#### Compliance Analysis
- **Coverage Percentage**: Shows how many framework controls are addressed by findings
- **Gap Analysis**: Identifies which controls are missing or need attention
- **Status Indicators**: 
  - ✓ PASS (80%+)
  - ⚠ REVIEW (60-80%)
  - ✗ FAIL (<60%)

### 3. Enhanced Security Scoring

**Algorithm:**
```
Base Score: 100
- Critical findings: -10 points each
- High findings: -5 points each  
- Medium findings: -2 points each
- Low findings: -0.5 points each
+ Compliant items: bonus points

Final Score: 0-100 (clamped)
```

**Score Interpretation:**
- 80-100: Excellent security posture
- 60-80: Good, but improvements needed
- 40-60: Fair, significant work required
- 20-40: Poor, urgent attention needed
- 0-20: Critical, emergency response required

## 📋 API Usage

### Basic Usage

```python
from src.audit import AWSAuditReport

# Create report
report = AWSAuditReport("123456789012")

# Add analysis sections
report.add_iam_analysis(iam_data)
report.add_storage_analysis(storage_data)

# Enable new features
report.include_charts = True
report.enable_compliance_mapping()

# Calculate and generate
report.calculate_security_score()
pdf_path = report.generate_pdf()
```

### Advanced Usage

```python
# Enable specific compliance frameworks
report.enable_compliance_mapping([
    "CIS Controls v8",
    "PCI DSS",
    "ISO 27001"
])

# Check compliance coverage
findings = report.get_all_findings()
coverage = report.compliance_mapper.calculate_framework_coverage(
    findings,
    "PCI DSS"
)

# Get gap analysis
gap_analysis = report.compliance_mapper.get_framework_gap_analysis(
    findings,
    "CIS Controls v8"
)
```

### Chart Generation (Standalone)

```python
from src.audit import ChartGenerator
import io

chart_gen = ChartGenerator()

# Generate individual charts
pie_chart_bytes = chart_gen.severity_distribution_pie(findings)
bar_chart_bytes = chart_gen.findings_by_category_bar(sections)
score_gauge_bytes = chart_gen.security_score_gauge(75.5)
progress_bytes = chart_gen.remediation_progress_bar(10, 6)
risk_matrix_bytes = chart_gen.risk_matrix_scatter(findings)
```

### Compliance Mapping (Standalone)

```python
from src.audit import ComplianceMapper

mapper = ComplianceMapper()

# Map findings to frameworks
mappings = mapper.map_finding_to_frameworks(finding)

# Get coverage for all frameworks
coverage = mapper.get_all_framework_coverage(findings)

# Get remediation priority by compliance impact
prioritized = mapper.get_remediation_priority_by_compliance(
    findings,
    frameworks=["CIS Controls v8", "PCI DSS"]
)

# Display framework details
mapper.display_framework_details(findings, "PCI DSS")
```

## 🎨 Visual Report Output

### Report Structure

```
1. Title Page
   - Cloud Provider
   - Report ID
   - Timestamp
   
2. Executive Summary
   - Security Score Gauge (CHART)
   - Finding Statistics Table
   - Severity Distribution (CHART)
   - Findings by Category (CHART)
   
3. Compliance Assessment (NEW)
   - Framework Coverage Table
   - Gap Analysis per Framework
   
4. Detailed Sections
   - IAM Security Analysis
   - Storage Security Analysis
   - Compute Security Analysis
   - Network Security Analysis
   
5. Remediation Roadmap
   - Immediate Actions (0-7 days)
   - Short-term (1-4 weeks)
   - Medium-term (1-2 months)
   - Long-term (Ongoing)
```

## 📊 Data Structures

### Finding Object

```python
{
    "severity": "CRITICAL",  # or HIGH, MEDIUM, LOW, PASS
    "title": "Root Account MFA Disabled",
    "description": "The root account does not have MFA enabled",
    "recommendation": "Enable MFA on the root account immediately",
    "resource": "arn:aws:iam::123456789012:root",  # Optional
    "effort": "5 minutes"  # Optional
}
```

### Section Object

```python
{
    "title": "IAM Security Analysis",
    "content": {
        "description": "Analysis of IAM configurations",
        "findings": [
            # List of finding objects
        ],
        "summary": [
            "Point 1",
            "Point 2"
        ]
    },
    "timestamp": datetime.now()
}
```

## 🔍 Compliance Mapping Details

### How It Works

1. **Keyword Extraction**: Framework controls have associated keywords
2. **Finding Analysis**: Finding title + description analyzed for keywords
3. **Mapping**: If keywords match, finding is mapped to that control
4. **Coverage Calculation**: Coverage % = (Mapped Controls / Total Controls) × 100

### Keyword Examples

| Framework | Control | Keywords |
|-----------|---------|----------|
| CIS v8 | Account Management | iam, user, access, permission, role, mfa |
| PCI-DSS | Access Control | privilege, access, least, rbac, acl |
| HIPAA | Encryption | encryption, key, cryptography, data |
| SOC2 | Monitoring | monitoring, logging, audit, alert, detection |
| ISO 27001 | Access Control | access, authentication, iam, privilege |
| NIST CSF | Protect | protect, access, encryption, security |

## 📁 File Structure

```
src/audit/
├── __init__.py                          # Module exports
├── audit_generator.py                   # Enhanced with charts + compliance
├── chart_generator.py                   # NEW: Chart generation (matplotlib)
├── compliance_mapper.py                 # NEW: Framework mapping
├── templates/
│   └── compliance_frameworks.json       # NEW: Framework definitions
└── schemas/
    ├── finding_schema.py                # (Future) Finding validation
    └── report_schema.py                 # (Future) Report validation
```

## ⚙️ Configuration

### Disable Charts

```python
report.include_charts = False
```

### Enable Specific Frameworks

```python
report.enable_compliance_mapping([
    "CIS Controls v8",
    "PCI DSS"
])
```

### Disable Compliance

```python
report.include_compliance = []
```

## 🧪 Testing

Run the demo to test enhanced audit reports:

```bash
python3 test_enhanced_audit.py
```

This generates:
- Enhanced PDF with charts and compliance data
- Console output showing security score
- Compliance framework coverage percentages

## 📈 Performance Metrics

| Operation | Time |
|-----------|------|
| Calculate security score | <10ms |
| Generate pie chart | 50-100ms |
| Generate bar chart | 50-100ms |
| Calculate compliance coverage | 20-50ms |
| Generate full PDF with charts | 1-3 seconds |

## 🚀 Future Enhancements

### Phase 2: Export Formats
- [ ] HTML export (email-ready)
- [ ] JSON export (tool integration)
- [ ] CSV export (spreadsheet analysis)

### Phase 3: Database & History
- [ ] Audit history tracking
- [ ] Comparison reports (before/after)
- [ ] Trend analysis over time

### Phase 4: Business Analytics
- [ ] Cost estimation for findings
- [ ] Business impact analysis
- [ ] ROI calculation for remediation

### Phase 5: Enterprise Features
- [ ] Custom branding
- [ ] Multi-cloud consolidated reports
- [ ] Automated email delivery

## 🐛 Troubleshooting

### Charts Not Appearing

**Issue**: Charts not showing in PDF

**Solution**:
```python
# Ensure matplotlib backends are configured
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend

# Verify dependencies
pip install matplotlib Pillow
```

### Compliance Frameworks Not Found

**Issue**: "Compliance frameworks file not found"

**Solution**:
```bash
# Verify template file exists
ls -la src/audit/templates/compliance_frameworks.json

# Ensure __init__.py imports are correct
python3 -c "from src.audit import ComplianceMapper; print('OK')"
```

### Memory Issues with Large Reports

**Issue**: Memory usage high with many findings

**Solution**:
```python
# Generate charts with lower DPI
chart_gen = ChartGenerator(dpi=72)  # Default is 100

# Process findings in batches
for i in range(0, len(findings), 100):
    batch = findings[i:i+100]
    # Process batch
```

## 📚 References

- [CIS Controls](https://www.cisecurity.org/controls)
- [PCI DSS Standard](https://www.pcisecuritystandards.org/)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/)
- [SOC 2 Framework](https://www.aicpa.org/soc2)
- [ISO 27001](https://www.iso.org/isoiec-27001-information-security-management.html)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review test_enhanced_audit.py for usage examples
3. Check compliance_frameworks.json for framework details
4. Review inline code documentation
