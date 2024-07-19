import toml
import sys

def merge_configs(base_config_path, repo_config_path, output_path):
    # Load the base configuration (global config)
    with open(base_config_path, 'r') as base_file:
        base_config = toml.load(base_file)
    
    # Load the repository-specific configuration (allowlist)
    with open(repo_config_path, 'r') as repo_file:
        repo_config = toml.load(repo_file)
    
    # Merge the allowlists
    if 'allowlist' in base_config and 'allowlist' in repo_config:
        # Merge paths, ensuring no duplicates
        base_paths = set(base_config['allowlist'].get('paths', []))
        repo_paths = set(repo_config['allowlist'].get('paths', []))
        merged_paths = list(base_paths | repo_paths)
        base_config['allowlist']['paths'] = merged_paths
        
        # Merge regexes, ensuring no duplicates
        base_regexes = set(base_config['allowlist'].get('regexes', []))
        repo_regexes = set(repo_config['allowlist'].get('regexes', []))
        merged_regexes = list(base_regexes | repo_regexes)
        base_config['allowlist']['regexes'] = merged_regexes
        
        # Optionally merge descriptions (if needed)
        if 'description' in repo_config['allowlist']:
            base_config['allowlist']['description'] = repo_config['allowlist']['description']
    elif 'allowlist' in repo_config:
        # If there's no allowlist in the base config, use the repo's allowlist
        base_config['allowlist'] = repo_config['allowlist']
    
    # Save the merged configuration
    with open(output_path, 'w') as output_file:
        toml.dump(base_config, output_file)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python merge_configs.py <base_config_path> <repo_config_path> <output_path>")
        sys.exit(1)
    
    base_config_path = sys.argv[1]
    repo_config_path = sys.argv[2]
    output_path = sys.argv[3]

    merge_configs(base_config_path, repo_config_path, output_path)
