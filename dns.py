import re

# Read DNS list from file
dns_file = "dns_list.txt"  # Update the file name if needed
with open(dns_file, "r") as file:
    dns_list = [line.strip().lstrip('.') for line in file if line.strip()]  # Remove leading dot and empty lines

# Template for a Gitleaks rule
RULE_TEMPLATE = """
[[rules]]
id = "{rule_id}"
description = "Detects DNS names related to {domain}"
regex = '''\\b[a-zA-Z0-9.-]+\\.{escaped_domain}\\b'''
tags = ["dns", "sensitive"]
"""

# Generate rules.toml content
rules_toml = ""
for dns in dns_list:
    escaped_domain = re.escape(dns)  # Escape for regex
    rule_id = f"DNS-{dns.replace('.', '-')}"  # Unique rule ID
    rules_toml += RULE_TEMPLATE.format(rule_id=rule_id, domain=dns, escaped_domain=escaped_domain)

# Write to rules.toml
with open("rules.toml", "w") as file:
    file.write(rules_toml)

print("✅ rules.toml generated successfully!")
