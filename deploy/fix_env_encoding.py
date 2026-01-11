"""
Fix .env file encoding from UTF-16 to UTF-8
"""
import os

env_file = '.env'
backup_file = '.env.backup'

print("="*60)
print("FIX .ENV FILE ENCODING")
print("="*60)

if not os.path.exists(env_file):
    print(f"ERROR: {env_file} not found!")
    exit(1)

# Backup original
print(f"\n[1/3] Creating backup: {backup_file}")
with open(env_file, 'rb') as f:
    content = f.read()
with open(backup_file, 'wb') as f:
    f.write(content)
print("  ✓ Backup created")

# Try to decode and fix
print("\n[2/3] Fixing encoding...")
try:
    # Try UTF-16 first (common Windows issue)
    text = content.decode('utf-16')
    print("  Detected UTF-16 encoding")
except:
    try:
        # Try UTF-16-LE
        text = content.decode('utf-16-le')
        print("  Detected UTF-16-LE encoding")
    except:
        try:
            # Remove null bytes manually
            text = content.replace(b'\x00', b'').decode('utf-8')
            print("  Removed null bytes")
        except:
            print("  ERROR: Could not decode file")
            exit(1)

# Clean up text
text = text.strip()
lines = text.split('\n')
clean_lines = [line.strip() for line in lines if line.strip()]

print(f"  Found {len(clean_lines)} configuration lines")

# Write back as UTF-8
print("\n[3/3] Saving as UTF-8...")
with open(env_file, 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(clean_lines) + '\n')

print("  ✓ File saved with UTF-8 encoding")

# Verify
print("\n" + "="*60)
print("VERIFICATION - Current .env content:")
print("="*60)
with open(env_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            # Hide sensitive values
            if 'SECRET' in line or 'PASSWORD' in line or 'TOKEN' in line:
                key = line.split('=')[0]
                print(f"  {key}=***hidden***")
            else:
                print(f"  {line}")

print("\n✓ DONE! Try running your command again.")
print("="*60)
