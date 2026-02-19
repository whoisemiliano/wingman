#!/usr/bin/env python3
"""
Wingman CLI - Main entry point for the command-line interface.
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

try:
    from . import __version__
    from .commands.field_extractor import field_extractor
    from .commands.report_replacer import report_replacer
    from .commands.pull_reports import pull_reports
    from .utils.salesforce_client import SalesforceClient
except ImportError:
    # Handle relative imports when running as standalone
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from wingman import __version__
    from wingman.commands.field_extractor import field_extractor
    from wingman.commands.report_replacer import report_replacer
    from wingman.commands.pull_reports import pull_reports
    from wingman.utils.salesforce_client import SalesforceClient

console = Console()


def print_banner():
    """Print the Wingman banner."""
    banner_text = Text("Wingman", style="bold blue")
    version_text = Text(f"v{__version__}", style="dim")
    tagline_text = Text("Your wingman for Salesforce—automate the boring admin tasks", style="italic yellow")
    
    banner = Panel.fit(
        f"{banner_text}\n{version_text}\n{tagline_text}\n\nStop wasting time on repetitive tasks. Automate the tedious work.",
        border_style="blue",
        padding=(1, 2)
    )
    console.print(banner)


@click.group()
@click.version_option(version=__version__, prog_name="wingman")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--org', '-o', help='Default Salesforce org alias to use')
@click.pass_context
def main(ctx, verbose, org):
    """
    Wingman - Your wingman for Salesforce. Automate the boring admin tasks.
    
    Automate the tedious, time-consuming tasks that Salesforce consultants face daily:
    - Extract field metadata from any Salesforce object instantly
    - Replace field references across hundreds of reports in minutes
    - Handle large orgs efficiently with smart batching
    - Preview changes before applying them
    
    Stop wasting hours on repetitive work. Focus on what matters most.
    """
    # Ensure that ctx.obj exists and is a dict
    ctx.ensure_object(dict)
    
    # Store global options
    ctx.obj['verbose'] = verbose
    ctx.obj['org'] = org
    
    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")
    
    if org:
        console.print(f"[dim]Using default org: {org}[/dim]")


@main.command()
@click.option('--org', '-o', help='Salesforce org alias (overrides default)')
@click.option('--objects', '-obj', required=True, help='Comma-separated list of objects to extract fields from')
@click.option('--max-fields', '-m', type=int, default=0, help='Maximum number of fields per object (0 = all)')
@click.option('--specific-fields', '-f', help='Comma-separated list of specific fields to extract')
@click.option('--output-dir', '-d', default='.', help='Output directory for CSV files')
@click.pass_context
def extract_fields(ctx, org, objects, max_fields, specific_fields, output_dir):
    """
    Extract field metadata from Salesforce objects and save to CSV files.
    
    Examples:
    \b
    wingman extract-fields --org myorg --objects Account,Contact
    wingman extract-fields --org myorg --objects Account --max-fields 10
    wingman extract-fields --org myorg --objects Account --specific-fields Name,Type,Phone
    """
    # Use org from command line or fall back to context default
    target_org = org or ctx.obj.get('org')
    
    if not target_org:
        console.print("[red]Error: No org specified. Use --org or set a default with --org option.[/red]")
        raise click.Abort()
    
    field_extractor(ctx, target_org, objects, max_fields, specific_fields, output_dir)


@main.command()
@click.option('--org', '-o', help='Salesforce org alias (overrides default)')
@click.option('--old-field', required=True, help='Old field reference to replace (e.g., Account.OldField__c)')
@click.option('--new-field', required=True, help='New field reference (e.g., Account.NewField__c)')
@click.option('--batch-size', '-b', type=int, default=100, help='Number of reports to process per batch')
@click.option('--dry-run', is_flag=True, help='Show what would be changed without making changes')
@click.option('--reports-path', '-r', help='Path to existing report files (skips retrieval from Salesforce)')
@click.pass_context
def replace_fields(ctx, org, old_field, new_field, batch_size, dry_run, reports_path):
    """
    Replace field references in Salesforce reports.
    
    This command will:
    1. Query all reports from the specified org (unless --reports-path is provided)
    2. Retrieve report metadata files (unless --reports-path is provided)
    3. Search and replace field references
    4. Create deployment packages for the changes
    
    Examples:
    \b
    wingman replace-fields --org myorg --old-field Account.OldField__c --new-field Account.NewField__c
    wingman replace-fields --org myorg --old-field Contact.OldField__c --new-field Contact.NewField__c --dry-run
    wingman replace-fields --old-field Account.OldField__c --new-field Account.NewField__c --reports-path ./force-app/main/default/reports
    """
    # If reports-path is provided, org is optional
    if not reports_path:
        # Use org from command line or fall back to context default
        target_org = org or ctx.obj.get('org')
        
        if not target_org:
            console.print("[red]Error: No org specified. Use --org or set a default with --org option.[/red]")
            raise click.Abort()
    else:
        target_org = org or ctx.obj.get('org')  # Optional when using reports-path
    
    report_replacer(ctx, target_org, old_field, new_field, batch_size, dry_run, reports_path)


@main.command()
@click.option('--org', '-o', help='Salesforce org alias (overrides default)')
@click.option('--name-contains', '-n', help='Only pull reports whose name or developer name contains this text (case-insensitive)')
@click.option('--batch-size', '-b', type=int, default=100, help='Number of reports to retrieve per batch')
@click.pass_context
def pull_reports_cmd(ctx, org, name_contains, batch_size):
    """
    Pull (retrieve) report metadata from the org without modifying anything.

    Reports are written to force-app/main/default/reports. Use --name-contains
    to limit to reports whose name or developer name contains the given text
    (e.g. "test" to get only test reports).

    Examples:
    \b
    wingman pull-reports --org myorg
    wingman pull-reports --org myorg --name-contains test
    wingman pull-reports --org myorg -n "Sales" --batch-size 50
    """
    target_org = org or ctx.obj.get('org')
    if not target_org:
        console.print("[red]Error: No org specified. Use --org or set a default with --org option.[/red]")
        raise click.Abort()
    pull_reports(ctx, target_org, name_contains, batch_size)


@main.command()
@click.option('--org', '-o', help='Salesforce org alias to test connection')
@click.pass_context
def test_connection(ctx, org):
    """
    Test connection to a Salesforce org.
    
    Examples:
    \b
    wingman test-connection --org myorg
    """
    target_org = org or ctx.obj.get('org')
    
    if not target_org:
        console.print("[red]Error: No org specified. Use --org or set a default with --org option.[/red]")
        raise click.Abort()
    
    try:
        client = SalesforceClient(target_org)
        if client.test_connection():
            console.print(f"[green]✓ Successfully connected to org: {target_org}[/green]")
        else:
            console.print(f"[red]✗ Failed to connect to org: {target_org}[/red]")
            raise click.Abort()
    except Exception as e:
        console.print(f"[red]✗ Connection failed: {str(e)}[/red]")
        raise click.Abort()


if __name__ == '__main__':
    print_banner()
    main()
