import json
import pandas as pd
from pydantic import BaseModel, ValidationError
from typing import List, Literal
from lxml import etree
import os

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_LOG = os.path.join(BASE_DIR, "../dat/json/changes_log.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "../dat/processed")
SCHEMA_DIR = os.path.join(BASE_DIR, "schemas")

# --- Pydantic Model (JSON Schema) ---
class LogEntry(BaseModel):
    timestamp: str
    file: str
    change: Literal['CREATED', 'MODIFIED', 'DELETED']

class LogContainer(BaseModel):
    logs: List[LogEntry]

def generate_json_schema():
    """Generates and saves JSON Schema based on Pydantic model."""
    schema_path = os.path.join(SCHEMA_DIR, "log_schema.json")
    with open(schema_path, "w") as f:
        f.write(json.dumps(LogEntry.model_json_schema(), indent=2))
    print(f"[Schema] JSON Schema saved to {schema_path}")

# --- Validators & Converters ---

def validate_and_load_json(file_path):
    """Reads JSON Lines, validates with Pydantic, returns list of models."""
    valid_entries = []
    errors = 0
    
    if not os.path.exists(file_path):
        print(f"[Warn] Input file {file_path} not found.")
        return []

    with open(file_path, 'r') as f:
        for line in f:
            try:
                # Parse JSON Line
                data = json.loads(line)
                # Validate with Pydantic
                entry = LogEntry(**data)
                valid_entries.append(entry)
            except (json.JSONDecodeError, ValidationError) as e:
                errors += 1
                # print(f"[Error] Invalid log entry: {e}")
    
    print(f"[JSON] Loaded {len(valid_entries)} valid entries. {errors} invalid ignored.")
    return valid_entries

def export_to_csv(entries: List[LogEntry]):
    """Exports data to CSV following RFC 4180."""
    if not entries: return

    df = pd.DataFrame([e.model_dump() for e in entries])
    
    # Validate against simple CSV schema definition
    csv_schema_path = os.path.join(SCHEMA_DIR, "csv_schema.json")
    with open(csv_schema_path, 'r') as f:
        schema_def = json.load(f)
    
    # Check columns
    if list(df.columns) != schema_def["columns"]:
        print("[Error] CSV Schema Mismatch: Column names do not match.")
        return

    output_path = os.path.join(OUTPUT_DIR, "data_export.csv")
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"[CSV] Exported to {output_path} (RFC 4180 Compliant)")

def export_to_xml(entries: List[LogEntry]):
    """Exports data to XML and validates against XSD."""
    if not entries: return

    root = etree.Element("LogData")
    for entry in entries:
        entry_elem = etree.SubElement(root, "Entry")
        etree.SubElement(entry_elem, "timestamp").text = entry.timestamp
        etree.SubElement(entry_elem, "file").text = entry.file
        etree.SubElement(entry_elem, "change").text = entry.change

    # Validate against XSD
    xsd_path = os.path.join(SCHEMA_DIR, "log_schema.xsd")
    try:
        xmlschema_doc = etree.parse(xsd_path)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        
        # Check validity
        if xmlschema.validate(root):
            output_path = os.path.join(OUTPUT_DIR, "data_export.xml")
            tree = etree.ElementTree(root)
            tree.write(output_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
            print(f"[XML] Exported to {output_path} (Validated against XSD)")
        else:
            print("[XML] Validation Failed against XSD!")
            for error in xmlschema.error_log:
                print(f"  - {error.message}")

    except Exception as e:
        print(f"[XML] Error loading XSD or validating: {e}")

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    generate_json_schema()
    
    print("--- Starting Data Processing ---")
    entries = validate_and_load_json(INPUT_LOG)
    
    if entries:
        export_to_csv(entries)
        export_to_xml(entries)
    else:
        print("No data to process.")

if __name__ == "__main__":
    main()
