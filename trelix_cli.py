#!/usr/bin/env python3
"""
Trelix Manager CLI - Command-line interface for scripting and automation.
Provides programmatic access to Trelix deployment management features.

Usage:
    trelix-cli --help
    trelix-cli deploy --platform mxone --file servers.xlsx --host localhost:5000
    trelix-cli metrics --host localhost:5000 --json
    trelix-cli precheck --platform mbg --ip 192.168.1.100 --username admin --password pass
    trelix-cli search --platform mxone --status installed --output json
"""

import argparse
import json
import sys
import os
import requests
from datetime import datetime
from typing import Optional, Dict, Any
import csv
from io import StringIO
import time


class TrelixClient:
    """Client for interacting with Trelix Manager API."""
    
    def __init__(self, host: str = "localhost:5000", token: Optional[str] = None, verify_ssl: bool = True):
        """Initialize Trelix client.
        
        Args:
            host: API host (e.g., 'localhost:5000' or 'https://trelix.example.com')
            token: Optional auth token
            verify_ssl: Whether to verify SSL certificates
        """
        if "://" not in host:
            host = f"http://{host}"
        self.base_url = host.rstrip("/")
        self.token = token
        self.verify_ssl = verify_ssl
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated API request."""
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.pop("headers", {})
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        try:
            resp = requests.request(method, url, headers=headers, verify=self.verify_ssl, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status_code": resp.status_code if hasattr(e, 'response') else None}
    
    def health(self) -> Dict[str, Any]:
        """Check API health."""
        return self._request("GET", "/health")
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate and get token."""
        result = self._request("POST", "/auth/login", json={"username": username, "password": password})
        if "token" in result:
            self.token = result["token"]
        return result
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get dashboard metrics."""
        return self._request("GET", "/api/dashboard/metrics")
    
    def get_performance_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get performance analytics."""
        return self._request("GET", "/api/analytics/performance", params={"days": days})
    
    def get_audit_logs(self, action_type: Optional[str] = None, user_id: Optional[int] = None, 
                      start_date: Optional[str] = None, end_date: Optional[str] = None,
                      limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get audit logs with optional filtering."""
        params = {"limit": limit, "offset": offset}
        if action_type:
            params["action_type"] = action_type
        if user_id:
            params["user_id"] = user_id
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._request("GET", "/api/audit-logs", params=params)
    
    def search_servers(self, platform: Optional[str] = None, ip: Optional[str] = None,
                      status: Optional[str] = None, credential_valid: Optional[bool] = None,
                      trelix_installed: Optional[bool] = None, days_since: Optional[int] = None,
                      limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Search servers with advanced filtering."""
        params = {"limit": limit, "offset": offset}
        if platform:
            params["platform"] = platform
        if ip:
            params["ip"] = ip
        if status:
            params["status"] = status
        if credential_valid is not None:
            params["credential_valid"] = str(credential_valid).lower()
        if trelix_installed is not None:
            params["trelix_installed"] = str(trelix_installed).lower()
        if days_since:
            params["days_since"] = days_since
        return self._request("GET", "/api/servers/search", params=params)
    
    def list_files(self, platform: str) -> Dict[str, Any]:
        """List deployment files for platform."""
        return self._request("GET", f"/list-files/{platform}")
    
    def precheck_existing(self, platform: str, filename: str) -> Dict[str, Any]:
        """Run precheck on servers from file."""
        return self._request("POST", f"/precheck-existing/{platform}", 
                           json={"filename": filename})
    
    def precheck_single(self, platform: str, ip: str, username: str, password: str, 
                       root_password: Optional[str] = None) -> Dict[str, Any]:
        """Run precheck on single server."""
        data = {
            "ip": ip,
            "admin_username": username,
            "admin_password": password,
        }
        if root_password:
            data["root_password"] = root_password
        return self._request("POST", f"/precheck-single/{platform}", json=data)
    
    def deploy_existing(self, platform: str, filename: str, target_ips: Optional[list] = None,
                       retry_count: int = 2) -> Dict[str, Any]:
        """Deploy to servers from file."""
        data = {"filename": filename, "retry_count": retry_count}
        if target_ips:
            data["target_ips"] = target_ips
        return self._request("POST", f"/use-existing/{platform}", json=data)
    
    def deploy_single(self, platform: str, ip: str, username: str, password: str,
                     root_password: Optional[str] = None, retry_count: int = 2) -> Dict[str, Any]:
        """Deploy to single server."""
        data = {
            "ip": ip,
            "admin_username": username,
            "admin_password": password,
            "retry_count": retry_count,
        }
        if root_password:
            data["root_password"] = root_password
        return self._request("POST", f"/use-single/{platform}", json=data)
    
    def stream_session(self, session_id: str) -> None:
        """Stream deployment session events (Server-Sent Events)."""
        url = f"{self.base_url}/stream/{session_id}"
        try:
            resp = requests.get(url, stream=True, verify=self.verify_ssl)
            for line in resp.iter_lines():
                if line:
                    print(line.decode('utf-8'))
        except requests.exceptions.RequestException as e:
            print(f"Error streaming session: {e}", file=sys.stderr)
    
    def export_run(self, session_id: str, format: str = "csv") -> Optional[bytes]:
        """Export deployment run results."""
        if format not in ("csv", "xlsx"):
            print(f"Invalid format: {format}. Must be 'csv' or 'xlsx'", file=sys.stderr)
            return None
        
        url = f"{self.base_url}/runs/{session_id}/export/{format}"
        try:
            resp = requests.get(url, verify=self.verify_ssl)
            resp.raise_for_status()
            return resp.content
        except requests.exceptions.RequestException as e:
            print(f"Error exporting run: {e}", file=sys.stderr)
            return None


def format_metrics_table(metrics: Dict[str, Any]) -> str:
    """Format metrics as pretty table."""
    lines = []
    
    overall = metrics.get("overall", {})
    lines.append("=== DASHBOARD METRICS ===")
    lines.append(f"Total Runs:           {overall.get('total_runs', 0)}")
    lines.append(f"Completed Runs:       {overall.get('completed_runs', 0)}")
    lines.append(f"Total Servers:        {overall.get('total_servers', 0)}")
    lines.append(f"Installed:            {overall.get('installed_servers', 0)}")
    lines.append(f"Failed:               {overall.get('failed_servers', 0)}")
    lines.append(f"Success Rate:         {metrics.get('success_rate_percent', 0)}%")
    lines.append(f"Avg Deployment Time:  {metrics.get('average_deployment_time_seconds', 0):.0f}s")
    
    status = metrics.get("status_breakdown", {})
    if status:
        lines.append("\nStatus Breakdown:")
        for st, count in status.items():
            lines.append(f"  {st}: {count}")
    
    platforms = metrics.get("platform_stats", [])
    if platforms:
        lines.append("\nPlatform Statistics:")
        for p in platforms:
            lines.append(f"  {p.get('platform', 'Unknown')}: {p.get('server_count', 0)} servers, "
                        f"{p.get('installed_count', 0)} installed")
    
    return "\n".join(lines)


def format_servers_table(servers: list) -> str:
    """Format servers as table."""
    if not servers:
        return "No servers found."
    
    lines = ["IP Address          Platform    Status      Installed  Credentials  Last Check"]
    lines.append("-" * 90)
    
    for s in servers:
        ip = str(s.get('ip_address', ''))[:18].ljust(18)
        platform = str(s.get('vm_type', ''))[:10].ljust(10)
        status = str(s.get('status', 'unknown'))[:11].ljust(11)
        installed = "Yes" if s.get('trelix_installed') else "No "
        installed = installed.ljust(10)
        creds = "Valid" if s.get('credential_valid') else "Invalid"
        creds = creds.ljust(12)
        checked = str(s.get('checked_at', ''))[:19]
        
        lines.append(f"{ip} {platform} {status} {installed} {creds} {checked}")
    
    return "\n".join(lines)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Trelix Manager CLI", formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
Examples:
  %(prog)s health --host localhost:5000
  %(prog)s metrics --host api.example.com:5000 --json
  %(prog)s search --platform mxone --status error --host localhost:5000
  %(prog)s deploy --platform mbg --file servers.xlsx
  %(prog)s precheck-single --platform mxone --ip 192.168.1.100 --username admin --password secret
  %(prog)s analytics --days 7 --host localhost:5000 --json
""")
    
    parser.add_argument("--host", default="localhost:5000", help="API host (default: localhost:5000)")
    parser.add_argument("--token", help="Authentication token")
    parser.add_argument("--username", help="Username for authentication")
    parser.add_argument("--password", help="Password for authentication")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--no-verify-ssl", action="store_true", help="Disable SSL verification")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Health check
    subparsers.add_parser("health", help="Check API health")
    
    # Metrics
    subparsers.add_parser("metrics", help="Get dashboard metrics")
    
    # Analytics
    analytics = subparsers.add_parser("analytics", help="Get performance analytics")
    analytics.add_argument("--days", type=int, default=30, help="Number of days to analyze")
    
    # Audit logs
    audit = subparsers.add_parser("audit-logs", help="List audit logs")
    audit.add_argument("--action", help="Filter by action type")
    audit.add_argument("--user-id", type=int, help="Filter by user ID")
    audit.add_argument("--start-date", help="Start date (ISO format)")
    audit.add_argument("--end-date", help="End date (ISO format)")
    audit.add_argument("--limit", type=int, default=100, help="Max results (default: 100)")
    
    # Search servers
    search = subparsers.add_parser("search", help="Search servers with advanced filtering")
    search.add_argument("--platform", help="Filter by platform")
    search.add_argument("--ip", help="Filter by IP address pattern")
    search.add_argument("--status", help="Filter by deployment status")
    search.add_argument("--installed", choices=["true", "false"], help="Filter by installation status")
    search.add_argument("--credentials-valid", choices=["true", "false"], help="Filter by credential validity")
    search.add_argument("--days-since", type=int, help="Filter by days since last deployment")
    search.add_argument("--limit", type=int, default=100, help="Max results")
    
    # Precheck
    precheck_single = subparsers.add_parser("precheck-single", help="Precheck single server")
    precheck_single.add_argument("--platform", required=True, help="Platform name")
    precheck_single.add_argument("--ip", required=True, help="Server IP address")
    precheck_single.add_argument("--username", required=True, help="Admin username")
    precheck_single.add_argument("--password", required=True, help="Admin password")
    precheck_single.add_argument("--root-password", help="Root password (for MxOne)")
    
    # Deploy
    deploy = subparsers.add_parser("deploy", help="Deploy to servers")
    deploy.add_argument("--platform", required=True, help="Platform name")
    deploy.add_argument("--file", help="Excel file with servers")
    deploy.add_argument("--ip", help="Single server IP")
    deploy.add_argument("--username", help="Username (for single server)")
    deploy.add_argument("--password", help="Password (for single server)")
    deploy.add_argument("--root-password", help="Root password (for single MxOne server)")
    deploy.add_argument("--retry", type=int, default=2, help="Retry count (default: 2)")
    deploy.add_argument("--stream", action="store_true", help="Stream deployment events")
    
    # Export
    export = subparsers.add_parser("export", help="Export deployment run")
    export.add_argument("--session-id", required=True, help="Session ID")
    export.add_argument("--format", choices=["csv", "xlsx"], default="csv", help="Export format")
    export.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize client
    client = TrelixClient(
        host=args.host,
        token=args.token,
        verify_ssl=not args.no_verify_ssl
    )
    
    # Authenticate if credentials provided
    if args.username and args.password:
        auth_result = client.login(args.username, args.password)
        if "error" in auth_result:
            print(f"Authentication failed: {auth_result['error']}", file=sys.stderr)
            return 1
        print(f"Authenticated as {auth_result.get('username')}", file=sys.stderr)
    
    # Execute command
    try:
        if args.command == "health":
            result = client.health()
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                status = result.get("status", "unknown")
                print(f"Status: {status}")
        
        elif args.command == "metrics":
            result = client.get_dashboard_metrics()
            if "error" in result:
                print(f"Error: {result['error']}", file=sys.stderr)
                return 1
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(format_metrics_table(result))
        
        elif args.command == "analytics":
            result = client.get_performance_analytics(args.days)
            if "error" in result:
                print(f"Error: {result['error']}", file=sys.stderr)
                return 1
            if args.json:
                print(json.dumps(result, indent=2, default=str))
            else:
                print(json.dumps(result, indent=2, default=str))
        
        elif args.command == "audit-logs":
            result = client.get_audit_logs(
                action_type=args.action if hasattr(args, 'action') else None,
                user_id=args.user_id if hasattr(args, 'user_id') else None,
                start_date=args.start_date if hasattr(args, 'start_date') else None,
                end_date=args.end_date if hasattr(args, 'end_date') else None,
                limit=args.limit if hasattr(args, 'limit') else 100
            )
            if "error" in result:
                print(f"Error: {result['error']}", file=sys.stderr)
                return 1
            if args.json:
                print(json.dumps(result, indent=2, default=str))
            else:
                logs = result.get("logs", [])
                for log in logs:
                    ts = log.get("created_at", "")
                    action = log.get("action_type", "")
                    resource = f"{log.get('resource_type', '')}/{log.get('resource_id', '')}"
                    print(f"{ts} | {action:20} | {resource}")
        
        elif args.command == "search":
            result = client.search_servers(
                platform=args.platform if hasattr(args, 'platform') else None,
                ip=args.ip if hasattr(args, 'ip') else None,
                status=args.status if hasattr(args, 'status') else None,
                trelix_installed=args.installed == "true" if hasattr(args, 'installed') else None,
                credential_valid=args.credentials_valid == "true" if hasattr(args, 'credentials_valid') else None,
                days_since=args.days_since if hasattr(args, 'days_since') else None,
                limit=args.limit if hasattr(args, 'limit') else 100
            )
            if "error" in result:
                print(f"Error: {result['error']}", file=sys.stderr)
                return 1
            if args.json:
                print(json.dumps(result, indent=2, default=str))
            else:
                servers = result.get("servers", [])
                print(format_servers_table(servers))
                print(f"\nFound {result.get('total', 0)} servers")
        
        elif args.command == "precheck-single":
            result = client.precheck_single(
                args.platform,
                args.ip,
                args.username,
                args.password,
                args.root_password if hasattr(args, 'root_password') else None
            )
            if "error" in result:
                print(f"Error: {result['error']}", file=sys.stderr)
                return 1
            if args.json:
                print(json.dumps(result, indent=2, default=str))
            else:
                status = result.get("precheck_details", [{}])[0].get("state", "unknown")
                reason = result.get("precheck_details", [{}])[0].get("reason", "")
                print(f"Status: {status}")
                print(f"Reason: {reason}")
        
        elif args.command == "deploy":
            if not args.file and not args.ip:
                print("Error: --file or --ip required", file=sys.stderr)
                return 1
            
            if args.file:
                result = client.deploy_existing(args.platform, args.file, retry_count=args.retry)
            else:
                result = client.deploy_single(
                    args.platform,
                    args.ip,
                    args.username,
                    args.password,
                    args.root_password if hasattr(args, 'root_password') else None,
                    retry_count=args.retry
                )
            
            if "error" in result:
                print(f"Error: {result['error']}", file=sys.stderr)
                return 1
            
            session_id = result.get("session_id")
            print(f"Deployment started. Session ID: {session_id}")
            
            if args.stream:
                print("Streaming events...")
                client.stream_session(session_id)
        
        elif args.command == "export":
            data = client.export_run(args.session_id, args.format)
            if data is None:
                return 1
            
            output_file = args.output or f"trelix_run_{args.session_id}.{args.format}"
            with open(output_file, "wb") as f:
                f.write(data)
            print(f"Exported to {output_file}")
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
