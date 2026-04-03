import json
import os

notebook_path = 'notebooks/Predict.price.change.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

count = 0
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        new_source = []
        for line in cell['source']:
            if "scheduler='processes'" in line:
                line = line.replace("scheduler='processes'", "scheduler='threads'")
                count += 1
            new_source.append(line)
        cell['source'] = new_source

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print(f"Notebook patched successfully. Replaced {count} occurrences.")
