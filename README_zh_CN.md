# my-mcp-ssh
[![EN doc](https://img.shields.io/badge/document-English-blue.svg)](README.md)
[![CN doc](https://img.shields.io/badge/文档-中文版-blue.svg)](README_zh_CN.md)

这是一个基于 Model Context Protocol (MCP) 的 SSH 连接工具，允许大语言模型通过 MCP 协议安全地与远程服务器进行 SSH 连接和文件操作。

## 功能特性

- SSH 连接管理：连接到远程 SSH 服务器
- 命令执行：在远程服务器上执行命令
- 文件传输：上传和下载文件
- 会话管理：维护和关闭 SSH 会话

## 安装
### 依赖
- Python >= 3.12
- uv包管理器

```bash
# 下载项目代码
git clone https://github.com/ffpy/my-mcp-ssh.git

# 进入项目目录
cd my-mcp-ssh

# 安装依赖
uv sync
```

## 用法
### 在客户端中配置
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

### 环境变量

可通过环境变量配置 SSH 连接参数：

- `SSH_HOST`: SSH 服务器主机名或 IP 地址
- `SSH_PORT`: SSH 服务器端口
- `SSH_USERNAME`: SSH 用户名
- `SSH_PASSWORD`: SSH 密码（如果使用密码认证）
- `SSH_KEY_PATH`: SSH 私钥文件路径（如果使用密钥认证）
- `SSH_KEY_PASSPHRASE`: SSH 私钥密码（如果需要）

## 工具列表

### connect

连接到SSH服务器

**参数：**
- `host`: SSH服务器主机名或IP地址，默认使用`SSH_HOST`环境变量
- `port`: SSH服务器端口，默认使用`SSH_PORT`环境变量或`22`
- `username`: SSH用户名，默认使用`SSH_USERNAME`环境变量
- `password`: SSH密码，默认使用`SSH_PASSWORD`环境变量
- `key_path`: SSH私钥文件路径，默认使用`SSH_KEY_PATH`环境变量或`~/.ssh/id_rsa`
- `key_passphrase`: SSH私钥密码，默认使用`SSH_KEY_PASSPHRASE`环境变量

### disconnect

断开SSH连接

**参数：**
- `session_id`: 要断开连接的会话ID

### list_sessions

列出所有活动SSH会话

**参数：**
- 无

### execute

在SSH服务器上执行命令

**参数：**
- `session_id`: 会话ID
- `command`: 要执行的命令
- `stdin`: 提供给命令的输入字符串，默认为空
- `timeout`: 命令超时时间（秒），默认为60秒

### upload

上传文件到SSH服务器

**参数：**
- `session_id`: 会话ID
- `local_path`: 本地文件路径
- `remote_path`: 远程文件路径

### download

从SSH服务器下载文件

**参数：**
- `session_id`: 会话ID
- `remote_path`: 远程文件路径
- `local_path`: 本地文件路径

## 调试
执行 `./inspector.sh` 进行在线调试

## License
my-mcp-ssh is licensed under the Apache License, Version 2.0