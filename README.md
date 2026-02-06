# OpenClaw AI Agent

🤖 An intelligent AI agent that combines Discord bot capabilities, GitHub automation, and Docker-in-Docker (DinD) container building with vLLM integration.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 🤖 **Discord Bot Integration** - Slash commands and natural language interface
- 🔧 **GitHub Integration** - Read/write access to repositories, PR management, issue automation
- 🐳 **Docker-in-Docker** - Full container building and management capabilities
- 🧠 **vLLM Integration** - AI-powered assistance using your local vLLM server
- ⚙️ **Configuration Management** - YAML-based configuration with environment variable overrides
- 🧪 **Test-Driven Development** - Comprehensive test suite with pytest
- 📊 **Health Monitoring** - Built-in health checks and monitoring endpoints
- 🔒 **Security** - Proper token management and secure-by-default configuration

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- vLLM server running on localhost:8001 (or modify configuration)
- Discord bot token (see [Discord Developer Portal](https://discord.com/developers/applications))
- GitHub Personal Access Token (see [GitHub Settings > Developer settings](https://github.com/settings/tokens))

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/LePhanFF/MyOpenclawAgent.git
cd MyOpenclawAgent

# Copy environment template
cp .env.example .env

# Configure your tokens and settings
nano .env
```

### 2. Configure Environment

Edit `.env` file with your actual tokens:

```env
DISCORD_BOT_TOKEN=your_actual_discord_bot_token_here
GITHUB_TOKEN=ghp_your_actual_github_token_here
```

### 3. Run with Docker Compose

```bash
# Build and start all services
docker-compose up -d --build

# Monitor logs
docker-compose logs -f openclaw

# Check service status
docker-compose ps
```

### 4. Verify Installation

```bash
# Check health endpoint
curl http://localhost:8080/health

# Check detailed health
curl http://localhost:8080/health/detailed
```

## 📋 Available Discord Commands

Once your bot is online in Discord, you can use these commands:

- `/ping` - Check bot latency
- `/status` - View OpenClaw system status
- `/chat <message>` - Chat with the AI assistant
- `/build <dockerfile> <tag>` - Build Docker containers (coming soon)
- `/deploy <service> <image>` - Deploy applications (coming soon)
- `/github <action> <repo>` - Perform GitHub operations (coming soon)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenClaw AI Agent                        │
├─────────────────────────────────────────────────────────────┤
│  Discord Bot Layer                                        │
│  ├── Slash Commands (/build, /deploy, /status)            │
│  ├── Chat Interface (natural language)                     │
│  └── Notifications                                        │
├─────────────────────────────────────────────────────────────┤
│  LLM Integration Layer                                      │
│  ├── vLLM Client (port 8001)                           │
│  └── OpenAI-compatible API wrapper                       │
├─────────────────────────────────────────────────────────────┤
│  GitHub Integration Layer                                   │
│  ├── PyGithub API client                                 │
│  └── Repository management                               │
├─────────────────────────────────────────────────────────────┤
│  Docker-in-Docker Layer                                     │
│  ├── Container building                                  │
│  └── Image management                                    │
└─────────────────────────────────────────────────────────────┘
```

## ⚙️ Configuration

### Main Configuration (`config/config.yaml`)

```yaml
application:
  name: "OpenClaw AI Agent"
  version: "1.0.0"
  log_level: "INFO"

llm:
  base_url: "http://host.docker.internal:8001/v1"
  model_name: "/model"
  api_key: "sk-dummy"
  max_tokens: 4000
  temperature: 0.7

discord:
  bot:
    token: "${DISCORD_BOT_TOKEN}"
    command_prefix: "/"

github:
  api:
    token: "${GITHUB_TOKEN}"
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|-----------|
| `DISCORD_BOT_TOKEN` | Discord bot application token | ✅ |
| `GITHUB_TOKEN` | GitHub personal access token | ✅ |
| `OPENAI_BASE_URL` | vLLM server URL | ❌ (uses config) |
| `MODEL_NAME` | vLLM model name | ❌ (uses config) |
| `LOG_LEVEL` | Logging level | ❌ (INFO) |

## 🧪 Testing

### Running Tests

```bash
# Run all tests
docker-compose exec openclaw python -m pytest

# Run with coverage
docker-compose exec openclaw python -m pytest --cov=src --cov-report=term-missing

# Run specific test categories
docker-compose exec openclaw python -m pytest -m unit
docker-compose exec openclaw python -m pytest -m integration
```

### Test Categories

- **Unit Tests** - Test individual components in isolation
- **Integration Tests** - Test component interactions
- **vLLM Tests** - Test vLLM integration (requires vLLM server)
- **Discord Tests** - Test Discord functionality (requires bot token)

## 📊 Monitoring

### Health Endpoints

- `GET /health` - Simple health check
- `GET /health/detailed` - Comprehensive system status

### Metrics

OpenClaw provides built-in metrics for monitoring:

- Bot uptime and status
- vLLM response times
- GitHub API usage
- Docker operation counts

## 🔧 Development

### Local Development Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your tokens

# Run tests
pytest

# Start application
python -m src.core.main
```

### Code Style

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## 📁 Project Structure

```
MyOpenclawAgent/
├── src/
│   ├── core/                 # Core application logic
│   │   ├── main.py          # Main entry point
│   │   ├── config_manager.py # Configuration management
│   │   ├── llm_client.py    # vLLM integration
│   │   └── health.py        # Health check endpoints
│   ├── discord/             # Discord bot components
│   │   ├── bot.py          # Main bot logic
│   │   ├── commands/       # Slash command implementations
│   │   ├── chat/           # Natural language interface
│   │   └── notifications/  # Notification system
│   └── github/             # GitHub integration
├── config/                  # Configuration files
├── tests/                   # Test suite
├── scripts/                 # Utility scripts
├── volumes/                 # Persistent data
├── Dockerfile              # Container definition
├── docker-compose.yml      # Service orchestration
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔒 Security

### Token Management

- Store tokens in environment variables or `.env` file
- Never commit tokens to version control
- Use GitHub's fine-grained tokens with minimal permissions
- Regularly rotate tokens

### Docker Security

- Uses non-root user (`openclaw:1000`)
- Rootless Docker daemon for enhanced isolation
- Network isolation between services
- Read-only configuration mounts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📝 TODO / Roadmap

- [x] **Phase 1** ✅ Core foundation with vLLM integration
- [ ] **Phase 2** Discord slash commands (build, deploy, github)
- [ ] **Phase 3** GitHub automation (PR creation, issue management)
- [ ] **Phase 4** Docker operations (build, push, deploy)
- [ ] **Phase 5** Advanced features (file sharing, webhooks)
- [ ] **Phase 6** Performance optimization and scaling

## 🐛 Troubleshooting

### Common Issues

**vLLM Connection Failed**
```bash
# Check if vLLM is running
curl http://localhost:8001/v1/models

# Check configuration
docker-compose logs openclaw | grep vLLM
```

**Discord Bot Not Responding**
```bash
# Check bot token
echo $DISCORD_BOT_TOKEN

# Check Discord logs
docker-compose logs openclaw | grep Discord
```

**Docker Build Issues**
```bash
# Check Docker daemon
docker-compose logs dind

# Check certificates
docker-compose exec openclaw ls -la /certs/client
```

### Getting Help

- 📖 Check this README
- 🐛 [Open an Issue](https://github.com/LePhanFF/MyOpenclawAgent/issues)
- 💬 [Discussions](https://github.com/LePhanFF/MyOpenclawAgent/discussions)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [vLLM](https://github.com/vllm-project/vllm) - High-throughput LLM inference
- [Pycord](https://github.com/Pycord-Development/pycord) - Discord library
- [PyGithub](https://github.com/PyGithub/PyGithub) - GitHub API library
- [FastAPI](https://fastapi.tiangolo.com/) - Health check API

---

**Made with ❤️ by [LePhanFF](https://github.com/LePhanFF)**

If this project helps you, please give it a ⭐ on GitHub!