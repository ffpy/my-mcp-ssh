# SSH MCP 服务器
# 基于 MCP 协议实现的 SSH 连接工具

import os
import paramiko
import uuid
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP
from session import Session, SessionManager

# 环境变量键名
ENV_SESSION_TIMEOUT = "SESSION_TIMEOUT"
ENV_SSH_HOST = "SSH_HOST"
ENV_SSH_PORT = "SSH_PORT"
ENV_SSH_USERNAME = "SSH_USERNAME"
ENV_SSH_PASSWORD = "SSH_PASSWORD"
ENV_SSH_KEY_PATH = "SSH_KEY_PATH"
ENV_SSH_KEY_PASSPHRASE = "SSH_KEY_PASSPHRASE"
ENV_MAX_OUTPUT_LENGTH = "MAX_OUTPUT_LENGTH"

# 常量字符串
SUCCESS = "success"
ERROR = "error"
SESSION_ID = "session_id"
SESSION_NOT_FOUND = "Session not found: {}"
DEFAULT_KEY_PATH = "~/.ssh/id_rsa"
MESSAGE = "message"
LOCAL_PATH = "local_path"
REMOTE_PATH = "remote_path"

# 创建 MCP 服务器
mcp = FastMCP("SSH连接服务器")

# 从环境变量获取会话超时时间（分钟），默认30分钟
SESSION_TIMEOUT = int(os.environ.get(ENV_SESSION_TIMEOUT, 30))

# 获取命令输出最大长度，默认5000个字符
MAX_OUTPUT_LENGTH = int(os.environ.get(ENV_MAX_OUTPUT_LENGTH, 5000))

# 创建会话管理器
session_manager = SessionManager(timeout_minutes=SESSION_TIMEOUT)


@mcp.tool()
def connect(
    host: str = "",
    port: int = 22,
    username: str = "",
    password: str = "",
    key_path: str = "",
    key_passphrase: str = "",
) -> Dict[str, Any]:
    """Connect to SSH server
    
    Args:
        session_id: Session ID, will be automatically generated if not provided
        host: SSH server hostname or IP address, defaults to SSH_HOST environment variable
        port: SSH server port, defaults to SSH_PORT environment variable or 22
        username: SSH username, defaults to SSH_USERNAME environment variable
        password: SSH password, defaults to SSH_PASSWORD environment variable
        key_path: SSH private key file path, defaults to SSH_KEY_PATH environment variable or ~/.ssh/id_rsa
        key_passphrase: SSH private key passphrase, defaults to SSH_KEY_PASSPHRASE environment variable
    
    Returns:
        Connection status
    """
    # 获取默认参数，并用提供的参数覆盖
    default_params = get_default_ssh_params()
    host = host or default_params["host"]
    port = port or default_params["port"]
    username = username or default_params["username"]
    password = password or default_params["password"]
    key_path = key_path or default_params["key_path"]
    key_passphrase = key_passphrase or default_params["key_passphrase"]
    
    # 如果密码和密钥都没提供，使用默认的id_rsa
    if not password and not key_path:
        default_key_path = os.path.expanduser(DEFAULT_KEY_PATH)
        if os.path.exists(default_key_path):
            key_path = default_key_path
    
    # 验证连接参数
    validation_result = validate_connection_params(host, username, password, key_path)
    if validation_result:
        return validation_result
    
    # 创建SSH客户端
    client_result = create_ssh_client(
        host, port, username, password, key_path, key_passphrase
    )
    
    if not client_result[SUCCESS]:
        return client_result
    
    # 创建会话对象
    session = Session(
        ssh_client=client_result["ssh_client"],
        id="",  # 临时ID，会被create_session方法替换
        sftp_client=None
    )
    
    # 创建会话并获取session_id
    session_id = session_manager.create_session(session)
    
    return {
        SUCCESS: True, 
        SESSION_ID: session_id
    }


@mcp.tool()
def disconnect(session_id: str) -> Dict[str, Any]:
    """Disconnect from SSH server
    
    Args:
        session_id: Session ID to disconnect
    
    Returns:
        Disconnection status
    """
    session = session_manager.get_session(session_id)
    
    if not session:
        return {SUCCESS: False, ERROR: SESSION_NOT_FOUND.format(session_id)}
    
    try:
        # 关闭并移除会话
        session.close()
        session_manager.remove_session(session_id)
        
        return {
            SUCCESS: True,
            SESSION_ID: session_id
        }
    except Exception as e:
        return {SUCCESS: False, ERROR: f"Error disconnecting: {str(e)}"}


@mcp.tool()
def list_sessions() -> List[Dict[str, str]]:
    """List all active SSH sessions
    
    Returns:
        List containing information about all sessions
    """
    return session_manager.list_sessions()


@mcp.tool()
def execute(session_id: str, command: str, stdin: str = "", timeout: int = 60) -> Dict[str, str]:
    """Execute command on SSH server
    
    Args:
        session_id: Session ID
        command: Command to execute
        stdin: Input string to provide to the command, defaults to None
        timeout: Command timeout in seconds, defaults to 60 seconds
    
    Returns:
        Command output (stdout and stderr) and exit status
    """
    session = session_manager.get_session(session_id)
    
    if not session:
        return {SUCCESS: False, ERROR: SESSION_NOT_FOUND.format(session_id)}
    
    try:
        session_manager.update_session_activity(session_id)
        stdin_obj, stdout, stderr = session.ssh_client.exec_command(command, timeout=timeout)
        
        # 如果提供了stdin数据，发送给命令
        if stdin:
            stdin_obj.write(stdin)
            stdin_obj.flush()
            stdin_obj.channel.shutdown_write()
            
        exit_status = stdout.channel.recv_exit_status()
        
        # 读取输出
        stdout_data = stdout.read().decode("utf-8")
        stderr_data = stderr.read().decode("utf-8")
        
        return {
            SUCCESS: True,
            "stdout": truncate_output(stdout_data),
            "stderr": truncate_output(stderr_data),
            "exit_status": exit_status
        }
    except Exception as e:
        return {SUCCESS: False, ERROR: f"Error executing command: {truncate_output(str(e))}"}


@mcp.tool()
def upload(session_id: str, local_path: str, remote_path: str) -> Dict[str, Any]:
    """Upload file to SSH server
    
    Args:
        session_id: Session ID
        local_path: Local file path
        remote_path: Remote file path
    
    Returns:
        Dictionary containing upload status information
    """
    session = session_manager.get_session(session_id)
    
    if not session:
        return {SUCCESS: False, ERROR: SESSION_NOT_FOUND.format(session_id)}
    
    try:
        session_manager.update_session_activity(session_id)
        
        # 如果sftp_client不存在，创建一个
        if not session.sftp_client:
            session.sftp_client = session.ssh_client.open_sftp()
            
        session.sftp_client.put(local_path, remote_path)
        return {
            SUCCESS: True,
            LOCAL_PATH: local_path,
            REMOTE_PATH: remote_path,
            SESSION_ID: session_id
        }
    except Exception as e:
        return {SUCCESS: False, ERROR: f"Error uploading file: {str(e)}"}


@mcp.tool()
def download(session_id: str, remote_path: str, local_path: str) -> Dict[str, Any]:
    """Download file from SSH server
    
    Args:
        session_id: Session ID
        remote_path: Remote file path
        local_path: Local file path
    
    Returns:
        Dictionary containing download status information
    """
    session = session_manager.get_session(session_id)
    
    if not session:
        return {SUCCESS: False, ERROR: SESSION_NOT_FOUND.format(session_id)}
    
    try:
        session_manager.update_session_activity(session_id)
        
        # 如果sftp_client不存在，创建一个
        if not session.sftp_client:
            session.sftp_client = session.ssh_client.open_sftp()
            
        session.sftp_client.get(remote_path, local_path)
        return {
            SUCCESS: True,
            REMOTE_PATH: remote_path,
            LOCAL_PATH: local_path,
            SESSION_ID: session_id
        }
    except Exception as e:
        return {SUCCESS: False, ERROR: f"Error downloading file: {str(e)}"}


def truncate_output(output: str) -> str:
    """截断输出字符串
    
    参数:
        output: 输出字符串
        
    返回:
        截断后的字符串
    """
    if len(output) <= MAX_OUTPUT_LENGTH:
        return output
    
    return output[:MAX_OUTPUT_LENGTH] + f"\n... Output truncated (exceeded {MAX_OUTPUT_LENGTH} characters) ..."


def get_default_ssh_params() -> Dict[str, Any]:
    """获取默认的SSH连接参数
    
    返回:
        包含默认SSH连接参数的字典
    """
    return {
        "host": os.environ.get(ENV_SSH_HOST),
        "port": int(os.environ.get(ENV_SSH_PORT, "22")),
        "username": os.environ.get(ENV_SSH_USERNAME),
        "password": os.environ.get(ENV_SSH_PASSWORD),
        "key_path": os.environ.get(ENV_SSH_KEY_PATH),
        "key_passphrase": os.environ.get(ENV_SSH_KEY_PASSPHRASE)
    }


def validate_connection_params(host: str, username: str, password: str, key_path: str) -> Dict[str, Any]:
    """验证SSH连接参数
    
    参数:
        host: 主机地址
        username: 用户名
        password: 密码
        key_path: 密钥路径
        
    返回:
        验证结果，成功返回None，失败返回错误信息
    """
    if not host:
        return {SUCCESS: False, ERROR: "Host address not provided"}
    
    if not username:
        return {SUCCESS: False, ERROR: "Username not provided"}
    
    # 如果密码和密钥都没提供，使用默认的id_rsa
    if not password and not key_path:
        default_key_path = os.path.expanduser(DEFAULT_KEY_PATH)
        if not os.path.exists(default_key_path):
            return {SUCCESS: False, ERROR: "No password or key path provided, and default key ~/.ssh/id_rsa does not exist"}
    
    return None


def create_ssh_client(host: str, port: int, username: str, 
                     password: Optional[str], key_path: Optional[str], 
                     key_passphrase: Optional[str]) -> Dict[str, Any]:
    """创建SSH客户端并连接
    
    参数:
        host: 主机地址
        port: 端口
        username: 用户名
        password: 密码
        key_path: 密钥路径
        key_passphrase: 密钥密码
        
    返回:
        包含SSH客户端的字典，或错误信息
    """
    try:
        # 创建SSH客户端
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # 使用密钥连接
        if key_path:
            key = paramiko.RSAKey.from_private_key_file(
                key_path, password=key_passphrase
            )
            ssh_client.connect(
                hostname=host,
                port=port,
                username=username,
                pkey=key
            )
        # 使用密码连接
        else:
            ssh_client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password
            )
        
        return {
            SUCCESS: True,
            "ssh_client": ssh_client
        }
    except Exception as e:
        return {SUCCESS: False, ERROR: f"Connection failed: {str(e)}"}


if __name__ == "__main__":
    print("my-mcp-ssh running...")
    mcp.run()
