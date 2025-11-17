"""
配置管理模块
负责读取和保存应用配置
"""
import json
import os
import uuid
from typing import Dict, Any, List, Optional
from utils.resource_path import get_data_path


class ConfigManager:
    """配置管理器"""

    DEFAULT_SYSTEM_PROMPT = """你是一名资深技术主管，擅长将技术工作转化为清晰、专业的报告。你的报告风格简洁明了，重点突出，便于管理层快速了解进展。"""

    DEFAULT_USER_PROMPT = """任务：根据下方信息生成工作报告。
规则（必须严格执行）：
1) 如果本输入包含【示例】部分，**你必须按示例格式精确输出且仅输出示例格式的内容**，只替换示例中的条目文本，不得增删任何符号、编号、换行或加注释，且不得输出额外段落或说明。
2) 在示例模式下，其它所有通用规则（字数限制、Markdown 等）**不再生效**；只准输出示例给出的那种纯编号短语列表。
3) 若输入不包含【示例】，才按通用报告规则生成（按模块分组、500字以内、Markdown 等）。
{commit_log}

【示例】
{example}
（如果检测到【示例】，**仅输出与示例同格式的编号列表**，不要多说）。"""

    # 保留旧的 DEFAULT_PROMPT 用于向后兼容
    DEFAULT_PROMPT = DEFAULT_USER_PROMPT

    DEFAULT_CONFIG = {
        "repos": [],  # 多仓库列表
        "log_level": "INFO",  # 日志级别: DEBUG | INFO | WARNING | ERROR
        "ai": {
            "provider": "openai",  # 当前激活的平台: openai | deepseek | zhipu
            "system_prompt": DEFAULT_SYSTEM_PROMPT,  # System Prompt（定义角色）
            "user_prompt": DEFAULT_USER_PROMPT,      # User Prompt（任务说明）
            "prompt": DEFAULT_PROMPT,                # 保留用于向后兼容
            "report_example": "",                    # 报告示例（可选）
            "use_example": False,                    # 是否启用示例数据
            "temperature": 0.7,                      # Temperature 参数 (0.0-2.0)
            "configs": {
                "openai": {
                    "api_key": "",
                    "model": "gpt-4o-mini",
                    "base_url": "https://api.openai.com/v1"
                },
                "deepseek": {
                    "api_key": "",
                    "model": "deepseek-chat",
                    "base_url": "https://api.deepseek.com"
                },
                "zhipu": {
                    "api_key": "",
                    "model": "glm-4-flash"
                }
            }
        }
    }

    def __init__(self, config_file: str = None):
        """
        初始化配置管理器（支持打包环境）

        Args:
            config_file: 配置文件路径（可选，默认使用 data/config.json）
        """
        if config_file is None:
            # 使用 data 目录中的配置文件（支持打包环境）
            config_file = get_data_path("config.json")
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置文件

        Returns:
            配置字典
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 检查是否需要迁移旧配置
                    config = self._migrate_old_config(config)
                    # 合并默认配置(确保新增字段不丢失)
                    return self._merge_config(self.DEFAULT_CONFIG.copy(), config)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            # 配置文件不存在,使用默认配置
            return self.DEFAULT_CONFIG.copy()

    def _merge_config(self, default: Dict, loaded: Dict) -> Dict:
        """
        合并默认配置和加载的配置

        Args:
            default: 默认配置
            loaded: 加载的配置

        Returns:
            合并后的配置
        """
        for key, value in loaded.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    default[key] = self._merge_config(default[key], value)
                else:
                    default[key] = value
        return default

    def save_config(self) -> bool:
        """
        保存配置到文件

        Returns:
            是否保存成功
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

    def get(self, key: str, default=None) -> Any:
        """
        获取配置项

        Args:
            key: 配置键,支持点号分隔的多级键(如 'ai.api_key')
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """
        设置配置项

        Args:
            key: 配置键,支持点号分隔的多级键(如 'ai.api_key')
            value: 配置值
        """
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def get_all(self) -> Dict[str, Any]:
        """
        获取全部配置

        Returns:
            配置字典
        """
        return self.config.copy()

    def _migrate_old_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        迁移旧版单仓库配置到新版多仓库格式

        Args:
            config: 加载的配置

        Returns:
            迁移后的配置
        """
        # 检查是否是旧版配置(有 repo_path 字段但没有 repos 字段)
        if 'repo_path' in config and 'repos' not in config:
            print("检测到旧版配置格式,正在自动迁移到多仓库格式...")

            # 提取旧版字段
            repo_path = config.pop('repo_path', '')
            author_name = config.pop('author_name', '')
            author_email = config.pop('author_email', '')

            # 创建新的仓库列表
            repos = []

            # 如果旧配置有有效的仓库路径,添加到仓库列表
            if repo_path:
                repos.append({
                    'id': str(uuid.uuid4()),
                    'name': '默认仓库',
                    'path': repo_path,
                    'author_name': author_name,
                    'author_email': author_email,
                    'enabled': True
                })
                print(f"已迁移仓库: {repo_path}")

            config['repos'] = repos

            # 保存迁移后的配置
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                print("配置迁移完成并已保存")
            except Exception as e:
                print(f"保存迁移后的配置失败: {e}")

        # 迁移旧版单 Prompt 到新版 system_prompt + user_prompt
        if 'ai' in config:
            # 如果只有旧的 prompt，拆分为 system + user
            if 'prompt' in config['ai'] and 'system_prompt' not in config['ai']:
                print("检测到旧版 Prompt 格式，正在迁移到 system_prompt + user_prompt...")
                # 全部作为 user_prompt，使用默认 system_prompt
                config['ai']['user_prompt'] = config['ai']['prompt']
                config['ai']['system_prompt'] = self.DEFAULT_SYSTEM_PROMPT
                print("Prompt 迁移完成: 使用默认 system_prompt，旧 prompt 作为 user_prompt")

        return config

    def get_repos(self) -> List[Dict[str, Any]]:
        """
        获取所有仓库配置

        Returns:
            仓库列表
        """
        return self.config.get('repos', [])

    def get_enabled_repos(self) -> List[Dict[str, Any]]:
        """
        获取所有已启用的仓库配置

        Returns:
            已启用的仓库列表
        """
        return [repo for repo in self.get_repos() if repo.get('enabled', True)]

    def add_repo(self, name: str, path: str, author_name: str = '',
                 author_email: str = '', enabled: bool = True) -> str:
        """
        添加新仓库

        Args:
            name: 仓库名称
            path: 仓库路径
            author_name: 作者名称
            author_email: 作者邮箱
            enabled: 是否启用

        Returns:
            新仓库的 ID
        """
        repo_id = str(uuid.uuid4())
        new_repo = {
            'id': repo_id,
            'name': name,
            'path': path,
            'author_name': author_name,
            'author_email': author_email,
            'enabled': enabled
        }

        if 'repos' not in self.config:
            self.config['repos'] = []

        self.config['repos'].append(new_repo)
        return repo_id

    def update_repo(self, repo_id: str, **kwargs) -> bool:
        """
        更新仓库配置

        Args:
            repo_id: 仓库 ID
            **kwargs: 要更新的字段(name, path, author_name, author_email, enabled)

        Returns:
            是否更新成功
        """
        repos = self.config.get('repos', [])
        for repo in repos:
            if repo.get('id') == repo_id:
                # 更新允许的字段
                allowed_fields = ['name', 'path', 'author_name', 'author_email', 'enabled']
                for key, value in kwargs.items():
                    if key in allowed_fields:
                        repo[key] = value
                return True
        return False

    def delete_repo(self, repo_id: str) -> bool:
        """
        删除仓库

        Args:
            repo_id: 仓库 ID

        Returns:
            是否删除成功
        """
        repos = self.config.get('repos', [])
        original_len = len(repos)
        self.config['repos'] = [repo for repo in repos if repo.get('id') != repo_id]
        return len(self.config['repos']) < original_len

    def toggle_repo(self, repo_id: str) -> bool:
        """
        切换仓库启用状态

        Args:
            repo_id: 仓库 ID

        Returns:
            是否切换成功
        """
        repos = self.config.get('repos', [])
        for repo in repos:
            if repo.get('id') == repo_id:
                repo['enabled'] = not repo.get('enabled', True)
                return True
        return False

    def get_repo_by_id(self, repo_id: str) -> Optional[Dict[str, Any]]:
        """
        根据 ID 获取仓库配置

        Args:
            repo_id: 仓库 ID

        Returns:
            仓库配置字典,如果不存在返回 None
        """
        repos = self.config.get('repos', [])
        for repo in repos:
            if repo.get('id') == repo_id:
                return repo.copy()
        return None
