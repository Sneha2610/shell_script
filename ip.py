import toml

def generate_rules_toml(ip_list, output_file):
    """
    Generate a Gitleaks-compatible rules.toml file for a list of IPs.

    Args:
        ip_list (list): List of IPs to include in the rules.
        output_file (str): Path to save the generated rules.toml file.
    """
    # Combine all IPs into a single regex pattern
    combined_regex = "|".join(ip.replace(".", r"\\.") for ip in ip_list)

    # Template for a single Gitleaks rule
    rule = {
        "description": "Detect specified IPs",
        "regex": combined_regex,
        "tags": ["ip"],
        "allowlist": {
            "paths": []
        }
    }

    # Create the rules dictionary
    rules_toml = {
        "rules": [rule]
    }

    # Write the rules to the TOML file
    with open(output_file, "w") as f:
        toml.dump(rules_toml, f)
    print(f"Custom rules file saved to {output_file}")

if __name__ == "__main__":
    # Example list of IPs
    ip_list = [
        "192.168.1.1",
        "10.0.0.1",
        "172.16.0.1"
    ]

    # Output file for rules.toml
    output_file = "rules.toml"

    # Generate the rules file
    generate_rules_toml(ip_list, output_file)
