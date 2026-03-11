#!/bin/bash
# 验证关键配置文件是否被 Git 追踪
# 在修改 .gitignore 后必须运行此脚本

set -e

echo "🔍 验证关键配置文件..."
echo

CRITICAL_FILES=(
    "AGENTS.md"
    "MEMORY.md"
    "IDENTITY.md"
    "USER.md"
    "SOUL.md"
    "TOOLS.md"
    "HEARTBEAT.md"
)

ISSUES_FOUND=0

for file in "${CRITICAL_FILES[@]}"; do
    if git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
        echo "✅ $file - 已被 Git 追踪"
    else
        echo "❌ $file - 未被 Git 追踪！"
        ISSUES_FOUND=1
    fi
done

echo

if [ $ISSUES_FOUND -eq 1 ]; then
    echo "🚨 发现问题：某些关键文件未被 Git 追踪！"
    echo
    echo "可能原因："
    echo "  1. 文件被添加到 .gitignore"
    echo "  2. 文件不存在"
    echo
    echo "解决方法："
    echo "  1. 检查 .gitignore，移除对这些文件的忽略"
    echo "  2. 运行: git add <file> && git commit -m 'add: 添加关键配置文件'"
    echo
    exit 1
else
    echo "✅ 所有关键文件都已被 Git 追踪"
    exit 0
fi
