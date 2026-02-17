"""
Field metadata extractor command for Wingman.
"""

import csv
import os
from typing import List, Optional, Dict, Any
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


def extract_formula(metadata_json: Dict[str, Any]) -> str:
    """Extract formula from metadata JSON."""
    if not metadata_json or not isinstance(metadata_json, dict):
        return ""
    
    return metadata_json.get('formula', '') or ""


def generate_csv(client: SalesforceClient, object_name: str, output_dir: str, 
                max_fields: int = 0, specific_fields: Optional[List[str]] = None) -> str:
    """Generate CSV file with field metadata for an object."""
    
    output_file = os.path.join(output_dir, f"{object_name}_field_metadata.csv")
    
    console.print(f"[blue]Generating CSV for object: {object_name}[/blue]")
    
    # Create CSV header
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Object', 'Full Name', 'Namespace', 'DeveloperName', 
                        'Label', 'Type', 'Description', 'Formula'])
    
    # Get field list
    if specific_fields:
        console.print(f"[blue]Using specific fields: {', '.join(specific_fields)}[/blue]")
        field_list = [f.strip() for f in specific_fields if f.strip()]
    else:
        field_list = client.get_field_list(object_name)
        if not field_list:
            console.print(f"[yellow]Warning: No fields found for object: {object_name}[/yellow]")
            return output_file
    
    # Apply field limit if specified
    if not specific_fields and max_fields > 0 and max_fields < len(field_list):
        field_list = field_list[:max_fields]
        console.print(f"[yellow]Limited processing to first {max_fields} fields for testing[/yellow]")
    
    total_fields = len(field_list)
    console.print(f"[blue]Found {total_fields} fields to process for {object_name}[/blue]")
    
    # Process fields with progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"Processing {object_name} fields", total=total_fields)
        
        field_count = 0
        for field_name in field_list:
            if not field_name or not field_name.strip():
                continue
                
            field_count += 1
            progress.update(task, description=f"Processing field {field_count}/{total_fields}: {field_name}")
            
            # Get field metadata
            metadata = client.get_field_metadata(object_name, field_name)
            
            if metadata:
                # Extract data from metadata
                object_dev_name = metadata.get('EntityDefinition', {}).get('DeveloperName', '')
                full_name = metadata.get('FullName', '')
                namespace = metadata.get('NamespacePrefix', '')
                dev_name = metadata.get('DeveloperName', '')
                label = metadata.get('MasterLabel', '')
                data_type = metadata.get('DataType', '')
                description = metadata.get('Description', '')
                metadata_json = metadata.get('Metadata', {})
                
                # Skip fields with empty metadata
                if not any([object_dev_name, full_name, dev_name]):
                    continue
                
                # Extract formula from metadata
                formula = extract_formula(metadata_json)
                
                # Write to CSV
                with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([
                        object_dev_name,
                        full_name,
                        namespace,
                        dev_name,
                        label,
                        data_type,
                        description,
                        formula
                    ])
            else:
                console.print(f"[yellow]Warning: Failed to get metadata for field: {field_name}[/yellow]")
            
            progress.advance(task)
    
    console.print(f"[green]✓ Generated {output_file} with {field_count} fields[/green]")
    return output_file


def field_extractor(ctx, org_alias: str, objects_input: str, max_fields: int, 
                   specific_fields: Optional[str], output_dir: str) -> None:
    """Main field extractor function."""
    
    console.print(f"[blue]Starting field metadata extraction...[/blue]")
    console.print(f"[blue]Org alias: {org_alias}[/blue]")
    console.print(f"[blue]Objects: {objects_input}[/blue]")
    if max_fields > 0:
        console.print(f"[blue]Field limit: {max_fields} per object[/blue]")
    if specific_fields:
        console.print(f"[blue]Specific fields: {specific_fields}[/blue]")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Parse objects
    objects = [obj.strip() for obj in objects_input.split(',') if obj.strip()]
    specific_fields_list = [f.strip() for f in specific_fields.split(',')] if specific_fields else None
    
    # Initialize Salesforce client
    try:
        client = SalesforceClient(org_alias)
    except Exception as e:
        console.print(f"[red]Failed to initialize Salesforce client: {e}[/red]")
        return
    
    # Process each object
    generated_files = []
    for object_name in objects:
        if not object_name:
            continue
            
        try:
            console.print(f"\n[blue]Processing object: {object_name}[/blue]")
            output_file = generate_csv(client, object_name, output_dir, max_fields, specific_fields_list)
            generated_files.append(output_file)
        except Exception as e:
            console.print(f"[red]Error processing object {object_name}: {e}[/red]")
            continue
    
    # Summary
    console.print(f"\n[green]Field metadata extraction completed![/green]")
    console.print(f"[blue]Generated CSV files:[/blue]")
    
    if generated_files:
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("File", style="cyan")
        table.add_column("Size", style="magenta")
        
        for file_path in generated_files:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                table.add_row(os.path.basename(file_path), f"{size:,} bytes")
        
        console.print(table)
    else:
        console.print("[yellow]No CSV files were generated[/yellow]")
