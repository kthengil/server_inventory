import os
import random

def update_logs_with_random_error(log_directory="logs", inject_count=20):
    error_lines = [
        "[ERROR] 02:39:46 - SSH key mismatch detected\n",
        "[ERROR] 02:39:46 - Unexpected YUM lock file found\n",
        "[ERROR] 02:39:46 - Inconsistent OS version across nodes\n",
        "[ERROR] 02:39:46 - Host unreachable during validation\n",
        "[ERROR] 02:39:46 - High CPU usage detected during check\n"
    ]

    # Get all log files in the directory
    all_log_files = [f for f in os.listdir(log_directory) if f.endswith(".log")]
    selected_files = random.sample(all_log_files, min(inject_count, len(all_log_files)))

    for filename in selected_files:
        file_path = os.path.join(log_directory, filename)
        with open(file_path, "r") as f:
            lines = f.readlines()
        
        if len(lines) < 2:
            continue

        last_line = lines[-1].strip()
        selected_error = random.choice(error_lines)

        if "completed Successfully" in last_line:
            lines[-1] = "[INFO] 02:39:46 - Pre-check dry run Completed with Errors\n"
            lines.insert(-1, selected_error)
        else:
            lines.insert(-1, selected_error)

        with open(file_path, "w") as f:
            f.writelines(lines)
        
        print(f"Injected error into: {file_path}")
if __name__ == "__main__":
    update_logs_with_random_error(log_directory="logs", inject_count=20)
