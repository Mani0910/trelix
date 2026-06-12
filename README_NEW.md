# Trelix Manager

Trelix Manager is a comprehensive deployment and management solution for Trellix endpoint protection across multiple enterprise platforms.

## Features

### Core Deployment Capabilities
- **Multi-platform support**: MxOne, MivB, MbG, MIV5000, and Windows
- **Bulk deployment**: Deploy to hundreds of servers simultaneously
- **Smart precheck**: Validate credentials and detect existing installations
- **Flexible input**: Excel files, manual entry, or network sources
- **Secure credentials**: Encrypted password storage and management

### Monitoring & Analytics (NEW)
- **Real-time dashboard**: Live metrics on deployments, success rates, and device status
- **Performance analytics**: Track trends, identify problematic devices
- **Audit logging**: Complete audit trail of all actions and deployments
- **Advanced search**: Filter servers by status, platform, credentials, and date

### Dark Mode (NEW)
- Automatic detection of system preferences
- Manual theme toggle in UI
- Persistent theme selection

### CLI Tool (NEW)
- Scriptable command-line interface for automation
- Integration with CI/CD pipelines
- Programmatic access to all features
- Support for batch operations

## Quick Start

### Docker Deployment (Recommended)

```bash
# Clone the repository
git clone <repo-url>
cd trelix

# Build and start containers
docker-compose up -d

# Access the application
open http://localhost:5000

# Test CLI
docker exec trelix trelix-cli --help
```

### Local Development

```bash
# Install Python 3.11+
python --version

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py

# Run CLI
python trelix_cli.py --help
```

## API Endpoints

### Dashboard & Monitoring (NEW)

- `GET /api/dashboard/metrics` - Real-time KPIs and statistics
- `GET /api/analytics/performance?days=30` - Success trends and analysis
- `GET /api/audit-logs` - Audit log viewer with filtering
- `GET /api/servers/search` - Advanced server search

### Core Deployment

- `POST /precheck-existing/<platform>` - Validate servers from Excel
- `POST /use-existing/<platform>` - Deploy to servers from Excel
- `POST /precheck-single/<platform>` - Validate single server
- `POST /use-single/<platform>` - Deploy to single server
- `GET /stream/<session_id>` - Stream deployment events (SSE)

### Utilities

- `GET /health` - Health check
- `GET /ready` - Readiness check
- `GET /list-files/<platform>` - List available deployment files
- `GET /runs/<session_id>/export/<fmt>` - Export results (CSV/XLSX)

## CLI Usage Examples

```bash
# Check API health
trelix-cli health --host localhost:5000

# Get dashboard metrics
trelix-cli metrics --host localhost:5000 --json

# View performance analytics
trelix-cli analytics --days 7 --host localhost:5000

# Search servers with filters
trelix-cli search --platform mxone --status error --host localhost:5000

# Run precheck on single server
trelix-cli precheck-single \
  --platform mxone \
  --ip 192.168.1.100 \
  --username admin \
  --password secret

# Deploy to multiple servers
trelix-cli deploy \
  --platform mxone \
  --file servers.xlsx \
  --host localhost:5000 \
  --stream

# View audit logs
trelix-cli audit-logs \
  --action deployment \
  --limit 100 \
  --host localhost:5000

# Export results
trelix-cli export \
  --session-id session_123456 \
  --format csv \
  --output results.csv
```

## Configuration

### Environment Variables

```bash
# API Configuration
TRELLIX_BIND_HOST=0.0.0.0
TRELLIX_PORT=5000
TRELLIX_DEBUG=0

# Database (required for metrics/audit features)
DATABASE_URL=postgresql://user:password@localhost:5432/trelix
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trelix
DB_USER=trelix_user
DB_PASSWORD=trelix_password

# Authentication
AUTH_ENABLED=0  # Enable authentication
TOKEN_TTL_SECONDS=43200

# File Storage
ENABLE_RESULT_EXPORTS=1
SECURE_EXPORT_DIR=/secure_data

# SMB/Network Share
SMB_SERVER=10.211.34.118
SMB_SHARE=api
NETWORK_USER=Administrator
NETWORK_PASS=password

# Platform-specific
SHARE_DIR_MXONE=/upgrade_credentials/mxone
SHARE_DIR_MIVB=/trelix_credentails/mivb
SHARE_DIR_MBG=/trelix_credentails/mbg
SHARE_DIR_MIV5000=/upgrade_credentials/miv5000
SHARE_DIR_WINDOWS=/trelix_credentials/windows
```

### Docker Environment

All environment variables can be configured in `docker-compose.yml`:

```yaml
services:
  trelix:
    environment:
      - DATABASE_URL=postgresql://user:pass@trelixdb:5432/trelix
      - AUTH_ENABLED=0
      - ENABLE_RESULT_EXPORTS=1
```

## Database Setup

The application automatically creates required tables on startup:

```bash
# PostgreSQL required tables
- app_users
- deployment_runs
- server_inventory
- deployment_results
- audit_logs (NEW)
```

To initialize database:

```bash
docker-compose up -d trelixdb
docker exec trelixdb psql -U trelix_user -d trelix -f /docker-entrypoint-initdb.d/001_init.sql
```

## Architecture

### Components

- **Backend**: Flask REST API (Python)
- **Frontend**: HTML5 with vanilla JavaScript
- **Database**: PostgreSQL (optional, required for metrics)
- **Real-time**: Server-Sent Events (SSE) for live updates

### Supported Platforms

| Platform | Linux | Windows | Key Features |
|----------|-------|---------|--------------|
| MxOne    | ✓     | ✗       | Root password required |
| MivB     | ✓     | ✗       | Multi-version support |
| MbG      | ✓     | ✗       | Bulk deployment |
| MIV5000  | ✓     | ✗       | Legacy support |
| Windows  | ✗     | ✓       | WinRM-based deployment |

## Performance Considerations

- Deploy to multiple servers in parallel
- Supports batch processing of 100+ devices
- Optimized database queries for analytics
- Configurable retry logic for resilience

## Security

- **Encrypted credentials**: Passwords encrypted at rest
- **SSL/TLS support**: HTTPS ready
- **Authentication**: Optional token-based auth
- **Audit logging**: Complete action trail
- **Input validation**: SQL injection and XSS protection

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL connection
docker exec trelixdb pg_isready -U trelix_user

# View logs
docker logs trelixdb

# Reset database
docker exec trelixdb dropdb -U trelix_user trelix
```

### API Issues
```bash
# Check health endpoint
curl http://localhost:5000/health

# View application logs
docker logs trelix

# Restart service
docker-compose restart trelix
```

### CLI Issues
```bash
# Test API connectivity
trelix-cli health --host localhost:5000 --no-verify-ssl

# Enable debug output
trelix-cli --help

# Use explicit host
trelix-cli metrics --host http://localhost:5000
```

## Development

### Project Structure

```
trelix/
├── app.py                  # Main Flask application
├── trelix_cli.py          # CLI tool (NEW)
├── index.html             # Web UI
├── config.py              # Configuration
├── mxone_trelix.py        # MxOne platform module
├── mivb_trelix.py         # MivB platform module
├── mbg_trelix.py          # MbG platform module
├── miv5000_trelix.py      # MIV5000 platform module
├── db/
│   └── init/
│       └── 001_init.sql   # Database schema
├── Dockerfile             # Container configuration
├── docker-compose.yml     # Multi-container setup
├── requirements.txt       # Python dependencies
└── FEATURES_NEW.md        # Detailed feature documentation (NEW)
```

### Adding a New Platform

1. Create `new_platform_trelix.py` module
2. Implement connection logic
3. Register in `app.py` configuration
4. Add environment variables
5. Update documentation

## Contributing

Please follow these guidelines:
- Code style: PEP 8
- Testing: Include unit tests for new features
- Documentation: Update README and comments
- Security: Run security checks before PR

## License

[Your License Here]

## Support

For issues and feature requests:
- GitHub Issues: [Link]
- Email: [Support Email]
- Documentation: See [FEATURES_NEW.md](FEATURES_NEW.md) for detailed API documentation

## Changelog

### Version 2.0 (Latest)
- **NEW**: Dashboard with real-time metrics
- **NEW**: Performance analytics and trend analysis
- **NEW**: Audit logging system
- **NEW**: Advanced server search and filtering
- **NEW**: CLI tool for scripting and automation
- **NEW**: Dark mode support
- Enhanced database schema for analytics
- Optimized queries for better performance

### Version 1.0
- Initial multi-platform deployment support
- Excel file integration
- Manual server entry
- Network share integration
- Email notifications

## Roadmap

- [ ] Real-time streaming dashboard
- [ ] Custom alerting and notifications
- [ ] Integration with Prometheus/Grafana
- [ ] REST API complete OpenAPI documentation
- [ ] Mobile app support
- [ ] Advanced role-based access control
- [ ] Multi-tenancy support
