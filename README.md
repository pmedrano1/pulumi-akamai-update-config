Akamai CP Code Modernization & Rule Update
This Pulumi project manages the update lifecycle of an existing Akamai Property. Specifically, it automates the creation of a unique CP Code and injects it into an existing configuration's rule tree.

🔄 The "Takeover" Workflow
When moving a property from a "Clone" project to a "Maintenance" project, follow these steps:

1. Resource Discovery & Import
Pulumi must first "adopt" the existing property.

Bash
# Syntax: pulumi import akamai:index/property:Property <ResourceName> <PropertyID>,<ContractID>,<GroupID>
pulumi import akamai:index/property:Property clonedProperty prp_123,ctr_456,grp_789
2. Capturing the Rule Tree
During the import, Pulumi prints a giant rules string. Capture this. It is the Source of Truth for your configuration.

⚠️ JSON Gotchas & The "Repair" Phase
1. The "Escaped String" Trap
The rules string provided by Pulumi is "stringified" for the terminal (filled with backslashes like \"rules\"). Python's JSON parser will fail if you read this directly.

The Solution: Use a repair script to unescape the text and remove trailing Pulumi artifacts (like the final ", or ").

Python
# repair.py - Use this to clean your raw terminal output
import json

with open('raw_rules.txt', 'r') as f:
    content = f.read().replace('\\"', '"').replace('\\/', '/')

# Trim logic to find the heart of the JSON
start = content.find('{')
end = content.rfind('}')
final_json = content[start : end + 1]

with open('rules.json', 'w') as f:
    json.dump(json.loads(final_json), f, indent=4)
2. The "Replacement" Safety Gate
If your Pulumi propertyName does not match the actual Akamai name exactly, Pulumi will plan a Replace (+-).

Replace = Delete the old property + Create a new one. (Dangerous!)

Update = Modify the existing property in place. (Safe!)

The Fix: Ensure your config matches the Akamai Name:
pulumi config set propertyName "cloned_pulumi_a-vrv-amd"

🏗️ Single File vs. Modular Snippets
This project supports two ways of managing your Akamai rules:

Option A: Consolidated rules.json (Easier)
Use the output from pulumi import. This gives you one giant file that is easy for the script to traverse and update.

Pros: Simple script logic; one single source of truth.

Cons: Harder for humans to read 10,000 lines of JSON.

Option B: Modular Snippets (Standard Akamai CLI)
Use the Akamai CLI to download modular snippets:
akamai property-manager import --property "NAME"

Pros: Highly readable; changes to specific policies (like CORS) are easy to track in Git.

Cons: Requires a "Stitcher" function in your Pulumi script to combine files before deployment.

🛠️ Implementation Details
The CP Code "Swap" Logic
The script uses a recursive Python function to find the cpCode behavior regardless of where it lives in the rule tree (Default Rule or a child rule).

Python
def swap_cp_code(node, new_id):
    if "behaviors" in node:
        for b in node["behaviors"]:
            if b.get("name") == "cpCode":
                b["options"]["value"]["id"] = new_id
    if "children" in node:
        for child in node["children"]:
            swap_cp_code(child, new_id)
Protection Toggle
Imported resources are protected by default. To perform the CP Code update:

Set protect=False in your ResourceOptions.

Run pulumi up.

Set protect=True again once the update is successful to prevent accidental deletion.

🚀 Execution
Bash
# Preview: Ensure it says "~ update", NOT "+- replace"
pulumi preview

# Deploy the new CP Code and Activation
pulumi up
Maintenance workflow for Akamai Adaptive Media Delivery (AMD) using Pulumi Python.