# Trelix Manager - New Features Documentation

## Overview

This document describes the new features added to Trelix Manager, including dashboard metrics, performance analytics, audit logging, advanced filtering, dark mode, and CLI tooling.

## Features

### 1. Dashboard with Real-Time Metrics

**Endpoint:** `GET /api/dashboard/metrics`

Get comprehensive dashboard metrics including:
- Total deployments and completed runs
- Device deployment status overview
- Success rates and failure counts
- Platform-specific statistics
- Average deployment time

**Example Usage:**
```bash
# Via CLI
trelix-cli metrics --host localhost:5000

# Via curl
curl http://localhost:5000/api/dashboard/metrics
```

**Response:**
```json
{
  "overall": {
    "total_runs": 42,
    "completed_runs": 40,
    "total_servers": 128,
    "installed_servers": 115,
    "failed_servers": 3
  },
  "success_rate_percent": 94.5,
  "status_breakdown": {
    "installed": 115,
    "warning": 8,
    "error": 5
  },
  "platform_stats": [
    {
      "platform": "mxone",
      "run_count": 10,
      "server_count": 45,
      "installed_count": 42
    }
  ],
  "average_deployment_time_seconds": 245.3,
  "period": "30 days"
}
```

### 2. Performance Analytics

**Endpoint:** `GET /api/analytics/performance?days=30`

Track and analyze deployment performance over time:
- Daily success trends
- Problematic devices identification
- Platform success rates comparison
- Credential validity statistics

**Example Usage:**
```bash
# Get 7-day analytics
trelix-cli analytics --days 7 --host localhost:5000 --json

# Via curl
curl "http://localhost:5000/api/analytics/performance?days=7"
```

**Response:**
```json
{
  "daily_trends": [
    {
      "date": "2024-06-12",
      "total": 25,
      "successful": 23,
      "failed": 2
    }
  ],
  "problematic_devices": [
    {
      "ip_address": "192.168.1.50",
      "total_attempts": 5,
      "failed_attempts": 3,
      "successful_attempts": 2,
      "last_attempt": "2024-06-12T14:30:00"
    }
  ],
  "platform_success_rates": [
    {
      "platform": "mxone",
      "total": 45,
      "successful": 42,
      "success_rate": 93.33
    }
  ],
  "credential_validity": {
    "true": 120,
    "false": 8,
    "null": 15
  }
}
```

### 3. Audit Log Viewer

**Endpoint:** `GET /api/audit-logs`

Browse and search audit logs with filtering by:
- Action type (deployment, precheck, login, etc.)
- User ID
- Date range
- Pagination support

**Query Parameters:**
- `action_type` - Filter by action type (wildcard)
- `user_id` - Filter by user ID
- `start_date` - Start date (ISO format)
- `end_date` - End date (ISO format)
- `limit` - Max results (default: 100)
- `offset` - Pagination offset

**Example Usage:**
```bash
# Get recent deployments
trelix-cli audit-logs --action deployment --host localhost:5000

# Get deployments in date range
trelix-cli audit-logs \
  --action deployment \
  --start-date 2024-06-01 \
  --end-date 2024-06-30 \
  --limit 50

# Via curl
curl "http://localhost:5000/api/audit-logs?action_type=deployment&limit=100"
```

**Response:**
```json
{
  "logs": [
    {
      "id": 1001,
      "user_id": 1,
      "action_type": "deployment_completed",
      "resource_type": "deployment_run",
      "resource_id": "session_123456",
      "details": "{\"platform\": \"mxone\", \"servers\": 10, \"success\": true}",
      "ip_address": "192.168.1.100",
      "created_at": "2024-06-12T14:30:00"
    }
  ],
  "total": 250,
  "limit": 100,
  "offset": 0
}
```

### 4. Advanced Server Search and Filtering

**Endpoint:** `GET /api/servers/search`

Search and filter servers by multiple criteria:
- IP address pattern matching
- Deployment status (installed, error, warning, pending)
- Platform type
- Credential validity
- Installation status
- Last deployment date

**Query Parameters:**
- `ip` - IP address pattern (wildcard)
- `platform` - Platform name (mxone, mbg, mivb, etc.)
- `status` - Status (installed, error, warning, pending)
- `credential_valid` - true/false
- `trelix_installed` - true/false
- `days_since` - Days since last deployment
- `limit` - Max results (default: 100)
- `offset` - Pagination offset

**Example Usage:**
```bash
# Find failed deployments on MxOne
trelix-cli search \
  --platform mxone \
  --status error \
  --host localhost:5000

# Find servers without valid credentials
trelix-cli search \
  --credentials-valid false \
  --host localhost:5000 \
  --json

# Find recently deployed servers
trelix-cli search \
  --installed true \
  --days-since 7 \
  --host localhost:5000

# Via curl
curl "http://localhost:5000/api/servers/search?platform=mxone&status=error&limit=50"
```

**Response:**
```json
{
  "servers": [
    {
      "id": 1,
      "ip_address": "192.168.1.50",
      "vm_type": "mxone",
      "putty_username": "admin",
      "credential_valid": true,
      "created_at": "2024-05-15T10:00:00",
      "last_credential_update": "2024-06-12T14:00:00",
      "trelix_installed": true,
      "trelix_version": "7.0.1",
      "status": "installed",
      "message": "Installation successful",
      "checked_at": "2024-06-12T14:00:00"
    }
  ],
  "total": 3,
  "limit": 100,
  "offset": 0
}
```

### 5. Dark Mode Support

Dark mode is automatically supported in the web UI:
- **Auto-detection**: Respects system color scheme preference
- **Manual toggle**: Theme selector available in UI
- **Persistence**: Selected theme is saved in browser localStorage
- **Fallback**: Defaults to light mode if not specified

The theme is controlled via the `data-theme` attribute on the HTML root element:
- `data-theme="light"` - Light mode
- `data-theme="dark"` - Dark mode

### 6. Command-Line Tool (CLI)

The `trelix-cli` tool provides programmatic access to Trelix Manager features for scripting, automation, and CI/CD integration.

**Installation in Docker:**
```bash
docker-compose up -d
docker exec trelix trelix-cli --help
```

**Local Installation:**
```bash
# Install in editable mode
pip install -e .

# Or run directly
python trelix_cli.py --help
```

**Available Commands:**

#### Health Check
```bash
trelix-cli health --host localhost:5000
```

#### Metrics
```bash
trelix-cli metrics --host localhost:5000 [--json]
```

#### Analytics
```bash
trelix-cli analytics --days 30 --host localhost:5000 [--json]
```

#### Audit Logs
```bash
trelix-cli audit-logs \
  --host localhost:5000 \
  [--action ACTION_TYPE] \
  [--user-id USER_ID] \
  [--start-date DATE] \
  [--end-date DATE] \
  [--limit LIMIT] \
  [--json]
```

#### Server Search
```bash
trelix-cli search \
  --host localhost:5000 \
  [--platform PLATFORM] \
  [--ip IP_PATTERN] \
  [--status STATUS] \
  [--installed true/false] \
  [--credentials-valid true/false] \
  [--days-since DAYS] \
  [--limit LIMIT] \
  [--json]
```

#### Precheck Single Server
```bash
trelix-cli precheck-single \
  --platform mxone \
  --ip 192.168.1.100 \
  --username admin \
  --password secret \
  [--root-password secret] \
  --host localhost:5000
```

#### Deploy
```bash
# Deploy to multiple servers from Excel file
trelix-cli deploy \
  --platform mxone \
  --file servers.xlsx \
  --host localhost:5000 \
  [--retry 2] \
  [--stream]

# Deploy to single server
trelix-cli deploy \
  --platform mxone \
  --ip 192.168.1.100 \
  --username admin \
  --password secret \
  --host localhost:5000 \
  [--stream]
```

#### Export Results
```bash
trelix-cli export \
  --session-id session_123456 \
  --format csv \
  --output results.csv \
  --host localhost:5000
```

#### Authentication
```bash
# Login and save token
trelix-cli health \
  --host localhost:5000 \
  --username admin \
  --password password

# Use saved token
trelix-cli metrics --host localhost:5000 --token TOKEN_VALUE
```

### Database Schema Extensions

Two new tables were added for metrics and audit tracking:

#### audit_logs Table
```sql
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES app_users(id),
    action_type VARCHAR(64) NOT NULL,
    resource_type VARCHAR(64),
    resource_id VARCHAR(255),
    details TEXT,
    ip_address INET,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### Enhanced deployment_results Table
Added `duration_seconds` column to track deployment timing for analytics.

### API Usage Examples

#### Get Dashboard Metrics (JavaScript)
```javascript
async function getMetrics() {
  const response = await fetch('http://localhost:5000/api/dashboard/metrics', {
    headers: {
      'Authorization': 'Bearer YOUR_TOKEN'
    }
  });
  const data = await response.json();
  console.log(data);
}
```

#### Search Servers (Python)
```python
import requests

client = requests.Session()
client.headers['Authorization'] = f'Bearer {token}'

response = client.get(
    'http://localhost:5000/api/servers/search',
    params={
        'platform': 'mxone',
        'status': 'error',
        'limit': 50
    }
)
servers = response.json()['servers']
```

#### Stream Deployment Events (JavaScript)
```javascript
const eventSource = new EventSource(`/stream/${sessionId}`);
eventSource.addEventListener('log', (e) => {
  console.log(e.data);
});
eventSource.addEventListener('done', (e) => {
  eventSource.close();
});
```

## Configuration

### Environment Variables

- `AUTH_ENABLED` - Enable/disable authentication (default: 0)
- `DATABASE_URL` - PostgreSQL connection string
- Additional configuration in `docker-compose.yml`

### UI Theme Preference

Users can:
1. Set system theme preference (auto-detected on first load)
2. Manually select theme from UI
3. Theme selection is stored in `localStorage` with key `trellix-theme`

## Performance Notes

- Dashboard metrics queries are optimized with indexes on `checked_at`, `status`, `run_id`
- Audit logs are indexed by `created_at` and `action_type` for fast filtering
- Server search supports pagination with `limit` and `offset`
- Analytics queries pre-aggregate data for efficient reporting

## Security Considerations

- Audit logs are immutable; only new entries can be added
- All API endpoints require authentication if `AUTH_ENABLED=1`
- Passwords are never returned in API responses
- Credential data is encrypted when stored at rest
- Audit log details are stored as JSON for structured querying

## Migration from Previous Versions

If upgrading from a version without these features:

1. **Database**: The new tables will be created automatically on first startup
2. **API**: New endpoints are available immediately
3. **UI**: Existing views continue to work; new views accessible via navigation
4. **CLI**: Install with `pip install -r requirements.txt` locally
5. **Docker**: Rebuild image: `docker-compose build --no-cache`

## Troubleshooting

### No metrics displayed
- Ensure database is enabled and accessible
- Check PostgreSQL connection string in `DATABASE_URL`
- Wait 5+ minutes for initial deployment data to accumulate

### Audit logs not appearing
- Verify `DATABASE_URL` is set correctly
- Check database user has INSERT permissions on `audit_logs` table
- Ensure PostgreSQL is running

### CLI tool not found in Docker
- Rebuild image: `docker-compose build --no-cache`
- Verify Dockerfile copies `trelix_cli.py`
- Check symlink: `docker exec trelix ls -la /usr/local/bin/trelix-cli`

### Dark mode not working
- Clear browser localStorage
- Check for JavaScript errors in console
- Ensure `data-theme` attribute is set on `<html>` element

## Future Enhancements

- Real-time streaming dashboard
- Custom alerting and notifications
- Report generation and scheduling
- Advanced filtering with saved search queries
- Performance baseline and anomaly detection
- Integration with monitoring systems (Prometheus, Grafana)
