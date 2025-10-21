import re

with open('app_combined.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all instances
content = re.sub(r'use_container_width=True', r'width="stretch"', content)
content = re.sub(r'use_container_width=False', r'width="content"', content)

with open('app_combined.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ All use_container_width instances have been fixed!")