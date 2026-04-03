import json
import os

notebook_path = 'notebooks/CreateModel.price.change.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

target_code_snippet = "def generate_charts(current_date):"

new_code_lines = [
    "if not USING_CACHED_DATAFRAME:\n",
    "    from functools import partial\n",
    "    \n",
    "    with mp.Pool(processes = NPARTITIONS) as p:\n",
    "        results = p.map(partial(generate_charts, asset_natal_chart=asset_natal_chart), dates_to_generate)\n",
    "\n",
    "    for x in results:\n",
    "        charts[x[0]] = x[1]\n",
    "        aspects[x[0]] = x[2]\n",
    "        aspects_transiting[x[0]] = x[3]"
]

patched = False
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source_str = "".join(cell['source'])
        if target_code_snippet in source_str:
            print("Found target cell. Patching...")
            cell['source'] = new_code_lines
            patched = True
            break

if patched:
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    print("Notebook patched successfully.")
else:
    print("Target cell not found!")
