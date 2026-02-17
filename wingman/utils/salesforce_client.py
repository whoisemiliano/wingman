"""
Salesforce client utilities for Wingman.
"""

import json
import subprocess
import sys
from typing import Dict, List, Optional, Any
from rich.console import Console

console = Console()


class SalesforceClient:
    """Salesforce client wrapper using the Salesforce CLI."""
    
    def __init__(self, org_alias: str):
        self.org_alias = org_alias
        self._check_sf_cli()
        self._validate_org()
    
    def _check_sf_cli(self) -> None:
        """Check if Salesforce CLI is installed and authenticated."""
        try:
            result = subprocess.run(['sf', 'org', 'list'], 
                                  capture_output=True, text=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            console.print("[red]Error: Salesforce CLI (sf) is not installed or not authenticated.[/red]")
            console.print("Please install it and run 'sf org login web' first.")
            sys.exit(1)
    
    def _validate_org(self) -> None:
        """Validate that the org alias exists."""
        try:
            result = subprocess.run(['sf', 'org', 'list', '--json'], 
                                  capture_output=True, text=True, check=True)
            orgs_data = json.loads(result.stdout)
            
            # Check all org sections
            all_orgs = []
            for section in ['other', 'sandboxes', 'nonScratchOrgs', 'devHubs', 'scratchOrgs']:
                if section in orgs_data.get('result', {}):
                    all_orgs.extend(orgs_data['result'][section])
            
            # Find the org
            org_found = any(org.get('alias') == self.org_alias for org in all_orgs)
            
            if not org_found:
                console.print(f"[red]Error: Org alias '{self.org_alias}' not found.[/red]")
                console.print("Available orgs:")
                subprocess.run(['sf', 'org', 'list'], check=True)
                sys.exit(1)
                
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            console.print(f"[red]Error validating org: {e}[/red]")
            sys.exit(1)
    
    def test_connection(self) -> bool:
        """Test connection to the Salesforce org."""
        try:
            result = subprocess.run(['sf', 'data', 'query', 
                                   '--query', 'SELECT Id FROM User LIMIT 1',
                                   '--target-org', self.org_alias,
                                   '--json'],
                                  capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def query(self, soql_query: str, use_tooling_api: bool = False) -> Dict[str, Any]:
        """Execute a SOQL query against the org."""
        cmd = ['sf', 'data', 'query', '--query', soql_query, '--target-org', self.org_alias, '--json']
        
        if use_tooling_api:
            cmd.append('--use-tooling-api')
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Query failed: {e}[/red]")
            if e.stderr:
                console.print(f"[red]Error details: {e.stderr}[/red]")
            raise
        except json.JSONDecodeError as e:
            console.print(f"[red]Invalid JSON response: {e}[/red]")
            raise
    
    def get_reports(self) -> List[Dict[str, Any]]:
        """Get all reports from the org."""
        soql_query = ("SELECT Id, Name, DeveloperName, FolderName, LastModifiedDate "
                     "FROM Report WHERE IsDeleted = false ORDER BY Name")
        
        result = self.query(soql_query)
        return result.get('result', {}).get('records', [])
    
    def get_folders(self) -> List[Dict[str, Any]]:
        """Get all folders from the org."""
        soql_query = "SELECT Id, Name, DeveloperName FROM Folder ORDER BY Name"
        
        try:
            result = self.query(soql_query)
            return result.get('result', {}).get('records', [])
        except Exception:
            console.print("[yellow]Warning: Could not retrieve folders, will use folder names as-is[/yellow]")
            return []
    
    def get_field_list(self, object_name: str) -> List[str]:
        """Get list of field names for an object."""
        soql_query = f"SELECT DeveloperName FROM FieldDefinition WHERE EntityDefinition.DeveloperName = '{object_name}'"
        
        result = self.query(soql_query)
        records = result.get('result', {}).get('records', [])
        return [record.get('DeveloperName') for record in records if record.get('DeveloperName')]
    
    def get_field_metadata(self, object_name: str, field_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed metadata for a specific field."""
        soql_query = (f"SELECT EntityDefinition.DeveloperName, FullName, NamespacePrefix, "
                     f"DeveloperName, MasterLabel, DataType, Description, Metadata "
                     f"FROM FieldDefinition WHERE EntityDefinition.DeveloperName = '{object_name}' "
                     f"AND DeveloperName = '{field_name}'")
        
        try:
            result = self.query(soql_query, use_tooling_api=True)
            records = result.get('result', {}).get('records', [])
            return records[0] if records else None
        except Exception:
            return None
    
    def retrieve_reports(self, package_file: str) -> bool:
        """Retrieve reports using a package.xml file."""
        try:
            result = subprocess.run(['sf', 'project', 'retrieve', 'start',
                                   '--manifest', package_file,
                                   '--target-org', self.org_alias,
                                   '--json'],
                                  capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to retrieve reports: {e}[/red]")
            if e.stderr:
                console.print(f"[red]Error details: {e.stderr}[/red]")
            return False
