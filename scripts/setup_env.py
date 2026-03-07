#!/usr/bin/env python3
"""
环境配置初始化脚本

功能：
1. 生成安全的 API_KEY
2. 验证 .env 文件配置
3. 检查必需的配置项
4. 提供配置建议
"""
import secrets
import sys
from pathlib import Path


def generate_api_key(length: int = 32) -> str:
    """生成安全的 API 密钥"""
    return secrets.token_urlsafe(length)


def generate_password(length: int = 16) -> str:
    """生成强密码"""
    import string
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def check_env_file() -> dict:
    """检查 .env 文件状态"""
    backend_dir = Path(__file__).parent.parent
    env_file = backend_dir / '.env'
    env_example = backend_dir / '.env.example'

    result = {
        'env_exists': env_file.exists(),
        'example_exists': env_example.exists(),
        'env_file': str(env_file),
        'missing_fields': []
    }

    if result['env_exists']:
        # 读取并检查配置
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()

        required_fields = ['DATABASE_URL', 'TAVILY_API_KEY', 'API_KEY']
        for field in required_fields:
            # 检查是否包含示例值
            if field in content:
                lines = [line for line in content.split('\n') if line.strip().startswith(field)]
                if lines:
                    value = lines[0].split('=', 1)[1].strip()
                    if 'your_' in value or 'change-me' in value:
                        result['missing_fields'].append(field)

    return result


def create_env_file():
    """创建 .env 文件"""
    backend_dir = Path(__file__).parent.parent
    env_example = backend_dir / '.env.example'
    env_file = backend_dir / '.env'

    if not env_example.exists():
        print("❌ .env.example 文件不存在")
        return False

    if env_file.exists():
        overwrite = input(f"⚠️  {env_file} 已存在，是否覆盖？(y/N): ")
        if overwrite.lower() != 'y':
            print("❌ 操作已取消")
            return False

    # 读取示例文件
    with open(env_example, 'r', encoding='utf-8') as f:
        content = f.read()

    # 生成 API_KEY
    api_key = generate_api_key()
    content = content.replace('your_secure_api_key_here', api_key)

    # 写入 .env 文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ 已创建 {env_file}")
    print(f"🔑 已生成 API_KEY: {api_key}")
    print("\n⚠️  请手动编辑 .env 文件，填写以下必需配置：")
    print("  - DATABASE_URL")
    print("  - TAVILY_API_KEY")
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("🔧 环境配置初始化工具")
    print("=" * 60)

    # 检查当前状态
    status = check_env_file()

    print(f"\n📁 .env 文件状态:")
    print(f"  - .env.example: {'✅ 存在' if status['example_exists'] else '❌ 不存在'}")
    print(f"  - .env: {'✅ 存在' if status['env_exists'] else '❌ 不存在'}")

    if status['missing_fields']:
        print(f"  - 缺失配置: {', '.join(status['missing_fields'])}")

    # 提供操作选项
    print("\n" + "=" * 60)
    print("请选择操作:")
    print("  1. 生成新的 API_KEY")
    print("  2. 生成强密码")
    print("  3. 创建/更新 .env 文件")
    print("  4. 验证当前配置")
    print("  0. 退出")
    print("=" * 60)

    choice = input("\n请输入选项 (0-4): ").strip()

    if choice == '1':
        key = generate_api_key()
        print(f"\n🔑 生成的 API_KEY:\n{key}")
        print("\n请将此密钥添加到 .env 文件的 API_KEY 配置项中")

    elif choice == '2':
        password = generate_password()
        print(f"\n🔐 生成的强密码:\n{password}")
        print("\n请将此密码用于 DATABASE_URL 中的数据库密码")

    elif choice == '3':
        create_env_file()

    elif choice == '4':
        if not status['env_exists']:
            print("\n❌ .env 文件不存在，请先创建")
        elif status['missing_fields']:
            print(f"\n⚠️  以下配置项需要填写: {', '.join(status['missing_fields'])}")
        else:
            print("\n✅ 配置文件检查通过")

    elif choice == '0':
        print("\n👋 再见!")
        sys.exit(0)

    else:
        print("\n❌ 无效的选项")


if __name__ == '__main__':
    main()
