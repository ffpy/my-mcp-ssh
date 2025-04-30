# my-mcp-ssh
[![EN doc](https://img.shields.io/badge/document-English-blue.svg)](README.md)
[![CN doc](https://img.shields.io/badge/文档-中文版-blue.svg)](README_zh_CN.md)

A Model Context Protocol (MCP) based SSH connection tool that allows large language models to securely connect to remote servers via SSH and perform file operations through the MCP protocol.

## Features

- SSH Connection Management: Connect to remote SSH servers
- Command Execution: Execute commands on remote servers
- File Transfer: Upload and download files
- Session Management: Maintain and close SSH sessions

## Installation
### Dependencies
- Python >= 3.12
- uv package manager

```bash
# Clone the project
git clone https://github.com/ffpy/my-mcp-ssh.git

# Enter the project directory
cd my-mcp-ssh

# Install dependencies
uv sync
```

## Usage
### Configure in client
```json
{
  "mcpServers": {
    "my-mcp-ssh": {
      "command": "uv",
      "args": [
        "--directory",
        "<your_path>/my-mcp-ssh",
        "run",
        "src/main.py"
      ],
      "env": {}
    }
  }
}
```

### Environment Variables

SSH connection parameters can be configured through environment variables:

- `SSH_HOST`: SSH server hostname or IP address
- `SSH_PORT`: SSH server port
- `SSH_USERNAME`: SSH username
- `SSH_PASSWORD`: SSH password (if using password authentication)
- `SSH_KEY_PATH`: SSH private key file path (if using key authentication)
- `SSH_KEY_PASSPHRASE`: SSH private key passphrase (if needed)

## Tool List

### connect

Connect to an SSH server

**Parameters:**
- `host`: SSH server hostname or IP address, defaults to `SSH_HOST` environment variable
- `port`: SSH server port, defaults to `SSH_PORT` environment variable or `22`
- `username`: SSH username, defaults to `SSH_USERNAME` environment variable
- `password`: SSH password, defaults to `SSH_PASSWORD` environment variable
- `key_path`: SSH private key file path, defaults to `SSH_KEY_PATH` environment variable or `~/.ssh/id_rsa`
- `key_passphrase`: SSH private key passphrase, defaults to `SSH_KEY_PASSPHRASE` environment variable

### disconnect

Disconnect from an SSH session

**Parameters:**
- `session_id`: The session ID to disconnect

### list_sessions

List all active SSH sessions

**Parameters:**
- None

### execute

Execute a command on the SSH server

**Parameters:**
- `session_id`: Session ID
- `command`: Command to execute
- `stdin`: Input string to provide to the command, default is empty
- `timeout`: Command timeout in seconds, default is 60 seconds

### upload

Upload a file to the SSH server

**Parameters:**
- `session_id`: Session ID
- `local_path`: Local file path
- `remote_path`: Remote file path

### download

Download a file from the SSH server

**Parameters:**
- `session_id`: Session ID
- `remote_path`: Remote file path
- `local_path`: Local file path

## Debugging
Run `./inspector.sh` for online debugging

## License
my-mcp-ssh is licensed under the Apache License, Version 2.0 