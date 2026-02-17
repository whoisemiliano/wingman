# Wingman

<img src="docs/wingman.png" alt="Wingman" width="280" />

Your wingman for Salesforce—automate the boring admin tasks.

A powerful CLI for Salesforce admins that automates the tedious, time-consuming work: field metadata extraction, bulk report updates, and more. Stop wasting hours on repetitive work and focus on what matters most.

## Your wingman for Salesforce

**Stop wasting time on repetitive tasks.** Wingman automates the operations that consume hours of consultant time:

- **⚡ Field Metadata Extraction**: Instantly extract field metadata from any Salesforce object to CSV
- **🔄 Bulk Report Updates**: Replace field references across hundreds of reports in minutes, not hours
- **📊 Batch Processing**: Handle large orgs efficiently with smart batching
- **🎨 Rich Interface**: Beautiful progress bars and colored output - no more guessing what's happening
- **👀 Dry Run Mode**: Preview changes before applying them - never break production again
- **🚀 Zero Setup**: Download and run - no Python, no dependencies, no headaches

## 🚀 Installation

### Prerequisites

**Only one requirement:**
- **Salesforce CLI (sf)** - for org authentication
  ```bash
  # Install Salesforce CLI
  npm install -g @salesforce/cli
  sf org login web
  ```

**That's it!** No Python, no pip, no dependencies to manage.

### Install Wingman

#### Option 1: One-Click Install (Recommended)

```bash
# Universal installer - works on any platform
curl -sSL https://raw.githubusercontent.com/whoisemiliano/wingman/master/install.sh | bash
```

#### Option 2: Download & Run

1. Go to [Releases](https://github.com/whoisemiliano/wingman/releases)
2. Download for your platform:
   - **macOS**: `wingman-macos.tar.gz`
   - **Linux**: `wingman-linux.tar.gz` 
   - **Windows**: `wingman-windows.zip`
3. Extract and run - **no Python required!**

#### Option 3: Developer Install

```bash
# Clone and install for development
git clone https://github.com/whoisemiliano/wingman.git
cd wingman
pip install -e .
```

### Verify Installation

```bash
wingman --version
wingman --help
```

## Usage

### Field Metadata Extraction

Extract field metadata from Salesforce objects and save to CSV files.

```bash
# Extract all fields from Account and Contact objects
wingman extract-fields --org myorg --objects Account,Contact

# Extract specific fields only
wingman extract-fields --org myorg --objects Account --specific-fields Name,Type,Phone

# Limit number of fields for testing
wingman extract-fields --org myorg --objects Account --max-fields 10

# Specify output directory
wingman extract-fields --org myorg --objects Account,Contact --output-dir ./exports
```

### Report Field Replacement

Replace field references in Salesforce reports.

```bash
# Replace field references in all reports
wingman replace-fields --org myorg --old-field Account.OldField__c --new-field Account.NewField__c

# Dry run to preview changes
wingman replace-fields --org myorg --old-field Account.OldField__c --new-field Account.NewField__c --dry-run

# Process reports in smaller batches
wingman replace-fields --org myorg --old-field Account.OldField__c --new-field Account.NewField__c --batch-size 50
```

### Test Connection

Test connection to a Salesforce org.

```bash
wingman test-connection --org myorg
```

### Global Options

- `--org, -o`: Salesforce org alias (can be set as default)
- `--verbose, -v`: Enable verbose output
- `--help`: Show help message
- `--version`: Show version information

## Configuration

### Setting Default Org

You can set a default org to avoid specifying `--org` every time:

```bash
wingman --org myorg extract-fields --objects Account
```

### Environment Variables

You can set environment variables for common options:

```bash
export WINGMAN_DEFAULT_ORG=myorg
wingman extract-fields --objects Account
```

## Output Files

### Field Extraction

- CSV files are created in the current directory (or specified output directory)
- File naming: `{ObjectName}_field_metadata.csv`
- Columns: Object, Full Name, Namespace, DeveloperName, Label, Type, Description, Formula

### Report Replacement

- **Retrieved reports**: `force-app/main/default/reports/`
- **Backup files**: `report-migration/backup/`
- **Package files**: `report-migration/retrieve/` and `report-migration/deploy/`

## Examples

### Complete Field Migration Workflow

```bash
# 1. Extract current field metadata
wingman extract-fields --org myorg --objects Account,Contact --output-dir ./field-analysis

# 2. Test connection
wingman test-connection --org myorg

# 3. Preview field replacement changes
wingman replace-fields --org myorg --old-field Account.OldField__c --new-field Account.NewField__c --dry-run

# 4. Apply field replacement changes
wingman replace-fields --org myorg --old-field Account.OldField__c --new-field Account.NewField__c

# 5. Verify changes by extracting updated metadata
wingman extract-fields --org myorg --objects Account --output-dir ./field-analysis-updated
```

### Batch Processing Large Orgs

```bash
# Process reports in smaller batches for large orgs
wingman replace-fields --org myorg --old-field Account.OldField__c --new-field Account.NewField__c --batch-size 25
```

## Troubleshooting

### Common Issues

1. **Salesforce CLI not found**
   ```bash
   # Install Salesforce CLI
   npm install -g @salesforce/cli
   ```

2. **Org not authenticated**
   ```bash
   # Login to your org
   sf org login web
   ```

3. **Permission errors**
   - Ensure your user has appropriate permissions to query reports and field metadata
   - Check that you have access to the objects you're trying to process

4. **Large org performance**
   - Use smaller batch sizes for report processing
   - Consider running during off-peak hours
   - Use specific field lists instead of extracting all fields

### Debug Mode

Enable verbose output for debugging:

```bash
wingman --verbose extract-fields --org myorg --objects Account
```

## Development

### Building a new release

Releases are built and published by **GitHub Actions** when you push a version tag.

**1. Bump version and create a release (recommended)**

From the repo root, on your default branch (e.g. `master`):

```bash
make release VERSION=0.1.0
```

This updates the version in `pyproject.toml`, `setup.py`, and `wingman/__init__.py`, commits, creates tag `v0.1.0`, and pushes both branch and tag. The [Build and Release](.github/workflows/build-and-release.yml) workflow then:

- Builds standalone executables for **macOS**, **Linux**, and **Windows**
- Creates a GitHub Release with `wingman-macos.tar.gz`, `wingman-linux.tar.gz`, `wingman-windows.zip`
- Publishes the release (no draft)

**2. Or create the tag yourself**

```bash
# Update version in pyproject.toml, setup.py, wingman/__init__.py then:
git add .
git commit -m "Bump version to 0.1.0"
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin master   # or your branch name
git push origin v0.1.0
```

**3. Manual workflow run (draft release)**

In GitHub: **Actions → Build and Release → Run workflow**. Choose a version (e.g. `v0.1.0`). The workflow builds for all platforms and creates a **draft** release; you can edit and publish it from the Releases page.

**4. Build only for your current platform (local)**

```bash
make build-standalone
```

Output is in `wingman-dist/` (single executable + docs for your OS only).

### Setting up Development Environment

```bash
# Clone repository
git clone <repository-url>
cd wingman

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements.txt
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black wingman/
flake8 wingman/
mypy wingman/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Create an issue in the repository
- Contact the Emi via hi@whosiemiliano.dev

## Changelog

### v0.1.0
- Initial release
- Field metadata extraction
- Report field replacement
- Rich CLI interface
- Batch processing support