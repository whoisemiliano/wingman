# Wingman - Quick Start Guide

**Your wingman for Salesforce—automate the boring admin tasks.**

Get up and running in 5 minutes and start saving hours on repetitive tasks!

## Prerequisites

**Only one requirement:**
- **Salesforce CLI (sf)** - for org authentication
- Access to a Salesforce org

**That's it!** No Python, no pip, no dependencies to manage.

## Installation

### Option 1: Quick Install (Recommended)

```bash
# One-line installation for any platform
curl -sSL https://raw.githubusercontent.com/whoisemiliano/wingman/master/install.sh | bash
```

### Option 2: Manual Install

```bash
# Install dependencies
pip install -r requirements.txt

# Install Wingman
pip install -e .
```

## Authentication

```bash
# Login to your Salesforce org
sf org login web

# List available orgs
sf org list
```

## Test Installation

```bash
# Run the test script
python test_installation.py

# Test CLI directly
wingman --help
```

## Basic Usage

### 1. Test Connection

```bash
wingman test-connection --org myorg
```

### 2. Extract Field Metadata

```bash
# Extract all fields from Account object
wingman extract-fields --org myorg --objects Account

# Extract specific fields
wingman extract-fields --org myorg --objects Account --specific-fields Name,Type,Phone

# Extract from multiple objects
wingman extract-fields --org myorg --objects Account,Contact,Opportunity
```

### 3. Replace Report Fields

```bash
# Preview changes (dry run)
wingman replace-fields --org myorg --old-field Account.OldField__c --new-field Account.NewField__c --dry-run

# Apply changes
wingman replace-fields --org myorg --old-field Account.OldField__c --new-field Account.NewField__c
```

## Common Workflows

### Field Migration

```bash
# 1. Extract current field metadata
wingman extract-fields --org myorg --objects Account --output-dir ./field-analysis

# 2. Preview field replacement
wingman replace-fields --org myorg --old-field Account.OldField__c --new-field Account.NewField__c --dry-run

# 3. Apply field replacement
wingman replace-fields --org myorg --old-field Account.OldField__c --new-field Account.NewField__c

# 4. Verify changes
wingman extract-fields --org myorg --objects Account --output-dir ./field-analysis-updated
```

### Large Org Processing

```bash
# Use smaller batch sizes for large orgs
wingman replace-fields --org myorg --old-field Account.OldField__c --new-field Account.NewField__c --batch-size 25
```

## Output Files

- **Field metadata**: `{ObjectName}_field_metadata.csv`
- **Retrieved reports**: `force-app/main/default/reports/`
- **Backup files**: `report-migration/backup/`
- **Package files**: `report-migration/retrieve/` and `report-migration/deploy/`

## Troubleshooting

### Common Issues

1. **"sf: command not found"**
   ```bash
   npm install -g @salesforce/cli
   ```

2. **"No orgs found"**
   ```bash
   sf org login web
   ```

3. **Permission errors**
   - Ensure your user has appropriate permissions
   - Check object and field access

4. **Large org performance**
   - Use smaller batch sizes
   - Run during off-peak hours
   - Use specific field lists

### Get Help

```bash
# General help
wingman --help

# Command-specific help
wingman extract-fields --help
wingman replace-fields --help

# Verbose output
wingman --verbose extract-fields --org myorg --objects Account
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out the [examples](README.md#examples) section
- Join our community for support and feature requests

Happy Salesforce automation! 🚀
