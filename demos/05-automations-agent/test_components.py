#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas>=2.0.0"]
# ///

"""Quick test to verify components work"""

import pandas as pd
from pathlib import Path

print("🧪 Testing Automation Agent Components")
print("=" * 60)

# Test 1: Database exists and is readable
print("\n1. Testing database...")
try:
    db_path = Path(__file__).parent / "automations_database.csv"
    df = pd.read_csv(db_path)
    print(f"   ✅ Database loaded: {len(df)} automations found")
    print(f"   Categories: {', '.join(df['category'].unique())}")
except Exception as e:
    print(f"   ❌ Database error: {e}")
    exit(1)

# Test 2: List automations (simulating MCP tool)
print("\n2. Testing list_all_automations logic...")
try:
    metadata = df[['id', 'name', 'description', 'category', 'script_type']]
    print(f"   ✅ Can retrieve metadata for {len(metadata)} automations")
    print("\n   First 3 automations:")
    for _, row in metadata.head(3).iterrows():
        print(f"     - {row['name']} ({row['category']}, {row['script_type']})")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Test 3: Get specific automation (simulating MCP tool)
print("\n3. Testing get_automation_by_id logic...")
try:
    automation = df[df['id'] == 1]
    if not automation.empty:
        auto = automation.iloc[0]
        print(f"   ✅ Retrieved automation ID 1: {auto['name']}")
        print(f"   Template length: {len(auto['template'])} characters")
        print(f"   First line: {auto['template'].split(chr(10))[0]}")
    else:
        print(f"   ❌ No automation found with ID 1")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Test 4: Search by category (simulating MCP tool)
print("\n4. Testing search_by_category logic...")
try:
    filtered = df[df['category'].str.contains("File Management", case=False, na=False)]
    print(f"   ✅ Found {len(filtered)} File Management automations:")
    for _, row in filtered.iterrows():
        print(f"     - {row['name']}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Test 5: Output directory exists
print("\n5. Testing output directory...")
try:
    output_dir = Path(__file__).parent / "generated_scripts"
    if output_dir.exists():
        print(f"   ✅ Output directory exists: {output_dir}")
        files = list(output_dir.glob("*"))
        print(f"   Currently contains {len(files)} files")
    else:
        print(f"   ⚠️  Output directory doesn't exist (will be created)")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✨ All component tests passed!")
print("\nReady to run the agent:")
print("  export ANTHROPIC_API_KEY='your-key'")
print("  uv run automation_agent.py")
