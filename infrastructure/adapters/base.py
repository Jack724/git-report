"""
AI 适配器抽象基类
定义统一的接口规范
"""
from abc import ABC, abstractmethod
from typing import Dict, Tuple
import time
from infrastructure.logger import get_logger

logger = get_logger()


class BaseAdapter(ABC):
    """AI 适配器抽象基类"""

    def __init__(self, system_prompt: str = "", user_prompt: str = "",
                 report_example: str = "", use_example: bool = False,
                 temperature: float = 0.7, prompt_template: str = ""):
        """
        初始化适配器

        Args:
            system_prompt: System Prompt (定义 AI 角色)
            user_prompt: User Prompt 模板 (包含 {commit_log} 和 {example} 占位符)
            report_example: 报告示例 (可选)
            use_example: 是否启用示例数据
            temperature: Temperature 参数 (0.0-2.0，控制生成随机性)
            prompt_template: 旧版 Prompt 模板 (向后兼容)
        """
        # 向后兼容: 如果使用旧版 prompt_template，则作为 user_prompt
        if prompt_template and not user_prompt:
            user_prompt = prompt_template

        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.report_example = report_example
        self.use_example = use_example
        self.temperature = temperature
        self.prompt_template = user_prompt  # 保留向后兼容
        self.last_usage = {}
        self.logger = logger

    @abstractmethod
    def generate_report(self, commit_summary: str) -> str:
        """
        生成报告

        Args:
            commit_summary: 提交摘要

        Returns:
            生成的报告文本

        Raises:
            Exception: API 调用失败
        """
        raise NotImplementedError

    def _build_final_prompt(self, commit_summary: str) -> str:
        """
        构建最终的 Prompt（替换占位符）- 向后兼容方法

        Args:
            commit_summary: 提交摘要

        Returns:
            替换占位符后的完整 Prompt
        """
        # 替换 {commit_log} 占位符
        prompt = self.user_prompt.replace('{commit_log}', commit_summary)

        # 处理 {example} 占位符
        if self.use_example and self.report_example and self.report_example.strip():
            # 使用指定格式：【示例】\n{example}
            example_text = f"\n\n【示例】\n{self.report_example.strip()}\n"
            prompt = prompt.replace('{example}', example_text)
        else:
            # 如果未启用或没有示例，移除 {example} 占位符
            prompt = prompt.replace('{example}', '')

        return prompt

    def _build_messages(self, commit_summary: str) -> list:
        """
        构建消息列表（包含 system 和 user 消息）

        Args:
            commit_summary: 提交摘要

        Returns:
            消息列表 [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        """
        messages = []

        # 添加 system 消息
        if self.system_prompt and self.system_prompt.strip():
            messages.append({
                "role": "system",
                "content": self.system_prompt.strip()
            })

        # 构建 user 消息内容
        user_content = self.user_prompt.replace('{commit_log}', commit_summary)

        # 处理 {example} 占位符
        if self.use_example and self.report_example and self.report_example.strip():
            # 使用指定格式：【示例】\n{example}
            example_text = f"\n\n【示例】\n{self.report_example.strip()}\n"
            user_content = user_content.replace('{example}', example_text)
        else:
            # 如果未启用或没有示例，移除 {example} 占位符
            user_content = user_content.replace('{example}', '')

        # 添加 user 消息
        messages.append({
            "role": "user",
            "content": user_content.strip()
        })

        return messages

    def get_token_usage(self) -> Dict[str, int]:
        """
        获取最后一次调用的 Token 用量

        Returns:
            包含 prompt_tokens, completion_tokens, total_tokens 的字典
        """
        return self.last_usage

    def test_connection(self) -> Tuple[bool, str]:
        """
        测试 API 连接是否正常

        Returns:
            (成功标志, 消息)
        """
        try:
            self.logger.info(f"[{self.platform_name}] 开始测试API连接")
            # 发送一个简单的测试请求
            response = self._send_test_request()
            self.logger.info(f"[{self.platform_name}] API连接测试成功")
            return True, f"连接成功! 平台: {self.platform_name}"
        except Exception as e:
            self.logger.error(f"[{self.platform_name}] API连接测试失败: {str(e)}")
            return False, f"连接失败: {str(e)}"

    @abstractmethod
    def _send_test_request(self) -> str:
        """
        发送测试请求

        Returns:
            测试响应结果

        Raises:
            Exception: 测试失败
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """
        平台名称

        Returns:
            平台显示名称
        """
        raise NotImplementedError

    def _mask_api_key(self, api_key: str) -> str:
        """
        脱敏API Key,只显示最后4位

        Args:
            api_key: 完整的API Key

        Returns:
            脱敏后的API Key
        """
        if not api_key or len(api_key) <= 4:
            return "****"
        return f"****{api_key[-4:]}"

    def _log_request_start(self, model: str, input_length: int, endpoint: str = ""):
        """
        记录请求开始日志

        Args:
            model: 模型名称
            input_length: 输入文本长度
            endpoint: API端点(可选)
        """
        self.logger.info(
            f"[{self.platform_name}] 开始生成报告 | 模型: {model} | 输入长度: {input_length}字符"
        )
        if endpoint:
            self.logger.debug(f"[{self.platform_name}] 请求端点: {endpoint}")

    def _log_request_params(self, **params):
        """
        记录请求参数

        Args:
            **params: 请求参数字典
        """
        # 过滤敏感信息
        safe_params = {}
        for key, value in params.items():
            if key in ['api_key', 'authorization']:
                safe_params[key] = self._mask_api_key(str(value))
            else:
                safe_params[key] = value

        self.logger.debug(f"[{self.platform_name}] 请求参数: {safe_params}")

    def _log_request_payload(self, payload: dict):
        """
        记录完整的请求负载（JSON payload）

        Args:
            payload: 请求负载字典
        """
        import json

        # 记录完整的请求负载，不做截断
        self.logger.info(f"[{self.platform_name}] 请求Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")

    def _log_response_data(self, response_data: dict):
        """
        记录完整的响应数据

        Args:
            response_data: API 响应的 JSON 数据
        """
        import json

        # 记录完整的响应数据，不做截断
        self.logger.info(f"[{self.platform_name}] 响应数据: {json.dumps(response_data, ensure_ascii=False, indent=2)}")

    def _log_request_success(self, status_code: int, duration: float, content_preview: str = ""):
        """
        记录请求成功日志

        Args:
            status_code: HTTP状态码
            duration: 请求耗时(秒)
            content_preview: 内容预览(可选)
        """
        self.logger.info(
            f"[{self.platform_name}] 请求成功 | 状态码: {status_code} | 耗时: {duration:.2f}秒"
        )

        # 记录Token使用情况
        if self.last_usage:
            total = self.last_usage.get('total_tokens', 0)
            prompt = self.last_usage.get('prompt_tokens', 0)
            completion = self.last_usage.get('completion_tokens', 0)
            self.logger.info(
                f"[{self.platform_name}] Token使用: 总计={total} (prompt={prompt}, completion={completion})"
            )

        # 记录内容预览
        if content_preview:
            preview = content_preview[:100] if len(content_preview) > 100 else content_preview
            self.logger.debug(
                f"[{self.platform_name}] 生成内容预览(前100字): {preview}..."
            )

    def _log_request_error(self, error_type: str, error_msg: str, status_code: int = None):
        """
        记录请求失败日志

        Args:
            error_type: 错误类型
            error_msg: 错误消息
            status_code: HTTP状态码(可选)
        """
        if status_code:
            self.logger.error(
                f"[{self.platform_name}] {error_type} | 状态码: {status_code} | 错误: {error_msg}"
            )
        else:
            self.logger.error(
                f"[{self.platform_name}] {error_type} | 错误: {error_msg}"
            )
