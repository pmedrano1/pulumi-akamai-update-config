import json

# 1. Read the messy file
with open('raw.txt', 'r') as f:
    content = f.read()

# 2. Fix the escapes
# We turn \" into " and \/ into /
clean_content = content.replace('\\"', '"').replace('\\/', '/')

# 3. Try to load it as JSON
try:
    data = json.loads(clean_content)
    # 4. Save it as a pretty-printed, real JSON file
    with open('rules.json', 'w') as f:
        json.dump(data, f, indent=4)
    print("✅ Success! 'rules.json' has been created and cleaned.")
except json.JSONDecodeError as e:
    print(f"❌ Still having trouble: {e}")
    # Print the first 50 chars of what we tried to parse to debug
    print(f"Start of string: {clean_content[:50]}")