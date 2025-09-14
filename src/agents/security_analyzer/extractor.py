# src/agents/security_analyzer/extractor.py
import os
import re
import json
from typing import Dict, List, Any, Optional, Tuple
import yaml

class ComplianceExtractor:
    """
    Extracts compliance configurations and policies from various sources
    for security analysis.
    """
    
    def __init__(self):
        """Initialize the compliance extractor."""
        # Define supported configuration formats
        self.format_detectors = {
            "json": lambda text: text.strip().startswith('{') and text.strip().endswith('}'),
            "yaml": lambda text: bool(re.match(r'^([^:]+:[^\n]+\n)+', text)),
            "terraform": lambda text: bool(re.search(r'resource\s+"[^"]+"', text)),
            "cloudformation": lambda text: bool(re.search(r'"?Resources"?\s*:', text)),
            "benchmark": lambda text: bool(re.search(r'(Benchmark|Control|Requirement|Policy)\s+\d+[\.:]', text)),
        }
    
    def extract_from_file(self, file_path: str) -> Tuple[str, str, Optional[str]]:
        """
        Extract configuration content from a file.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            Tuple of (content, format_type, error_message)
        """
        if not os.path.exists(file_path):
            return "", "", f"File not found: {file_path}"
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Detect format
            format_type = self.detect_format(content, file_path)
            return content, format_type, None
            
        except Exception as e:
            return "", "", f"Error reading file: {str(e)}"
    
    def extract_from_directory(self, dir_path: str, recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Extract configurations from all files in a directory.
        
        Args:
            dir_path: Path to the directory
            recursive: Whether to search subdirectories
            
        Returns:
            List of dicts with extraction results
        """
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            return [{"error": f"Directory not found: {dir_path}"}]
            
        results = []
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith(('.json', '.yaml', '.yml', '.tf', '.hcl', '.template')):
                    file_path = os.path.join(root, file)
                    content, format_type, error = self.extract_from_file(file_path)
                    
                    if error:
                        results.append({
                            "file_path": file_path,
                            "error": error
                        })
                    else:
                        results.append({
                            "file_path": file_path,
                            "content": content,
                            "format": format_type
                        })
            
            # Stop recursion if not requested
            if not recursive:
                break
                
        return results
    
    def extract_from_text(self, text: str) -> Tuple[str, str]:
        """
        Extract and normalize configuration from text input.
        
        Args:
            text: The text containing configuration
            
        Returns:
            Tuple of (normalized_content, format_type)
        """
        # Detect the format
        format_type = self.detect_format(text)
        
        # Normalize content based on format
        if format_type == "json":
            try:
                # Parse and re-serialize to normalize formatting
                parsed = json.loads(text)
                normalized = json.dumps(parsed, indent=2)
                return normalized, format_type
            except json.JSONDecodeError:
                # If parsing fails, return as-is
                return text, format_type
                
        elif format_type == "yaml":
            try:
                # Parse and re-serialize to normalize formatting
                parsed = yaml.safe_load(text)
                normalized = yaml.dump(parsed, default_flow_style=False)
                return normalized, format_type
            except Exception:
                # If parsing fails, return as-is
                return text, format_type
                
        # For other formats, return as-is
        return text, format_type
    
    def detect_format(self, content: str, file_path: str = "") -> str:
        """
        Detect the format of configuration content.
        
        Args:
            content: The configuration content
            file_path: Optional file path for extension-based detection
            
        Returns:
            Format type as string
        """
        # Try to detect by file extension first
        if file_path:
            if file_path.endswith('.json'):
                return "json"
            elif file_path.endswith(('.yaml', '.yml')):
                return "yaml"
            elif file_path.endswith(('.tf', '.hcl')):
                return "terraform"
            elif file_path.endswith('.template') and '"Resources"' in content:
                return "cloudformation"
        
        # Try to detect by content patterns
        for format_name, detector in self.format_detectors.items():
            if detector(content):
                return format_name
                
        # Default to unknown if can't determine
        return "unknown"
    
    def extract_policies_from_config(self, content: str, format_type: str) -> List[Dict[str, Any]]:
        """
        Extract security policies from configuration content.
        
        Args:
            content: The configuration content
            format_type: The format of the configuration
            
        Returns:
            List of extracted policies
        """
        policies = []
        
        if format_type == "json":
            try:
                data = json.loads(content)
                policies.extend(self._extract_policies_from_json(data))
            except json.JSONDecodeError:
                policies.append({"error": "Invalid JSON format"})
                
        elif format_type == "yaml":
            try:
                data = yaml.safe_load(content)
                policies.extend(self._extract_policies_from_json(data))
            except Exception as e:
                policies.append({"error": f"YAML parsing error: {str(e)}"})
                
        elif format_type == "terraform":
            policies.extend(self._extract_policies_from_terraform(content))
            
        elif format_type == "cloudformation":
            try:
                data = json.loads(content) if content.strip().startswith('{') else yaml.safe_load(content)
                policies.extend(self._extract_policies_from_cloudformation(data))
            except Exception:
                policies.append({"error": "Error parsing CloudFormation template"})
                
        return policies
    
    def _extract_policies_from_json(self, data: Any, path: str = "") -> List[Dict[str, Any]]:
        """
        Recursively extract security policies from JSON/YAML data.
        
        Args:
            data: The parsed JSON/YAML data
            path: Current path in the object structure
            
        Returns:
            List of extracted policies
        """
        policies = []
        
        if isinstance(data, dict):
            # Check if this looks like a policy
            if "Statement" in data and ("Effect" in data or any("Effect" in s for s in data["Statement"] if isinstance(s, dict))):
                policies.append({
                    "type": "iam_policy",
                    "path": path,
                    "content": data
                })
            elif "PolicyDocument" in data:
                policies.append({
                    "type": "policy_document",
                    "path": path,
                    "content": data["PolicyDocument"]
                })
            
            # Recursively process dict
            for key, value in data.items():
                new_path = f"{path}.{key}" if path else key
                policies.extend(self._extract_policies_from_json(value, new_path))
                
        elif isinstance(data, list):
            # Recursively process list
            for i, item in enumerate(data):
                new_path = f"{path}[{i}]"
                policies.extend(self._extract_policies_from_json(item, new_path))
                
        return policies
    
    def _extract_policies_from_terraform(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract security policies from Terraform configuration.
        
        Args:
            content: Terraform configuration content
            
        Returns:
            List of extracted policies
        """
        policies = []
        
        # Extract IAM policies
        iam_policy_blocks = re.finditer(
            r'resource\s+"aws_iam_policy"\s+"[^"]+"\s+{(.*?)\s*}', 
            content, 
            re.DOTALL
        )
        
        for match in iam_policy_blocks:
            policy_block = match.group(1)
            # Extract policy document
            policy_doc_match = re.search(r'policy\s+=\s+<<\s*EOF\s*(.*?)\s*EOF', policy_block, re.DOTALL)
            if policy_doc_match:
                try:
                    policy_json = policy_doc_match.group(1).strip()
                    policy_data = json.loads(policy_json)
                    policies.append({
                        "type": "terraform_iam_policy",
                        "content": policy_data
                    })
                except json.JSONDecodeError:
                    # If not valid JSON, store as text
                    policies.append({
                        "type": "terraform_iam_policy_text",
                        "content": policy_doc_match.group(1).strip()
                    })
        
        # Extract security groups
        sg_blocks = re.finditer(
            r'resource\s+"aws_security_group"\s+"[^"]+"\s+{(.*?)\s*}', 
            content, 
            re.DOTALL
        )
        
        for match in sg_blocks:
            sg_block = match.group(1)
            name_match = re.search(r'name\s+=\s+"([^"]+)"', sg_block)
            name = name_match.group(1) if name_match else "unnamed"
            
            # Extract ingress rules
            ingress_blocks = re.finditer(r'ingress\s+{(.*?)}', sg_block, re.DOTALL)
            ingress_rules = []
            
            for ingress_match in ingress_blocks:
                ingress_block = ingress_match.group(1)
                cidr_match = re.search(r'cidr_blocks\s+=\s+\[(.*?)\]', ingress_block, re.DOTALL)
                from_port_match = re.search(r'from_port\s+=\s+(\d+)', ingress_block)
                to_port_match = re.search(r'to_port\s+=\s+(\d+)', ingress_block)
                
                if cidr_match and from_port_match and to_port_match:
                    cidr_blocks = [b.strip(' "\'') for b in cidr_match.group(1).split(',')]
                    ingress_rules.append({
                        "from_port": int(from_port_match.group(1)),
                        "to_port": int(to_port_match.group(1)),
                        "cidr_blocks": cidr_blocks
                    })
            
            if ingress_rules:
                policies.append({
                    "type": "terraform_security_group",
                    "name": name,
                    "ingress_rules": ingress_rules
                })
        
        return policies
    
    def _extract_policies_from_cloudformation(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract security policies from CloudFormation template.
        
        Args:
            data: Parsed CloudFormation template
            
        Returns:
            List of extracted policies
        """
        policies = []
        
        # Check if Resources section exists
        if "Resources" not in data:
            return policies
            
        # Extract IAM policies
        for resource_id, resource in data["Resources"].items():
            if resource.get("Type") == "AWS::IAM::Policy" or resource.get("Type") == "AWS::IAM::ManagedPolicy":
                policy_doc = resource.get("Properties", {}).get("PolicyDocument")
                if policy_doc:
                    policies.append({
                        "type": "cloudformation_iam_policy",
                        "resource_id": resource_id,
                        "content": policy_doc
                    })
            
            # Extract security groups
            elif resource.get("Type") == "AWS::EC2::SecurityGroup":
                sg_props = resource.get("Properties", {})
                ingress_rules = sg_props.get("SecurityGroupIngress", [])
                
                if ingress_rules:
                    policies.append({
                        "type": "cloudformation_security_group",
                        "resource_id": resource_id,
                        "group_name": sg_props.get("GroupName", "unnamed"),
                        "ingress_rules": ingress_rules
                    })
                    
            # Extract role policies
            elif resource.get("Type") == "AWS::IAM::Role":
                role_props = resource.get("Properties", {})
                policy_docs = role_props.get("Policies", [])
                
                for policy in policy_docs:
                    if "PolicyDocument" in policy:
                        policies.append({
                            "type": "cloudformation_role_policy",
                            "resource_id": resource_id,
                            "policy_name": policy.get("PolicyName", "unnamed"),
                            "content": policy["PolicyDocument"]
                        })
        
        return policies
