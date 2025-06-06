import json
import random
from typing import List, Dict, Any
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

def generate_applications(total_apps: int) -> List[Dict[str, str]]:
    """Generate a list of applications with fake data"""
    apps = []
    for i in range(1, total_apps + 1):
        app_name = fake.catch_phrase().replace(' ', '_')
        manager_name = fake.name()
        email = f"{manager_name.split()[0].lower()}.{manager_name.split()[-1].lower()}@example.com"
        
        apps.append({
            "app_id": f"APP-{i:04d}",
            "app_name": app_name,
            "app_manager": manager_name,
            "app_email": email
        })
    return apps

def generate_server_name(country: str, env: str, model: str) -> str:
    """Generate a unique server name based on given parameters"""
    model_code = {'HP': 'H', 'Dell': 'D', 'VMware': 'V'}[model]
    random_num = f"{random.randint(0, 99999999):08d}"
    return f"{country}{env}{model_code}{random_num}"

def get_packages_for_version(os_version: str) -> List[str]:
    """Generate sample packages based on RHEL version"""
    base_packages = [
        "kernel", "systemd", "glibc", "openssl", "bash", "python", "perl",
        "vim", "curl", "wget", "tar", "gzip", "make", "gcc", "openssh",
        "sudo", "rsync", "cronie", "logrotate", "yum", "rpm", "firewalld",
        "selinux", "nano", "htop", "iotop", "net-tools", "bind-utils",
        "tcpdump", "lsof", "strace", "sysstat", "dmidecode", "pciutils",
        "usbutils", "man-db", "less", "which", "file", "findutils"
    ]
    
    version_suffix = {
        "7": ".el7.x86_64",
        "8": ".el8.x86_64",
        "9": ".el9.x86_64"
    }[os_version]
    
    packages = []
    for pkg in base_packages:
        # Generate random version numbers
        if pkg == "kernel":
            version = f"3.10.0-{random.randint(1000, 2000)}"
        elif pkg == "systemd":
            version = f"219-{random.randint(70, 100)}"
        elif pkg == "glibc":
            version = f"2.{random.randint(10, 30)}-{random.randint(100, 200)}"
        else:
            version = f"{random.randint(1, 3)}.{random.randint(0, 20)}-{random.randint(1, 100)}"
        
        packages.append(f"{pkg}-{version}{version_suffix}")
    
    return packages

def generate_booked_dates(inventory_size: int, 
                         campaign_start: str, 
                         campaign_end: str, 
                         booked_servers: int) -> List[str]:
    """Generate booked dates with max 50 servers per hour"""
    start = datetime.strptime(campaign_start, "%d-%m-%Y")
    end = datetime.strptime(campaign_end, "%d-%m-%Y")
    
    # Calculate total hours in campaign
    total_hours = int((end - start).total_seconds() / 3600) + 1
    
    # Distribute booked servers across hours (max 50 per hour)
    hours_needed = (booked_servers // 50) + (1 if booked_servers % 50 else 0)
    servers_per_hour = [50] * (booked_servers // 50)
    if booked_servers % 50:
        servers_per_hour.append(booked_servers % 50)
    
    # Select random hours for booking (ensuring we don't exceed total hours)
    selected_hours = random.sample(range(total_hours), hours_needed)
    
    # Generate all booked dates
    booked_dates = []
    for i, hour_idx in enumerate(selected_hours):
        current_hour = start + timedelta(hours=hour_idx)
        for _ in range(servers_per_hour[i]):
            # Add random minutes to spread within the hour
            booked_time = current_hour + timedelta(minutes=random.randint(0, 59))
            booked_dates.append(booked_time.strftime("%d-%m-%Y %H:00"))
    
    # Pad with None for non-booked servers
    booked_dates += [None] * (inventory_size - booked_servers)
    random.shuffle(booked_dates)
    return booked_dates

def generate_server_entry(applications: List[Dict[str, str]], booked_date: str = None) -> Dict[str, Any]:
    """Generate a single server entry with random data"""
    country = random.choice(["US", "UK", "IN"])
    env = random.choice(["PRD", "DEV", "STG"])
    model = random.choice(["HP", "Dell", "VMware"])
    os_version = random.choice(["7", "8", "9"])
    
    # Select a random application for this server
    app_info = random.choice(applications)
    
    server_entry = {
        "server": generate_server_name(country, env, model),
        "config": {
            "model": model,
            "os": "RHEL",
            "version": os_version
        },
        "packages": get_packages_for_version(os_version),
        "free_space": {
            "/boot": random.randint(150, 250),
            "/": random.randint(2500, 8000),
            "/var": random.randint(2500, 20000),
            "/tmp": random.randint(1500, 3000)
        },
        "app_info": {
            "app_id": app_info["app_id"],
            "app_name": app_info["app_name"],
            "app_manager": app_info["app_manager"],
            "app_email": app_info["app_email"]
        }
    }
    
    if booked_date:
        server_entry["booked_date"] = booked_date
    
    return server_entry

def introduce_errors(inventory: List[Dict[str, Any]], error_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Introduce errors into the inventory based on the error specification"""
    flagged_packages = error_spec["package"]["flagged_list"]
    package_error_count = error_spec["package"]["count"]
    space_error_count = error_spec["space"]["count"]
    
    # Make a deep copy of the inventory to modify
    import copy
    inventory = copy.deepcopy(inventory)
    
    print(f"[DEBUG] Introducing {space_error_count} space errors and {package_error_count} package errors")
    
    # Select random servers for space errors
    if space_error_count > 0:
        space_error_servers = random.sample(inventory, min(space_error_count, len(inventory)))
        print(f"[DEBUG] Selected {len(space_error_servers)} servers for space errors")
        
        for i, server in enumerate(space_error_servers):
            print(f"[DEBUG] Processing space error for server {i+1}: {server['server']}")
            
            # Randomly choose which mount points to affect (1-4 mount points)
            mount_points = ["/boot", "/", "/var", "/tmp"]
            num_affected = random.randint(1, 4)
            affected_mounts = random.sample(mount_points, num_affected)
            
            print(f"[DEBUG] Affecting mount points: {affected_mounts}")
            
            for mount_point in affected_mounts:
                if mount_point == "/boot":
                    server["free_space"][mount_point] = error_spec["space"]["boot"]
                elif mount_point == "/":
                    server["free_space"][mount_point] = error_spec["space"]["root"]
                elif mount_point == "/var":
                    server["free_space"][mount_point] = error_spec["space"]["var"]
                elif mount_point == "/tmp":
                    server["free_space"][mount_point] = error_spec["space"]["tmp"]
            
            print(f"[DEBUG] Updated free_space: {server['free_space']}")
    
    # Select random servers for package errors (may overlap with space errors)
    if package_error_count > 0:
        package_error_servers = random.sample(inventory, min(package_error_count, len(inventory)))
        print(f"[DEBUG] Selected {len(package_error_servers)} servers for package errors")
        
        for i, server in enumerate(package_error_servers):
            print(f"[DEBUG] Processing package error for server {i+1}: {server['server']}")
            
            bad_package = random.choice(flagged_packages)
            print(f"[DEBUG] Selected flagged package: {bad_package}")
            
            # Get the base package name (e.g., "glibc" from "glibc-1.12-136.el7_9.x86_64")
            package_base = bad_package.split('-')[0]
            
            # Try to find and replace existing package with same base name
            replaced = False
            for j, existing_pkg in enumerate(server["packages"]):
                if existing_pkg.startswith(package_base + '-'):
                    print(f"[DEBUG] Replacing existing package {existing_pkg} with {bad_package}")
                    server["packages"][j] = bad_package
                    replaced = True
                    break
            
            if not replaced:
                # Replace a random package if no matching base package found
                idx = random.randint(0, len(server["packages"]) - 1)
                old_package = server["packages"][idx]
                server["packages"][idx] = bad_package
                print(f"[DEBUG] Replaced random package {old_package} with {bad_package}")
    
    return inventory

def generate_inventory(inventory_size: int, 
                     total_apps: int, 
                     booked_servers: int,
                     campaign_start: str,
                     campaign_end: str,
                     error_spec: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Generate server inventory with optional errors"""
    # First generate all applications
    applications = generate_applications(total_apps)
    
    # Generate booked dates
    booked_dates = generate_booked_dates(inventory_size, campaign_start, campaign_end, booked_servers)
    
    # Then generate servers, each assigned to one of the applications
    inventory = [generate_server_entry(applications, booked_date) 
                for booked_date in booked_dates]
    
    if error_spec:
        inventory = introduce_errors(inventory, error_spec)
    
    return inventory

# Example usage
if __name__ == "__main__":
    # Define the error specification with realistic low space thresholds
    error_specification = {
        "space": {
            "count": 30,
            "boot": 50,     # Very low /boot space (< 100MB is critical)
            "root": 800,    # Low root space (< 1GB is concerning)
            "var": 900,     # Low /var space (< 1GB is concerning for logs)
            "tmp": 400      # Low temp space (< 500MB can cause issues)
        },
        "package": {
            "flagged_list": [
                "glibc-1.14-153.el7_9.x86_64",     # Vulnerable glibc version
                "sudo-1.8.23-3.el7.x86_64"         # Vulnerable sudo version
            ],
            "count": 45
        }
    }
    
    # Campaign dates (DD-MM-YYYY format)
    campaign_start = "01-01-2023"
    campaign_end = "31-01-2023"
    
    # Generate inventory
    print("Generating inventory...")
    inventory = generate_inventory(
        inventory_size=350,
        total_apps=30,
        booked_servers=200,
        campaign_start=campaign_start,
        campaign_end=campaign_end,
        error_spec=error_specification
    )
    
    # Save to JSON file
    with open("server_inventory.json", "w") as f:
        json.dump(inventory, f, indent=2)
    
    print("Inventory generated and saved to server_inventory.json")
    
    # Analysis for verification
    print("\n=== Analysis ===")
    space_errors = {"boot": 0, "root": 0, "var": 0, "tmp": 0}
    package_errors = 0
    flagged_packages = error_specification["package"]["flagged_list"]
    
    for server in inventory:
        # Check space errors
        if server["free_space"]["/boot"] <= 100:  # Boot space critical threshold
            space_errors["boot"] += 1
        if server["free_space"]["/"] <= 1000:  # Root space critical threshold
            space_errors["root"] += 1
        if server["free_space"]["/var"] <= 1000:  # Var space critical threshold
            space_errors["var"] += 1
        if server["free_space"]["/tmp"] <= 500:  # Tmp space critical threshold
            space_errors["tmp"] += 1
        
        # Check package errors
        for package in server["packages"]:
            if package in flagged_packages:
                package_errors += 1
                break
    
    print(f"Space errors - /boot: {space_errors['boot']}, /: {space_errors['root']}, /var: {space_errors['var']}, /tmp: {space_errors['tmp']}")
    print(f"Servers with flagged packages: {package_errors}")
    print(f"Expected space errors: {error_specification['space']['count']}")
    print(f"Expected package errors: {error_specification['package']['count']}")