import os
import sys
import traceback

# Get absolute path of the root directory (where this script is)
root_dir = os.path.dirname(os.path.abspath(__file__))
script_name = 'debug_create_model_price_change.py'
script_path = os.path.join(root_dir, 'notebooks', script_name)

print("Root Dir:", root_dir)
print("Target Script:", script_path)
print("Exists:", os.path.exists(script_path))

try:
    # Change to notebooks dir so relative paths inside the debug script (like ./config) work
    notebooks_dir = os.path.join(root_dir, 'notebooks')
    if os.path.isdir(notebooks_dir):
        os.chdir(notebooks_dir)
        print("Changed CWD to:", os.getcwd())
    
    # Add notebooks dir to sys.path so modules inside it (like settings) can be imported
    if notebooks_dir not in sys.path:
        sys.path.append(notebooks_dir)

    # Add root to sys.path to find pyastrotrader
    if root_dir not in sys.path:
        sys.path.append(root_dir)
    
    # Execute the debug script
    print(f"Executing {script_path}...")
    
    with open(script_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    exec(code, {'__name__': '__main__'})

except Exception:
    with open('../traceback.log', 'w') as f:
        traceback.print_exc(file=f)
    traceback.print_exc()
