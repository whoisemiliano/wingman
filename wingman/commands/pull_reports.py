"""
Pull (retrieve) reports from Salesforce without modifying them.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table

try:
    from ..utils.salesforce_client import SalesforceClient
    from .report_replacer import create_package_xml, create_deployment_structure
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from wingman.utils.salesforce_client import SalesforceClient
    from wingman.commands.report_replacer import create_package_xml, create_deployment_structure

console = Console()


def pull_reports(
    ctx: Any,
    org_alias: str,
    name_contains: Optional[str] = None,
    batch_size: int = 100,
) -> None:
    """
    Retrieve report metadata from the org into force-app/main/default/reports.
    Optionally filter by report name or developer name containing a string.
    """
    console.print("[blue]Starting report retrieval (pull only, no field replacement)...[/blue]")
    console.print(f"[blue]Org alias: {org_alias}[/blue]")
    if name_contains:
        console.print(f"[blue]Name filter (contains): {name_contains}[/blue]")
    console.print(f"[blue]Batch size: {batch_size}[/blue]")

    create_deployment_structure()

    try:
        client = SalesforceClient(org_alias)
    except Exception as e:
        console.print(f"[red]Failed to initialize Salesforce client: {e}[/red]")
        return

    console.print("[blue]Querying reports and folders from org...[/blue]")
    try:
        reports = client.get_reports(name_contains=name_contains)
        folders = client.get_folders()
    except Exception as e:
        console.print(f"[red]Failed to retrieve report list: {e}[/red]")
        return

    if not reports:
        filter_msg = f" matching '{name_contains}'" if name_contains else ""
        console.print(f"[yellow]No reports found in the org{filter_msg}[/yellow]")
        return

    console.print(f"[green]✓ Found {len(reports)} reports to retrieve[/green]")

    folder_mapping: Dict[str, str] = {}
    if folders:
        for folder in folders:
            folder_name = folder.get("Name", "")
            folder_dev_name = folder.get("DeveloperName", "")
            if folder_name and folder_dev_name:
                folder_mapping[folder_name] = folder_dev_name

    all_report_ids: List[str] = []
    for report in reports:
        developer_name = report.get("DeveloperName", "")
        folder_name = report.get("FolderName", "")
        if not developer_name:
            continue
        if folder_name == "Public Reports" or not folder_name:
            report_identifier = f"unfiled$public/{developer_name}"
        else:
            folder_dev_name = folder_mapping.get(folder_name)
            if folder_dev_name:
                report_identifier = f"{folder_dev_name}/{developer_name}"
            else:
                folder_identifier = folder_name.replace(" ", "_")
                report_identifier = f"{folder_identifier}/{developer_name}"
        all_report_ids.append(report_identifier)

    packages_needed = (len(all_report_ids) + batch_size - 1) // batch_size
    console.print(f"[blue]Retrieving in {packages_needed} batch(es)...[/blue]")

    for i in range(0, len(all_report_ids), batch_size):
        batch_num = (i // batch_size) + 1
        batch_reports = all_report_ids[i : i + batch_size]
        package_file = f"report-migration/retrieve/package_{batch_num}.xml"
        console.print(f"[blue]Batch {batch_num}/{packages_needed}: retrieving {len(batch_reports)} reports...[/blue]")
        create_package_xml(package_file, batch_reports)
        if client.retrieve_reports(package_file):
            console.print(f"[green]✓ Batch {batch_num} retrieved[/green]")
        else:
            console.print(f"[yellow]Warning: Batch {batch_num} retrieve failed[/yellow]")

    console.print("[green]✓ Report pull completed[/green]")
    console.print("[blue]Reports are in: force-app/main/default/reports[/blue]")
    console.print(f"[blue]Total retrieved: {len(all_report_ids)} reports[/blue]")

    if all_report_ids:
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Report", style="cyan")
        for rid in all_report_ids[:50]:  # show first 50
            table.add_row(rid)
        if len(all_report_ids) > 50:
            table.add_row(f"... and {len(all_report_ids) - 50} more")
        console.print(table)
