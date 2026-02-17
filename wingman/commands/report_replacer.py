"""
Report field replacer command for Wingman.
"""

import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

try:
    from ..utils.salesforce_client import SalesforceClient
except ImportError:
    # Handle relative imports when running as standalone
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from wingman.utils.salesforce_client import SalesforceClient

console = Console()


def create_package_xml(package_file: str, reports: List[str]) -> None:
    """Create a package.xml file for the given reports."""
    console.print(f"[blue]Creating package.xml with {len(reports)} reports...[/blue]")
    
    # Create the XML structure
    package = ET.Element("Package")
    package.set("xmlns", "http://soap.sforce.com/2006/04/metadata")
    
    types = ET.SubElement(package, "types")
    
    for report in reports:
        member = ET.SubElement(types, "members")
        member.text = report
    
    name = ET.SubElement(types, "name")
    name.text = "Report"
    
    version = ET.SubElement(package, "version")
    version.text = "65.0"
    
    # Write to file
    tree = ET.ElementTree(package)
    ET.indent(tree, space="    ", level=0)
    tree.write(package_file, encoding="utf-8", xml_declaration=True)
    
    console.print(f"[green]✓ Created package.xml with {len(reports)} reports[/green]")


def create_deployment_structure() -> None:
    """Create the deployment directory structure."""
    console.print("[blue]Creating deployment directory structure...[/blue]")
    
    directories = [
        "report-migration/retrieve",
        "report-migration/deploy", 
        "report-migration/backup"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    console.print("[green]✓ Created deployment structure in report-migration[/green]")


def search_replace_in_reports(old_field: str, new_field: str, dry_run: bool = False, reports_path: Optional[str] = None) -> List[str]:
    """Search and replace field references in report files."""
    console.print(f"[blue]Searching for field '{old_field}' in reports...[/blue]")
    
    # Use provided reports path or default
    base_path = Path(reports_path) if reports_path else Path("force-app/main/default/reports")
    
    # Find all report files
    report_files = list(base_path.rglob("*.report-meta.xml"))
    
    if not report_files:
        console.print(f"[yellow]Warning: No report files found in {base_path}[/yellow]")
        return []
    
    console.print(f"[blue]Found {len(report_files)} report files to process[/blue]")
    
    updated_reports = []
    total_files = 0
    updated_files = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Processing report files", total=len(report_files))
        
        for report_file in report_files:
            total_files += 1
            progress.update(task, description=f"Processing {report_file.name}")
            
            try:
                # Check if file contains the old field
                with open(report_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if old_field in content:
                    console.print(f"[blue]Found field '{old_field}' in: {report_file.name}[/blue]")
                    
                    if not dry_run:
                        # Create backup directory structure
                        backup_path = report_file.relative_to(base_path)
                        backup_dir = Path("report-migration/backup") / backup_path.parent
                        backup_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Copy original file to backup
                        shutil.copy2(report_file, Path("report-migration/backup") / backup_path)
                        
                        # Replace the field in the original file
                        new_content = content.replace(old_field, new_field)
                        
                        with open(report_file, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        # Verify the replacement worked
                        if new_field in new_content:
                            console.print(f"[green]✓ Successfully replaced '{old_field}' with '{new_field}' in: {report_file.name}[/green]")
                        else:
                            console.print(f"[yellow]Warning: Replacement may have failed in: {report_file.name}[/yellow]")
                    else:
                        console.print(f"[yellow]DRY RUN: Would replace '{old_field}' with '{new_field}' in: {report_file.name}[/yellow]")
                    
                    # Get report identifier for tracking
                    relative_path = report_file.relative_to(base_path)
                    report_identifier = str(relative_path.with_suffix(''))
                    updated_reports.append(report_identifier)
                    updated_files += 1
                    
                    console.print(f"[green]Updated report: {report_identifier}[/green]")
            
            except Exception as e:
                console.print(f"[red]Error processing {report_file.name}: {e}[/red]")
            
            progress.advance(task)
    
    console.print(f"[blue]Processed {total_files} report files, updated {updated_files} files[/blue]")
    return updated_reports


def create_final_package_xml(final_package_file: str, updated_reports: List[str]) -> bool:
    """Create final package.xml with only updated reports."""
    if not updated_reports:
        console.print("[yellow]Warning: No reports were updated - not creating final package.xml[/yellow]")
        return False
    
    console.print(f"[blue]Creating final package.xml with {len(updated_reports)} updated reports...[/blue]")
    create_package_xml(final_package_file, updated_reports)
    console.print(f"[green]✓ Created final package.xml with {len(updated_reports)} updated reports[/green]")
    return True


def report_replacer(ctx, org_alias: Optional[str], old_field: str, new_field: str, 
                   batch_size: int, dry_run: bool, reports_path: Optional[str] = None) -> None:
    """Main report replacer function."""
    
    console.print(f"[blue]Starting report field replacement...[/blue]")
    if org_alias:
        console.print(f"[blue]Org alias: {org_alias}[/blue]")
    if reports_path:
        console.print(f"[blue]Reports path: {reports_path}[/blue]")
    console.print(f"[blue]Old field: {old_field}[/blue]")
    console.print(f"[blue]New field: {new_field}[/blue]")
    console.print(f"[blue]Batch size: {batch_size}[/blue]")
    if dry_run:
        console.print(f"[yellow]DRY RUN MODE: No changes will be made[/yellow]")
    
    # Create deployment structure
    create_deployment_structure()
    
    # If reports_path is provided, skip Salesforce retrieval and use existing reports
    if reports_path:
        console.print("[blue]Using existing reports from provided path (skipping Salesforce retrieval)...[/blue]")
        
        # Verify reports path exists
        reports_base = Path(reports_path)
        if not reports_base.exists():
            console.print(f"[red]Error: Reports path does not exist: {reports_path}[/red]")
            return
        
        # Search and replace field values directly
        console.print("[blue]Searching and replacing field values in reports...[/blue]")
        all_updated_reports = search_replace_in_reports(old_field, new_field, dry_run, reports_path)
        
        # Create final package.xml with all updated reports
        console.print("[blue]Creating final package.xml with all updated reports...[/blue]")
        final_package_file = "report-migration/deploy/package.xml"
        
        if create_final_package_xml(final_package_file, all_updated_reports):
            console.print(f"[green]✓ Completed processing all reports![/green]")
            console.print(f"[blue]Reports processed from: {reports_path}[/blue]")
            console.print(f"[blue]Original reports (backup) are in: report-migration/backup/[/blue]")
            console.print(f"[blue]Package files are in: report-migration/[/blue]")
            console.print(f"[blue]Total updated reports: {len(all_updated_reports)}[/blue]")
            
            # List updated reports
            if all_updated_reports:
                console.print("\n[blue]Updated reports:[/blue]")
                table = Table(show_header=True, header_style="bold blue")
                table.add_column("Report", style="cyan")
                
                for report in all_updated_reports:
                    table.add_row(report)
                
                console.print(table)
        else:
            console.print("[yellow]Warning: No reports were updated[/yellow]")
        
        console.print(f"[green]Report field replacement completed![/green]")
        console.print(f"[blue]Summary:[/blue]")
        console.print(f"[blue]  Reports updated: {len(all_updated_reports)}[/blue]")
        return
    
    # Original flow: Retrieve reports from Salesforce
    if not org_alias:
        console.print("[red]Error: Org alias is required when not using --reports-path[/red]")
        return
    
    # Initialize Salesforce client
    try:
        client = SalesforceClient(org_alias)
    except Exception as e:
        console.print(f"[red]Failed to initialize Salesforce client: {e}[/red]")
        return
    
    # Get all reports and folders
    console.print("[blue]Step 1: Querying all reports and folders from org...[/blue]")
    
    try:
        reports = client.get_reports()
        folders = client.get_folders()
    except Exception as e:
        console.print(f"[red]Failed to retrieve reports: {e}[/red]")
        return
    
    if not reports:
        console.print("[yellow]Warning: No reports found in the org[/yellow]")
        return
    
    console.print(f"[green]✓ Found {len(reports)} reports to process[/green]")
    
    # Create folder mapping
    folder_mapping = {}
    if folders:
        console.print("[blue]Creating folder mapping...[/blue]")
        for folder in folders:
            folder_name = folder.get('Name', '')
            folder_dev_name = folder.get('DeveloperName', '')
            if folder_name and folder_dev_name:
                folder_mapping[folder_name] = folder_dev_name
        console.print(f"[green]✓ Created mapping for {len(folder_mapping)} folders[/green]")
    
    # Build report identifiers with proper folder structure
    console.print(f"[blue]Processing {len(reports)} reports...[/blue]")
    all_reports = []
    
    for report in reports:
        developer_name = report.get('DeveloperName', '')
        folder_name = report.get('FolderName', '')
        
        if not developer_name:
            continue
        
        if folder_name == "Public Reports" or not folder_name: 
            report_identifier = f"unfiled$public/{developer_name}"
        else:
            folder_dev_name = folder_mapping.get(folder_name)
            if folder_dev_name:
                report_identifier = f"{folder_dev_name}/{developer_name}"
            else:
                # Fallback: replace spaces with underscores
                folder_identifier = folder_name.replace(' ', '_')
                report_identifier = f"{folder_identifier}/{developer_name}"
        
        all_reports.append(report_identifier)
    
    console.print(f"[green]✓ Processed all {len(reports)} reports[/green]")
    
    # Calculate number of packages needed
    packages_needed = (len(all_reports) + batch_size - 1) // batch_size
    console.print(f"[blue]Creating {packages_needed} package.xml file(s)[/blue]")
    
    # Process all reports in batches
    console.print(f"[blue]Processing all {len(all_reports)} reports in batches of {batch_size}...[/blue]")
    
    all_updated_reports = []
    
    for i in range(0, len(all_reports), batch_size):
        batch_num = (i // batch_size) + 1
        batch_reports = all_reports[i:i + batch_size]
        package_file = f"report-migration/retrieve/package_{batch_num}.xml"
        
        console.print(f"[blue]Processing batch {batch_num} of {packages_needed} ({len(batch_reports)} reports)...[/blue]")
        
        # Create package.xml for this batch
        create_package_xml(package_file, batch_reports)
        
        # Retrieve reports
        console.print(f"[blue]Step 3: Retrieving reports for batch {batch_num}...[/blue]")
        if client.retrieve_reports(package_file):
            console.print(f"[green]✓ Successfully retrieved reports for batch {batch_num}[/green]")
            
            # Search and replace field values
            console.print(f"[blue]Step 4-5: Searching and replacing field values in batch {batch_num}...[/blue]")
            batch_updated_reports = search_replace_in_reports(old_field, new_field, dry_run)
            
            # Add to overall updated reports
            all_updated_reports.extend(batch_updated_reports)
            
            console.print(f"[green]✓ Completed batch {batch_num}[/green]")
        else:
            console.print(f"[yellow]Warning: Failed to retrieve reports for batch {batch_num}[/yellow]")
    
    # Create final package.xml with all updated reports
    console.print("[blue]Step 6: Creating final package.xml with all updated reports...[/blue]")
    final_package_file = "report-migration/deploy/package.xml"
    
    if create_final_package_xml(final_package_file, all_updated_reports):
        console.print(f"[green]✓ Completed processing all reports![/green]")
        console.print(f"[blue]Retrieved reports are in: force-app/main/default/reports[/blue]")
        console.print(f"[blue]Original reports (backup) are in: report-migration/backup/[/blue]")
        console.print(f"[blue]Package files are in: report-migration/[/blue]")
        console.print(f"[blue]Total updated reports: {len(all_updated_reports)}[/blue]")
        
        # List updated reports
        if all_updated_reports:
            console.print("\n[blue]Updated reports:[/blue]")
            table = Table(show_header=True, header_style="bold blue")
            table.add_column("Report", style="cyan")
            
            for report in all_updated_reports:
                table.add_row(report)
            
            console.print(table)
    else:
        console.print("[yellow]Warning: No reports were updated[/yellow]")
    
    console.print(f"[green]Report field replacement completed![/green]")
    console.print(f"[blue]Summary:[/blue]")
    console.print(f"[blue]  Total reports found: {len(reports)}[/blue]")
    console.print(f"[blue]  Reports processed: {len(all_reports)}[/blue]")
    console.print(f"[blue]  Reports updated: {len(all_updated_reports)}[/blue]")
