#!/usr/bin/env python3
"""
Standard Remediation Playbooks

Pre-built playbooks for common security findings across AWS, GCP, and Azure.
"""

from .playbook_engine import RemediationPlaybook


class PlaybookLibrary:
    """Library of standard remediation playbooks."""
    
    @staticmethod
    def create_aws_public_s3_bucket_playbook() -> RemediationPlaybook:
        """Playbook to remediate public S3 buckets."""
        playbook = RemediationPlaybook(
            playbook_id="AWS-PUBLIC-S3",
            name="Fix Public S3 Bucket",
            description="Automatically restricts public access to S3 bucket",
            finding_category="Storage",
            severity="CRITICAL"
        )
        
        playbook.add_action(
            action_name="block_public_access",
            action_type="aws",
            params={
                "service": "s3",
                "action": "put-public-access-block",
                "params": {
                    "BlockPublicAcls": True,
                    "IgnorePublicAcls": True,
                    "BlockPublicPolicy": True,
                    "RestrictPublicBuckets": True
                }
            }
        )
        
        playbook.add_action(
            action_name="notify_security_team",
            action_type="notification",
            params={
                "type": "slack",
                "channel": "#security-alerts",
                "message": "S3 bucket public access blocked"
            }
        )
        
        return playbook
    
    @staticmethod
    def create_aws_unencrypted_ebs_playbook() -> RemediationPlaybook:
        """Playbook to enable encryption on unencrypted EBS volumes."""
        playbook = RemediationPlaybook(
            playbook_id="AWS-EBS-ENCRYPTION",
            name="Enable EBS Encryption",
            description="Enables encryption for unencrypted EBS volumes",
            finding_category="Compute",
            severity="HIGH"
        )
        
        playbook.add_action(
            action_name="enable_ebs_encryption_by_default",
            action_type="aws",
            params={
                "service": "ec2",
                "action": "enable-ebs-encryption-by-default"
            }
        )
        
        playbook.add_prerequisite("volume_has_no_snapshots")
        playbook.requires_approval = True
        
        return playbook
    
    @staticmethod
    def create_aws_open_security_group_playbook() -> RemediationPlaybook:
        """Playbook to fix overly permissive security groups."""
        playbook = RemediationPlaybook(
            playbook_id="AWS-SG-RESTRICTION",
            name="Restrict Security Group",
            description="Removes overly permissive ingress rules",
            finding_category="Network",
            severity="HIGH"
        )
        
        playbook.add_action(
            action_name="remove_0_0_0_0_rules",
            action_type="aws",
            params={
                "service": "ec2",
                "action": "revoke-security-group-ingress",
                "filter": "CidrIp=0.0.0.0/0"
            }
        )
        
        playbook.requires_approval = True
        playbook.rollback_enabled = True
        
        return playbook
    
    @staticmethod
    def create_gcp_public_bucket_playbook() -> RemediationPlaybook:
        """Playbook to fix public GCS buckets."""
        playbook = RemediationPlaybook(
            playbook_id="GCP-PUBLIC-BUCKET",
            name="Restrict GCS Bucket Access",
            description="Removes public access from GCS buckets",
            finding_category="Storage",
            severity="CRITICAL"
        )
        
        playbook.add_action(
            action_name="remove_public_access",
            action_type="gcp",
            params={
                "service": "storage",
                "action": "set-bucket-iam-policy",
                "policy": {
                    "bindings": []
                }
            }
        )
        
        playbook.requires_approval = True
        
        return playbook
    
    @staticmethod
    def create_gcp_compute_firewall_playbook() -> RemediationPlaybook:
        """Playbook to restrict GCP firewall rules."""
        playbook = RemediationPlaybook(
            playbook_id="GCP-FW-RESTRICTION",
            name="Restrict Firewall Rule",
            description="Removes overly permissive firewall rules",
            finding_category="Network",
            severity="HIGH"
        )
        
        playbook.add_action(
            action_name="delete_permissive_rule",
            action_type="gcp",
            params={
                "service": "compute",
                "action": "delete-firewall",
                "filter": "sourceRanges=['0.0.0.0/0']"
            }
        )
        
        playbook.requires_approval = True
        
        return playbook
    
    @staticmethod
    def create_azure_public_blob_playbook() -> RemediationPlaybook:
        """Playbook to restrict public access to Azure Blob Storage."""
        playbook = RemediationPlaybook(
            playbook_id="AZURE-BLOB-PUBLIC",
            name="Restrict Blob Storage Access",
            description="Changes public blob containers to private",
            finding_category="Storage",
            severity="CRITICAL"
        )
        
        playbook.add_action(
            action_name="set_container_to_private",
            action_type="azure",
            params={
                "service": "storage",
                "action": "set-container-access-level",
                "access_level": "Private"
            }
        )
        
        playbook.requires_approval = True
        
        return playbook
    
    @staticmethod
    def create_azure_nsg_restriction_playbook() -> RemediationPlaybook:
        """Playbook to restrict Azure NSG rules."""
        playbook = RemediationPlaybook(
            playbook_id="AZURE-NSG-RESTRICTION",
            name="Restrict Network Security Group",
            description="Removes overly permissive NSG rules",
            finding_category="Network",
            severity="HIGH"
        )
        
        playbook.add_action(
            action_name="remove_open_rules",
            action_type="azure",
            params={
                "service": "network",
                "action": "remove-security-rule",
                "filter": "sourceAddressPrefix='*'"
            }
        )
        
        playbook.requires_approval = True
        playbook.rollback_enabled = True
        
        return playbook
    
    @staticmethod
    def create_enable_logging_playbook() -> RemediationPlaybook:
        """Playbook to enable logging on resources."""
        playbook = RemediationPlaybook(
            playbook_id="ENABLE-LOGGING",
            name="Enable Resource Logging",
            description="Enables CloudTrail/audit logging on resources",
            finding_category="Compliance",
            severity="MEDIUM"
        )
        
        playbook.add_action(
            action_name="enable_cloudtrail",
            action_type="aws",
            params={
                "service": "cloudtrail",
                "action": "start-logging"
            }
        )
        
        playbook.add_action(
            action_name="enable_s3_logging",
            action_type="aws",
            params={
                "service": "s3",
                "action": "put-bucket-logging"
            }
        )
        
        return playbook
    
    @staticmethod
    def create_enable_mfa_playbook() -> RemediationPlaybook:
        """Playbook to enable MFA on privileged accounts."""
        playbook = RemediationPlaybook(
            playbook_id="ENABLE-MFA",
            name="Enable MFA on Privileged Account",
            description="Sends notification to enable MFA",
            finding_category="IAM",
            severity="CRITICAL"
        )
        
        playbook.add_action(
            action_name="send_mfa_requirement_notification",
            action_type="notification",
            params={
                "type": "email",
                "subject": "Required: Enable MFA on Your Account",
                "template": "mfa_requirement"
            }
        )
        
        playbook.requires_approval = False
        
        return playbook
    
    @staticmethod
    def create_rotate_credentials_playbook() -> RemediationPlaybook:
        """Playbook to rotate exposed credentials."""
        playbook = RemediationPlaybook(
            playbook_id="ROTATE-CREDENTIALS",
            name="Rotate Exposed Credentials",
            description="Deactivates old credentials and generates new ones",
            finding_category="IAM",
            severity="CRITICAL"
        )
        
        playbook.add_action(
            action_name="deactivate_access_key",
            action_type="aws",
            params={
                "service": "iam",
                "action": "update-access-key-status",
                "status": "Inactive"
            }
        )
        
        playbook.add_action(
            action_name="create_new_access_key",
            action_type="aws",
            params={
                "service": "iam",
                "action": "create-access-key"
            }
        )
        
        playbook.requires_approval = True
        playbook.rollback_enabled = True
        
        return playbook
    
    @staticmethod
    def get_all_playbooks() -> dict:
        """Get all available playbooks."""
        return {
            "AWS-PUBLIC-S3": PlaybookLibrary.create_aws_public_s3_bucket_playbook(),
            "AWS-EBS-ENCRYPTION": PlaybookLibrary.create_aws_unencrypted_ebs_playbook(),
            "AWS-SG-RESTRICTION": PlaybookLibrary.create_aws_open_security_group_playbook(),
            "GCP-PUBLIC-BUCKET": PlaybookLibrary.create_gcp_public_bucket_playbook(),
            "GCP-FW-RESTRICTION": PlaybookLibrary.create_gcp_compute_firewall_playbook(),
            "AZURE-BLOB-PUBLIC": PlaybookLibrary.create_azure_public_blob_playbook(),
            "AZURE-NSG-RESTRICTION": PlaybookLibrary.create_azure_nsg_restriction_playbook(),
            "ENABLE-LOGGING": PlaybookLibrary.create_enable_logging_playbook(),
            "ENABLE-MFA": PlaybookLibrary.create_enable_mfa_playbook(),
            "ROTATE-CREDENTIALS": PlaybookLibrary.create_rotate_credentials_playbook(),
        }
    
    @staticmethod
    def get_playbook_by_category(category: str) -> dict:
        """Get playbooks for a specific finding category."""
        all_playbooks = PlaybookLibrary.get_all_playbooks()
        return {
            pb_id: pb for pb_id, pb in all_playbooks.items()
            if pb.finding_category.lower() == category.lower()
        }
    
    @staticmethod
    def get_playbooks_by_severity(severity: str) -> dict:
        """Get playbooks for a specific severity level."""
        all_playbooks = PlaybookLibrary.get_all_playbooks()
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        threshold = severity_order.get(severity, 999)
        
        return {
            pb_id: pb for pb_id, pb in all_playbooks.items()
            if severity_order.get(pb.severity, 999) <= threshold
        }
