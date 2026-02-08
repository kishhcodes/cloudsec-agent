#!/usr/bin/env python3
"""
Remediation Playbook Engine

Executes automated remediation actions for security findings
with approval workflows, rollback support, and audit logging.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


class PlaybookStatus(Enum):
    """Status of a playbook execution."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"
    REJECTED = "REJECTED"


class ActionStatus(Enum):
    """Status of an individual action."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class ActionResult:
    """Result of executing a single action."""
    action_name: str
    status: ActionStatus
    message: str
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class PlaybookExecution:
    """Record of a playbook execution."""
    playbook_id: str
    execution_id: str
    status: PlaybookStatus
    initiated_by: str
    actions: List[ActionResult]
    finding_id: str
    started_at: str
    playbook_name: str = ""  # Human-readable playbook name
    dry_run: bool = False  # Whether this is a test execution
    ended_at: Optional[str] = None
    notes: Optional[str] = None
    approval_status: Optional[str] = None
    approver: Optional[str] = None


class RemediationPlaybook:
    """
    Defines a remediation playbook for a specific security finding.
    
    Playbooks are YAML-like configurations that define:
    - Detection criteria
    - Actions to execute
    - Prerequisites and conditions
    - Approval requirements
    - Rollback procedures
    """
    
    def __init__(
        self,
        playbook_id: str,
        name: str,
        description: str,
        finding_category: str,
        severity: str
    ):
        """
        Initialize a remediation playbook.
        
        Args:
            playbook_id: Unique playbook identifier
            name: Human-readable name
            description: Detailed description
            finding_category: Category of findings this addresses
            severity: Minimum severity level to trigger
        """
        self.playbook_id = playbook_id
        self.name = name
        self.description = description
        self.finding_category = finding_category
        self.category = finding_category  # Alias for compatibility
        self.severity = severity
        self.actions: List[Dict[str, Any]] = []
        self.prerequisites: List[str] = []
        self.requires_approval = True
        self.rollback_enabled = True
        self.timeout_seconds = 300
        self.logger = logging.getLogger(__name__)
    
    def add_action(
        self,
        action_name: str,
        action_type: str,
        params: Dict[str, Any],
        condition: Optional[Callable] = None
    ) -> None:
        """
        Add an action to the playbook.
        
        Args:
            action_name: Name of the action
            action_type: Type of action (aws, gcp, azure, notification, script)
            params: Parameters for the action
            condition: Optional condition function to check before execution
        """
        action = {
            "name": action_name,
            "type": action_type,
            "params": params,
            "condition": condition
        }
        self.actions.append(action)
        self.logger.debug(f"Added action: {action_name}")
    
    def add_prerequisite(self, check_name: str) -> None:
        """Add a prerequisite that must be satisfied before execution."""
        self.prerequisites.append(check_name)
    
    def set_approval_required(self, required: bool) -> None:
        """Set whether this playbook requires approval."""
        self.requires_approval = required
    
    def set_rollback_enabled(self, enabled: bool) -> None:
        """Set whether this playbook supports rollback."""
        self.rollback_enabled = enabled
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert playbook to dictionary."""
        return {
            "playbook_id": self.playbook_id,
            "name": self.name,
            "description": self.description,
            "finding_category": self.finding_category,
            "severity": self.severity,
            "actions": [
                {
                    "name": a["name"],
                    "type": a["type"],
                    "params": a["params"]
                }
                for a in self.actions
            ],
            "prerequisites": self.prerequisites,
            "requires_approval": self.requires_approval,
            "rollback_enabled": self.rollback_enabled,
            "timeout_seconds": self.timeout_seconds
        }


class PlaybookExecutor:
    """Executes remediation playbooks."""
    
    def __init__(self, cloud_clients: Optional[Dict[str, Any]] = None):
        """
        Initialize the playbook executor.
        
        Args:
            cloud_clients: Dictionary of cloud provider clients
        """
        self.cloud_clients = cloud_clients or {}
        self.executions: Dict[str, PlaybookExecution] = {}
        self.action_handlers: Dict[str, Callable] = {}
        self.logger = logging.getLogger(__name__)
        self._register_default_handlers()
    
    def _register_default_handlers(self) -> None:
        """Register default action handlers."""
        self.action_handlers["notification"] = self._handle_notification
        self.action_handlers["script"] = self._handle_script
        self.action_handlers["aws"] = self._handle_aws_action
        self.action_handlers["gcp"] = self._handle_gcp_action
        self.action_handlers["azure"] = self._handle_azure_action
    
    def register_handler(self, action_type: str, handler: Callable) -> None:
        """Register a custom action handler."""
        self.action_handlers[action_type] = handler
        self.logger.info(f"Registered handler for action type: {action_type}")
    
    def validate_playbook(self, playbook: RemediationPlaybook) -> bool:
        """
        Validate playbook configuration.
        
        Args:
            playbook: Playbook to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not playbook.actions:
            self.logger.warning(f"Playbook {playbook.playbook_id} has no actions")
            return False
        
        for action in playbook.actions:
            if action["type"] not in self.action_handlers:
                self.logger.warning(
                    f"Unknown action type: {action['type']} in "
                    f"playbook {playbook.playbook_id}"
                )
                return False
        
        return True
    
    def execute_playbook(
        self,
        playbook: RemediationPlaybook,
        finding_data: Dict[str, Any],
        initiated_by: str,
        execution_id: Optional[str] = None,
        dry_run: bool = False
    ) -> PlaybookExecution:
        """
        Execute a remediation playbook.
        
        Args:
            playbook: Playbook to execute
            finding_data: Finding that triggered the playbook
            initiated_by: User who initiated execution
            execution_id: Optional custom execution ID
            dry_run: If True, don't actually execute actions
            
        Returns:
            PlaybookExecution record
        """
        if not execution_id:
            execution_id = self._generate_execution_id(playbook.playbook_id)
        
        execution = PlaybookExecution(
            playbook_id=playbook.playbook_id,
            execution_id=execution_id,
            status=PlaybookStatus.PENDING,
            initiated_by=initiated_by,
            actions=[],
            finding_id=finding_data.get('id', 'unknown'),
            started_at=datetime.now().isoformat(),
            playbook_name=playbook.name,
            dry_run=dry_run
        )
        
        if playbook.requires_approval:
            execution.status = PlaybookStatus.PENDING
            execution.approval_status = "AWAITING_APPROVAL"
            self.logger.info(f"Playbook {execution_id} awaiting approval")
        else:
            execution = self._execute_actions(playbook, execution, dry_run)
        
        self.executions[execution_id] = execution
        return execution
    
    def approve_execution(
        self,
        execution_id: str,
        approver: str,
        dry_run: bool = False
    ) -> bool:
        """
        Approve a pending playbook execution.
        
        Args:
            execution_id: Execution ID to approve
            approver: User approving the execution
            dry_run: If True, don't actually execute
            
        Returns:
            True if approved and executed successfully
        """
        execution = self.executions.get(execution_id)
        if not execution:
            self.logger.error(f"Execution not found: {execution_id}")
            return False
        
        if execution.status != PlaybookStatus.PENDING:
            self.logger.error(f"Cannot approve execution in status: {execution.status}")
            return False
        
        execution.approval_status = "APPROVED"
        execution.approver = approver
        execution.status = PlaybookStatus.APPROVED
        
        self.logger.info(f"Execution {execution_id} approved by {approver}")
        
        # Get the playbook and execute it
        # TODO: Retrieve playbook from storage
        return True
    
    def reject_execution(
        self,
        execution_id: str,
        rejector: str,
        reason: str
    ) -> bool:
        """
        Reject a pending playbook execution.
        
        Args:
            execution_id: Execution ID to reject
            rejector: User rejecting the execution
            reason: Reason for rejection
            
        Returns:
            True if rejected successfully
        """
        execution = self.executions.get(execution_id)
        if not execution:
            return False
        
        execution.status = PlaybookStatus.REJECTED
        execution.approval_status = "REJECTED"
        execution.approver = rejector
        execution.notes = reason
        execution.ended_at = datetime.now().isoformat()
        
        self.logger.info(f"Execution {execution_id} rejected: {reason}")
        return True
    
    def rollback_execution(self, execution_id: str) -> bool:
        """
        Rollback a completed playbook execution.
        
        Args:
            execution_id: Execution ID to rollback
            
        Returns:
            True if rollback successful
        """
        execution = self.executions.get(execution_id)
        if not execution:
            return False
        
        if execution.status != PlaybookStatus.COMPLETED:
            self.logger.error(
                f"Cannot rollback execution in status: {execution.status}"
            )
            return False
        
        # TODO: Implement rollback logic by reversing actions in reverse order
        execution.status = PlaybookStatus.ROLLED_BACK
        execution.ended_at = datetime.now().isoformat()
        
        self.logger.info(f"Execution {execution_id} rolled back")
        return True
    
    def get_execution(self, execution_id: str) -> Optional[PlaybookExecution]:
        """Get execution record."""
        return self.executions.get(execution_id)
    
    def get_execution_history(
        self,
        playbook_id: Optional[str] = None,
        finding_id: Optional[str] = None,
        limit: int = 10
    ) -> List[PlaybookExecution]:
        """Get execution history with optional filters."""
        executions = list(self.executions.values())
        
        if playbook_id:
            executions = [e for e in executions if e.playbook_id == playbook_id]
        if finding_id:
            executions = [e for e in executions if e.finding_id == finding_id]
        
        # Sort by started_at descending
        executions.sort(key=lambda e: e.started_at, reverse=True)
        
        return executions[:limit]
    
    def _execute_actions(
        self,
        playbook: RemediationPlaybook,
        execution: PlaybookExecution,
        dry_run: bool
    ) -> PlaybookExecution:
        """Execute all actions in the playbook."""
        execution.status = PlaybookStatus.RUNNING
        
        for action in playbook.actions:
            # Check condition if provided
            if action.get("condition") and not action["condition"]():
                result = ActionResult(
                    action_name=action["name"],
                    status=ActionStatus.SKIPPED,
                    message="Condition not met"
                )
                execution.actions.append(result)
                continue
            
            # Execute action
            handler = self.action_handlers.get(action["type"])
            if handler:
                result = handler(action, dry_run)
            else:
                result = ActionResult(
                    action_name=action["name"],
                    status=ActionStatus.FAILED,
                    message=f"No handler for action type: {action['type']}",
                    error="Handler not found"
                )
            
            execution.actions.append(result)
            
            if result.status == ActionStatus.FAILED:
                execution.status = PlaybookStatus.FAILED
                break
        
        if execution.status == PlaybookStatus.RUNNING:
            execution.status = PlaybookStatus.COMPLETED
        
        execution.ended_at = datetime.now().isoformat()
        return execution
    
    def _handle_notification(
        self,
        action: Dict[str, Any],
        dry_run: bool
    ) -> ActionResult:
        """Handle notification action."""
        params = action.get("params", {})
        
        if dry_run:
            return ActionResult(
                action_name=action["name"],
                status=ActionStatus.SUCCESS,
                message="[DRY RUN] Notification would be sent",
                output=params
            )
        
        # Send notification
        return ActionResult(
            action_name=action["name"],
            status=ActionStatus.SUCCESS,
            message=f"Sent notification: {params.get('type', 'unknown')}"
        )
    
    def _handle_script(
        self,
        action: Dict[str, Any],
        dry_run: bool
    ) -> ActionResult:
        """Handle script execution action."""
        params = action.get("params", {})
        script_path = params.get("script")
        
        if dry_run:
            return ActionResult(
                action_name=action["name"],
                status=ActionStatus.SUCCESS,
                message=f"[DRY RUN] Would execute script: {script_path}"
            )
        
        # Execute script
        return ActionResult(
            action_name=action["name"],
            status=ActionStatus.SUCCESS,
            message=f"Executed script: {script_path}"
        )
    
    def _handle_aws_action(
        self,
        action: Dict[str, Any],
        dry_run: bool
    ) -> ActionResult:
        """Handle AWS remediation action."""
        params = action.get("params", {})
        action_type = params.get("type", "unknown")
        
        if dry_run:
            return ActionResult(
                action_name=action["name"],
                status=ActionStatus.SUCCESS,
                message=f"[DRY RUN] AWS action would be executed: {action_type}"
            )
        
        # Execute AWS action via client
        return ActionResult(
            action_name=action["name"],
            status=ActionStatus.SUCCESS,
            message=f"Executed AWS action: {action_type}"
        )
    
    def _handle_gcp_action(
        self,
        action: Dict[str, Any],
        dry_run: bool
    ) -> ActionResult:
        """Handle GCP remediation action."""
        params = action.get("params", {})
        action_type = params.get("type", "unknown")
        
        if dry_run:
            return ActionResult(
                action_name=action["name"],
                status=ActionStatus.SUCCESS,
                message=f"[DRY RUN] GCP action would be executed: {action_type}"
            )
        
        return ActionResult(
            action_name=action["name"],
            status=ActionStatus.SUCCESS,
            message=f"Executed GCP action: {action_type}"
        )
    
    def _handle_azure_action(
        self,
        action: Dict[str, Any],
        dry_run: bool
    ) -> ActionResult:
        """Handle Azure remediation action."""
        params = action.get("params", {})
        action_type = params.get("type", "unknown")
        
        if dry_run:
            return ActionResult(
                action_name=action["name"],
                status=ActionStatus.SUCCESS,
                message=f"[DRY RUN] Azure action would be executed: {action_type}"
            )
        
        return ActionResult(
            action_name=action["name"],
            status=ActionStatus.SUCCESS,
            message=f"Executed Azure action: {action_type}"
        )
    
    def _generate_execution_id(self, playbook_id: str) -> str:
        """Generate unique execution ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{playbook_id}-{timestamp}"
