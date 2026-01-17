"""
Generate a secure SECRET_KEY for production use
"""
import secrets

print("=" * 60)
print("SECRET KEY GENERATOR")
print("=" * 60)
print()
print("Generating secure random key...")
print()

secret_key = secrets.token_urlsafe(32)

print("Your new SECRET_KEY:")
print("-" * 60)
print(secret_key)
print("-" * 60)
print()
print("Add this to your .env file:")
print(f"SECRET_KEY={secret_key}")
print()
print("✓ Keep this key secure and never commit to git!")
print("=" * 60)
