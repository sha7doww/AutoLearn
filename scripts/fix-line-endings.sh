#!/bin/bash
# 修复所有脚本的行尾符
# Fix CRLF line endings to LF for all scripts

echo "Fixing line endings for all shell scripts..."

# Fix all .sh files
for file in /home/sha7dow/Project/AutoLearn/scripts/*.sh; do
    if [ -f "$file" ]; then
        sed -i 's/\r$//' "$file"
        echo "✓ Fixed: $(basename $file)"
    fi
done

# Also fix Python files if needed
find /home/sha7dow/Project/AutoLearn/backend -name "*.py" -type f -exec sed -i 's/\r$//' {} \;
echo "✓ Fixed all Python files"

echo ""
echo "✅ All line endings fixed!"
echo ""
echo "To prevent this in the future, make sure:"
echo "  1. Git is configured: git config --global core.autocrlf input"
echo "  2. Your editor uses LF line endings (Unix mode)"
