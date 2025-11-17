"""
模块功能测试脚本
用于快速验证各个核心模块是否正常工作
"""
import sys
import os
from datetime import datetime, timedelta

# 设置 UTF-8 编码输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def test_config_manager():
    """测试配置管理器"""
    print("\n=== 测试 ConfigManager ===")
    try:
        from infrastructure.config_manager import ConfigManager

        config = ConfigManager("test_config.json")

        # 测试基本配置
        config.set("test_key", "test_value")
        config.set("nested.key", "nested_value")
        assert config.get("test_key") == "test_value"
        assert config.get("nested.key") == "nested_value"

        # 测试多仓库功能
        repo_id = config.add_repo(
            name="测试仓库",
            path="/test/path",
            author_name="测试作者",
            author_email="test@example.com"
        )

        repos = config.get_repos()
        assert len(repos) == 1
        assert repos[0]['name'] == "测试仓库"

        # 测试更新仓库
        config.update_repo(repo_id, name="更新后的仓库")
        updated_repo = config.get_repo_by_id(repo_id)
        assert updated_repo['name'] == "更新后的仓库"

        # 测试切换启用状态
        config.toggle_repo(repo_id)
        enabled_repos = config.get_enabled_repos()
        assert len(enabled_repos) == 0

        # 测试删除仓库
        config.delete_repo(repo_id)
        repos = config.get_repos()
        assert len(repos) == 0

        print("[OK] ConfigManager 测试通过 (包含多仓库功能)")
        return True
    except Exception as e:
        print(f"[FAIL] ConfigManager 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_git_service():
    """测试 Git 服务"""
    print("\n=== 测试 GitService ===")
    try:
        from core.services.git_service import GitService
        import os

        # 使用当前项目作为测试仓库
        current_repo = "."
        if not os.path.exists(".git"):
            print("[SKIP] 跳过 GitService 测试(当前目录不是 Git 仓库)")
            return True

        service = GitService(current_repo)
        commits = service.get_commits(
            start_date=datetime.now() - timedelta(days=30)
        )

        print(f"[OK] GitService 测试通过,获取到 {len(commits)} 条提交")
        if commits:
            print(f"  最新提交: {commits[0].message[:50]}")
        return True
    except Exception as e:
        print(f"[FAIL] GitService 测试失败: {e}")
        return False


def test_formatter():
    """测试数据格式化器"""
    print("\n=== 测试 DataFormatter ===")
    try:
        from core.services.formatter import DataFormatter
        from core.services.git_service import CommitRecord

        formatter = DataFormatter()

        # 创建测试提交(包含多仓库)
        test_commits = [
            CommitRecord(
                hash="abc123",
                author="Test User",
                email="test@example.com",
                date=datetime.now(),
                message="feat: 添加新功能",
                repo_name="仓库A",
                repo_path="/path/to/repo_a"
            ),
            CommitRecord(
                hash="def456",
                author="Test User",
                email="test@example.com",
                date=datetime.now(),
                message="fix: 修复bug",
                repo_name="仓库B",
                repo_path="/path/to/repo_b"
            ),
        ]

        # 测试分类
        assert formatter.classify_commit("feat: test") == "feat"
        assert formatter.classify_commit("fix: test") == "fix"

        # 测试格式化
        summary = formatter.format_commits(test_commits)
        assert "新功能" in summary or "feat" in summary
        assert "修复" in summary or "fix" in summary
        # 测试仓库信息
        assert "仓库A" in summary
        assert "仓库B" in summary
        assert "涉及仓库: 2 个" in summary

        print("[OK] DataFormatter 测试通过 (包含多仓库)")
        return True
    except Exception as e:
        print(f"[FAIL] DataFormatter 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_client():
    """测试 AI 客户端(新架构:适配器模式)"""
    print("\n=== 测试 AiClient (适配器架构) ===")
    try:
        from infrastructure.ai_client import AiClientFactory
        from infrastructure.config_manager import ConfigManager
        from infrastructure.adapters.base import BaseAdapter
        from infrastructure.adapters.openai_adapter import OpenAIAdapter
        from infrastructure.adapters.deepseek_adapter import DeepseekAdapter
        from infrastructure.adapters.zhipu_adapter import ZhipuAdapter

        # 创建测试配置
        test_config = ConfigManager("test_ai_config.json")
        test_config.set('ai.provider', 'openai')
        test_config.set('ai.prompt', ConfigManager.DEFAULT_PROMPT)
        test_config.set('ai.configs.openai', {
            'api_key': 'fake_api_key',
            'model': 'gpt-4o-mini'
        })

        # 测试工厂创建
        client = AiClientFactory.create(test_config)
        assert isinstance(client, BaseAdapter)
        assert isinstance(client, OpenAIAdapter)
        assert "{commit_log}" in client.prompt_template
        assert client.platform_name == "OpenAI GPT"

        # 测试 Token 用量统计接口
        usage = client.get_token_usage()
        assert isinstance(usage, dict)

        # 测试三个适配器都能正常创建
        test_config.set('ai.provider', 'deepseek')
        test_config.set('ai.configs.deepseek', {'api_key': 'test', 'model': 'deepseek-chat'})
        deepseek_client = AiClientFactory.create(test_config)
        assert isinstance(deepseek_client, DeepseekAdapter)

        test_config.set('ai.provider', 'zhipu')
        test_config.set('ai.configs.zhipu', {'api_key': 'test', 'model': 'glm-4-flash'})
        zhipu_client = AiClientFactory.create(test_config)
        assert isinstance(zhipu_client, ZhipuAdapter)

        print("[OK] AiClient 测试通过 (OpenAI/Deepseek/智谱 三适配器)")
        return True
    except Exception as e:
        print(f"[FAIL] AiClient 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_repo_scanner():
    """测试仓库扫描器"""
    print("\n=== 测试 RepoScanner ===")
    try:
        from core.repo_scanner import RepoScanner
        import os

        scanner = RepoScanner()

        # 扫描当前项目目录(应该能找到当前Git仓库)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        repos = scanner.scan_directory(current_dir, max_depth=1)

        # 应该至少找到当前项目
        assert len(repos) >= 1, "应该至少找到当前Git仓库"

        # 检查第一个仓库的信息
        first_repo = repos[0]
        assert first_repo.name, "仓库名称不应为空"
        assert first_repo.path, "仓库路径不应为空"
        assert os.path.exists(first_repo.path), "仓库路径应该存在"

        print(f"[OK] RepoScanner 测试通过,找到 {len(repos)} 个仓库")
        if repos:
            print(f"  示例仓库: {repos[0].name} ({repos[0].path})")
            if repos[0].author_name or repos[0].author_email:
                print(f"  作者信息: {repos[0].author_name} <{repos[0].author_email}>")

        return True
    except Exception as e:
        print(f"[FAIL] RepoScanner 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_import():
    """测试 UI 模块导入"""
    print("\n=== 测试 UI 模块 ===")
    try:
        from ui.main_window import MainWindow
        from ui.repo_scan_dialog import RepoScanDialog
        print("[OK] UI 模块导入成功")
        return True
    except Exception as e:
        print(f"[FAIL] UI 模块导入失败: {e}")
        print("  可能原因: PyQt5 未安装,请运行 pip install PyQt5")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("=" * 50)
    print("开始测试核心模块...")
    print("=" * 50)

    results = {
        "ConfigManager": test_config_manager(),
        "GitService": test_git_service(),
        "DataFormatter": test_formatter(),
        "AiClient": test_ai_client(),
        "RepoScanner": test_repo_scanner(),
        "UI": test_ui_import()
    }

    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)

    for name, result in results.items():
        status = "[OK] 通过" if result else "[FAIL] 失败"
        print(f"{name:20} {status}")

    total = len(results)
    passed = sum(results.values())
    print("\n" + "=" * 50)
    print(f"总计: {passed}/{total} 个模块测试通过")
    print("=" * 50)

    # 清理测试文件
    import os
    if os.path.exists("test_config.json"):
        os.remove("test_config.json")
    if os.path.exists("test_ai_config.json"):
        os.remove("test_ai_config.json")
    if os.path.exists("temp_test_config.json"):
        os.remove("temp_test_config.json")

    if passed == total:
        print("\n[SUCCESS] 所有测试通过,可以运行 main.py 启动程序!")
        return 0
    else:
        print("\n[WARNING] 部分测试失败,请检查依赖安装或代码")
        return 1


if __name__ == "__main__":
    sys.exit(main())
