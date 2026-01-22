import os
import json
import re

class ActoInterpreter:
    def __init__(self, rules_file):
        self.rules = []
        self.parse_rules(rules_file)

    def parse_size(self, size_str):
        """Converts strings like '10MB', '1KB' to bytes."""
        units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}
        match = re.match(r"(\d+)([A-Za-z]+)", size_str)
        if match:
            value, unit = match.groups()
            return int(value) * units.get(unit.upper(), 1)
        return int(size_str)

    def parse_rules(self, filepath):
        """Parses the .acto rules file."""
        if not os.path.exists(filepath):
            print(f"Error: Rules file '{filepath}' not found.")
            return

        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or not line.startswith("IF"):
                    continue
                
                # Syntax: IF <var> <op> <val> THEN TAG <tag>
                # Regex to capture components
                pattern = r"IF\s+(\w+)\s+(IS|>|<)\s+('?[\w\.]+'?|\d+[A-Z]+)\s+THEN\s+TAG\s+'([^']+)'"
                match = re.match(pattern, line)
                
                if match:
                    variable, operator, value, tag = match.groups()
                    # Strip quotes from string values
                    if value.startswith("'"):
                        value = value.strip("'")
                    
                    self.rules.append({
                        "var": variable,
                        "op": operator,
                        "val": value,
                        "tag": tag
                    })
                    print(f"Loaded Rule: {variable} {operator} {value} -> {tag}")

    def evaluate(self, file_path):
        """Applies rules to a specific file."""
        tags = []
        try:
            stats = os.stat(file_path)
            file_size = stats.st_size
            _, ext = os.path.splitext(file_path)
            
            # Context variables for the file
            context = {
                "size": file_size,
                "extension": ext.lower() # Normalize extension
            }

            for rule in self.rules:
                var_name = rule["var"]
                operator = rule["op"]
                rule_val = rule["val"]
                
                if var_name not in context:
                    continue

                actual_val = context[var_name]

                # Logic comparison
                is_match = False
                
                if var_name == "size":
                    # Convert rule value (e.g. "10MB") to bytes for comparison
                    rule_bytes = self.parse_size(str(rule_val))
                    if operator == ">":
                        is_match = actual_val > rule_bytes
                    elif operator == "<":
                        is_match = actual_val < rule_bytes
                    elif operator == "IS":
                        is_match = actual_val == rule_bytes
                
                elif var_name == "extension":
                    if operator == "IS":
                        is_match = actual_val == rule_val.lower()

                if is_match:
                    tags.append(rule["tag"])

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
        
        return list(set(tags)) # Return unique tags

    def scan_directory(self, target_dir, output_file):
        """Scans directory, tags files, outputs JSON."""
        results = {}
        
        if not os.path.exists(target_dir):
            print(f"Directory {target_dir} does not exist. Creating it.")
            os.makedirs(target_dir)

        print(f"\nScanning: {target_dir}")
        for root, _, files in os.walk(target_dir):
            for file in files:
                full_path = os.path.join(root, file)
                tags = self.evaluate(full_path)
                results[file] = {
                    "path": full_path,
                    "tags": tags,
                    "size_bytes": os.path.getsize(full_path)
                }
                print(f"  -> {file}: {tags}")

        # Save to JSON
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"\nMetadata saved to: {output_file}")

if __name__ == "__main__":
    # Paths relative to where the script is run
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RULES_PATH = os.path.join(BASE_DIR, "rules.acto")
    TARGET_DIR = os.path.join(BASE_DIR, "target_folder")
    OUTPUT_JSON = os.path.join(BASE_DIR, "../dat/json/metadata.json")

    interpreter = ActoInterpreter(RULES_PATH)
    interpreter.scan_directory(TARGET_DIR, OUTPUT_JSON)
