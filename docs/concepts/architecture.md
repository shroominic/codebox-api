# Architecture Overview

- [REST API](https://codeboxapi.com/docs)

## Core Components

- [Github Repo](https://github.com/shroominic/codebox-api)

1. **Base Layer**
   - Core `CodeBox` class
   - Code execution interface
   - File management interface
   - Helper methods

2. **Implementation Layer**
   - `LocalBox`: Local running sandbox
   - `RemoteBox`: REST API adapter for remote execution
   - `DockerBox`: Docker adapter for local parallel execution

3. **CodeBox API Service**
   - REST API interface
   - Fully isolated and scalable
   - File and session management
   - Custom factory support

## Why is Sandboxing Important?

Security is critical when deploying LLM Agents in production:

- 🛡️ **Malicious Code Protection**: Isolated and secure execution
- 🔐 **Injection Prevention**: Mitigation of prompt injection attacks
- 🏰 **System Isolation**: No host system access
- 📊 **Resource Control**: Memory and CPU limits

## How It Works

CodeBox uses a three-tier architecture:

1. **API Layer**
   - REST API for service interaction
   - API key authentication
   - Sync/Async operation support

2. **Container Layer**
   - Hardened Docker containers
   - Complete host system isolation
   - Automatic resource management

3. **Storage Layer**
   - Persistent file system
   - Dependency management
   - Package caching
