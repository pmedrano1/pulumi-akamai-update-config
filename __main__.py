import pulumi
import pulumi_akamai as akamai
import json
import os

config = pulumi.Config()

# 1. Variables
contract_id = config.require("contractId")
group_id    = config.require("groupId")
prop_id     = config.require("propertyId")
prop_name   = config.require("propertyName")
email       = config.require("notificationEmail")
product_id  = "prd_Adaptive_Media_Delivery"

# 2. CREATE A NEW CP CODE
new_cp_code = akamai.CpCode("newAmdCpCode",
    name=f"{prop_name}-cp".replace("_", "-")[:50],
    contract_id=contract_id,
    group_id=group_id,
    product_id=product_id
)

# 3. RULE UPDATE LOGIC (Reading from local file)
def update_rules_with_cp_code(cp_code_urn):
    # --- MODIFIED: Read from local rules.json instead of API ---
    path = os.path.join(os.getcwd(), "rules.json")
    with open(path, "r") as f:
        rules_dict = json.load(f)
    
    # Extract numeric ID from URN (e.g. 'cpc_123' -> 123)
    numeric_cp_id = int(cp_code_urn.split('_')[-1])

    def swap_cp_code(node):
        if "behaviors" in node:
            for behavior in node["behaviors"]:
                if behavior.get("name") == "cpCode":
                    behavior["options"]["value"]["id"] = numeric_cp_id
        
        if "children" in node:
            for child in node["children"]:
                swap_cp_code(child)

    swap_cp_code(rules_dict["rules"])
    return json.dumps(rules_dict)

# 4. DEFINE THE PROPERTY
amd_property = akamai.Property("clonedProperty",
    name=prop_name,
    contract_id=contract_id,
    group_id=group_id,
    product_id=product_id,
    # --- ADDED: Matching your import output ---
    rule_format="v2026-02-16", 
    hostnames=[akamai.PropertyHostnameArgs(
        cname_from="cloned-pulumi-demo-vrv.akamaized.net", # Update if different
        cname_to="cloned-pulumi-demo-vrv.akamaized.net",   # Update if different
        cert_provisioning_type="CPS_MANAGED",
    )],
    rules=new_cp_code.id.apply(update_rules_with_cp_code),
    opts=pulumi.ResourceOptions(protect=False) # Matches import safety
)

# 5. ACTIVATE ON STAGING
activation = akamai.PropertyActivation("activateNewCpCode",
    property_id=amd_property.id,
    version=amd_property.latest_version,
    network="STAGING",
    contacts=[email],
    note="Updated CP Code to unique ID via rules.json",
    auto_acknowledge_rule_warnings=True
)

pulumi.export("new_cp_code_number", new_cp_code.id)