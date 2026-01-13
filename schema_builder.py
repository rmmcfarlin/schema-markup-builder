from pathlib import Path
import json
import re
import csv


placeholder_regex = re.compile(r"\{\{(\w+)\}\}")

schema_data_path = Path("./schema_data/brand-pages.csv")
brand_template_path = Path('./schema_templates/brand-template.json')

with open(brand_template_path, 'r') as file:
    brand_dict = json.load(file)


def create_url_name(brand):
    return brand.replace(" ", "-").lower()

def create_url_search_name(brand):
    return brand.replace(" ", "+")


def complete_csv(csv_path):

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    for col in ("brand_url_name", "brand_url_search_term"):
        if col not in fieldnames:
            fieldnames.append(col)
    
    for row in rows:
        brand = row.get("brand_name", "").strip()
        if brand:
            row["brand_url_name"] = create_url_name(brand)
            row["brand_url_search_term"] = create_url_search_name(brand)
    
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def replace_variables(template, row):

    if isinstance(template, dict):
        return {k: replace_variables(v, row) for k, v in template.items()}
    if isinstance(template, list):
        return [replace_variables(v, row) for v in template]
    if isinstance(template, str):
        def repl(m):
            key = m.group(1)
            return row.get(key, "")
        return placeholder_regex.sub(repl, template)
    return template

def main():
    complete_csv(schema_data_path)
    out_dir = Path("./Output")
    with open(schema_data_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [h.strip() for h in reader.fieldnames]
        for row in reader:
            replaced = replace_variables(brand_dict, row)

            brand_name = row.get("brand_url_name") or "output"
            out_path = out_dir / f"{brand_name}-schema.json"
            out_path.write_text(json.dumps(replaced, indent=2, ensure_ascii=False), encoding="utf-8")

main()