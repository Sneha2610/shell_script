import os

def generate_rules_toml(ip_list, output_file="rules.toml"):
    """
    Generate a rules.toml file for a list of specific IP addresses.

    Args:
        ip_list (list): List of IP addresses to include in the rules.
        output_file (str): Path to save the generated rules.toml file.
    """
    # Escape dots in IP addresses and create the regex
    regex = r"\b(?:{})\b".format("|".join(ip.replace(".", r"\.") for ip in ip_list))

    # Define the TOML content
    toml_content = f"""
title = "Custom Gitleaks Rules"
description = "Custom rules to identify specific IP addresses."
version = 1

[[rules]]
id = "specific-ip-detection"
description = "Detects a predefined list of specific IP addresses"
regex = '''{regex}'''
tags = ["IP"]

[[rules.allowlist]]
# Optional: Exclude patterns if needed
regexes = []
"""

    # Write the TOML content to the file
    with open(output_file, "w") as f:
        f.write(toml_content.strip())
    
    print(f"rules.toml generated successfully at {os.path.abspath(output_file)}")

# Example usage
if __name__ == "__main__":
    # Replace with your list of IPs
    ip_list = [
        "192.168.1.1",
        "10.0.0.1",
        "203.0.113.5",
        "198.51.100.7"
    ]
    generate_rules_toml(ip_list)
