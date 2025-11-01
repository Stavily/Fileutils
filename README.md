# File Utils Plugin

A Stavily plugin for performing basic file and directory operations on Linux filesystems.

## Features

- **Create Files**: Create new files with optional content
- **Create Directories**: Create new directories (with parent directories if needed)
- **Move Files/Directories**: Move files or directories to new locations
- **Delete Files/Directories**: Delete files or directories recursively
- **Rename Files/Directories**: Rename files or directories

## Configuration

The plugin accepts lists of operations to perform:

- `operation`: List of operation types (`create_file`, `create_dir`, `move`, `delete`, `rename`)
- `destination`: List of target paths for the operations
- `source`: List of source paths (for `move` and `rename` operations)
- `content`: List of content strings (for `create_file` operations)

## Usage

### Command Line

```bash
# Run the plugin (uses default configuration)
python3 main.py
```

### Plugin Configuration

Configure operations in `plugin.yaml`:

```yaml
configuration:
  operation: ["create_file", "create_dir"]
  destination: ["/tmp/example.txt", "/tmp/new_directory"]
  content: ["Hello, World!"]
```

## Output Format

The plugin outputs JSON data with operation results:

```json
{
  "status": "success",
  "data": {
    "total_operations": 2,
    "successful_operations": 2,
    "failed_operations": 0,
    "results": [
      {
        "operation": "create_file",
        "destination": "/tmp/example.txt",
        "success": true
      },
      {
        "operation": "create_dir",
        "destination": "/tmp/new_directory",
        "success": true
      }
    ]
  }
}
```

## Requirements

- Python 3.8+
- Linux operating system
- Appropriate filesystem permissions for operations

## Installation

1. Place the plugin files in a directory
2. Ensure `main.py` is executable
3. Configure `plugin.yaml` with desired operations
4. Run the plugin using the Stavily framework

## Security Notes

- Requires appropriate filesystem permissions
- Operations are performed with the privileges of the running process
- Be careful with delete operations as they are irreversible
- Validate paths to prevent unintended operations

## Error Handling

The plugin includes comprehensive error handling:
- Individual operation failures don't stop the entire process
- Detailed error messages for each failed operation
- Logging of all operations and errors
- JSON output with status indication