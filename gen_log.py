import json
from datetime import datetime
from collections import defaultdict
import os

def generate_log_files(inventory_file: str, log_directory: str = "logs"):
    """
    Generate log files for booked servers from inventory JSON
    Checks for space issues and package conflicts
    Generates a consolidated error summary
    """
    # Load inventory data
    with open(inventory_file, 'r') as f:
        inventory = json.load(f)
    
    # Create log directory if it doesn't exist
    os.makedirs(log_directory, exist_ok=True)
    
    # Current date for log headers
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Thresholds for space checks (in MB)
    space_thresholds = {
        "/boot": 100,
        "/": 1000,
        "/var": 1000,
        "/tmp": 500
    }
    
    # Error tracking
    error_counts = {
        "total_servers": 0,
        "servers_with_errors": 0,
        "space_errors": defaultdict(int),
        "package_errors": 0,
        "servers_with_space_errors": 0,
        "servers_with_package_errors": 0
    }
    
    # Process each server in inventory
    for server in inventory:
        # Only process booked servers
        if not server.get("booked_date"):
            continue
        
        error_counts["total_servers"] += 1
        server_has_errors = False
        
        # Extract server info
        hostname = server["server"]
        os_version = f"Red Hat Enterprise Linux {server['config']['version']}"
        
        # Get flagged packages from inventory (if any)
        flagged_packages = []
        for pkg in server["packages"]:
            if any(bad_pkg in pkg for bad_pkg in [
                "glibc-1.14-153.el7_9.x86_64",     # Vulnerable glibc version
                "sudo-1.8.23-3.el7.x86_64"         # Vulnerable sudo version
            ]):
                flagged_packages.append(pkg)
        
        if flagged_packages:
            error_counts["package_errors"] += len(flagged_packages)
            error_counts["servers_with_package_errors"] += 1
            server_has_errors = True
        
        # Check for space issues
        space_issues = {}
        for partition, space in server["free_space"].items():
            if space < space_thresholds[partition]:
                space_issues[partition] = True
                error_counts["space_errors"][partition] += 1
                server_has_errors = True
        
        if space_issues:
            error_counts["servers_with_space_errors"] += 1
        
        if server_has_errors:
            error_counts["servers_with_errors"] += 1
        
        # Generate log content
        log_content = f"""########################################
# Linux Patch Log - RHEL 7, RHEL 8 & RHEL 9
# Date: {current_date}
# Hostname: {hostname}
# OS: {os_version}
########################################

=== [Stage 1: Pre-check Stage] ===
[INFO] 02:39:46 - Starting dry run pre-check on host: {hostname}
[INFO] 02:39:46 - Checking disk space on root and /var partitions...\n"""
        
        # Add space check results
        for partition, space in server["free_space"].items():
            status = "OK"
            if space < space_thresholds[partition]:
                status = f"Insufficient space (Available: {space}MB, Required: {space_thresholds[partition]}MB)"
                log_content += f"[ERROR] 02:39:46 - {partition} - {status}\n"
            else:
                log_content += f"[INFO] 02:39:46 - {partition} - Available: {space}MB, Required: {space_thresholds[partition]}MB - OK\n"
        
        # Add remaining checks
        log_content += """[INFO] 02:39:46 - Verifying system accessibility...
[INFO] 02:39:46 - SSH accessible
[INFO] 02:39:46 - Checking for locked YUM transactions...
[INFO] 02:39:46 - No active yum transactions found
[INFO] 02:39:46 - Verifying package repositories...
[INFO] 02:39:46 - Checking for package conflicts...\n"""
        
        # Add package conflict info if any
        if flagged_packages:
            for pkg in flagged_packages:
                log_content += f"[ERROR] 02:39:46 - Conflict with flagged package: {pkg}\n"
        
        # Add final status
        if server_has_errors:
            log_content += "[INFO] 02:39:46 - Pre-check dry run completed with Warnings or Errors\n"
        else:
            log_content += "[INFO] 02:39:46 - Pre-check dry run completed Successfully\n"
        
        # Write log file
        log_filename = f"{hostname}_precheck.log"
        log_path = os.path.join(log_directory, log_filename)
        
        with open(log_path, 'w') as log_file:
            log_file.write(log_content)
        
        print(f"Generated log file: {log_path}")
    
    # Generate consolidated error report
    summary_report = f"""########################################
# Consolidated Pre-Check Error Report
# Date: {current_date}
# Total Servers Checked: {error_counts['total_servers']}
########################################

=== Error Summary ===
[INFO] Servers with any errors: {error_counts['servers_with_errors']}/{error_counts['total_servers']}

=== Space Errors ===
[INFO] Servers with space issues: {error_counts['servers_with_space_errors']}
[INFO] /boot space errors: {error_counts['space_errors']['/boot']}
[INFO] / space errors: {error_counts['space_errors']['/']}
[INFO] /var space errors: {error_counts['space_errors']['/var']}
[INFO] /tmp space errors: {error_counts['space_errors']['/tmp']}

=== Package Errors ===
[INFO] Servers with package conflicts: {error_counts['servers_with_package_errors']}
[INFO] Total flagged packages found: {error_counts['package_errors']}

"""
    
    # Write summary report
    summary_path = os.path.join(log_directory, "00_precheck_summary.log")
    with open(summary_path, 'w') as summary_file:
        summary_file.write(summary_report)
    
    print(f"\nGenerated summary report: {summary_path}")
    print("\n=== Consolidated Error Counts ===")
    print(summary_report)

if __name__ == "__main__":
    # Example usage
    generate_log_files("server_inventory.json")