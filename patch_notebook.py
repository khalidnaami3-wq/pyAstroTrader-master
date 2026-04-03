import json

notebook_path = 'notebooks/DownloadData.ipynb'

with open(notebook_path, 'r') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        new_source = []
        for line in cell['source']:
            if "TIME_SERIES_DAILY_ADJUSTED" in line:
                line = line.replace("TIME_SERIES_DAILY_ADJUSTED", "TIME_SERIES_DAILY")
                line = line.replace("outputsize=full", "outputsize=compact")
            if "6. volume" in line:
                line = line.replace("6. volume", "5. volume")
            new_source.append(line)
        cell['source'] = new_source

with open(notebook_path, 'w') as f:
    json.dump(nb, f, indent=1)

print("Notebook patched successfully.")
