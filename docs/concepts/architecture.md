## Architecture Overview
- [REST API](https://codeboxapi.com/docs)
### Core Components
- [Github Repo](https://github.com/shroominic/codebox-api)
1. **Base Layer**
   - Abstract `BaseBox` class
   - Core execution interface
   - Session management
   - Resource handling
2. **Implementation Layer**
   - `LocalBox`: Local development environment
   - `DockerBox`: Containerized execution
   - `RemoteBox`: Cloud execution service
3. **API Layer**
   - REST API interface
   - Async/Sync operations
   - File management
   - Package handling
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
