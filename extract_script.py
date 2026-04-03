import json

notebook_path = 'notebooks/CreateModel.ipynb'
output_script = 'debug_script.py'

with open(notebook_path, 'r') as f:
    nb = json.load(f)

code = []
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        code.append(source)

with open(output_script, 'w') as f:
    f.write("\n\n".join(code))

print("Script extracted.")
