"""
OpenAI API 适配器
支持 OpenAI GPT 系列模型
"""
import requests
import time
from infrastructure.adapters.base import BaseAdapter


class OpenAIAdapter(BaseAdapter):
    """OpenAI API 适配器"""

    BASE_URL = "https://api.openai.com/v1"
    DEFAULT_MODEL = "gpt-4o-mini"

    def __init__(self, api_key: str, model: str = None, base_url: str = None,
                 system_prompt: str = "", user_prompt: str = "", report_example: str = "",
                 use_example: bool = False, temperature: float = 0.7, prompt_template: str = ""):
        """
        初始化 OpenAI 适配器

        Args:
            api_key: OpenAI API Key
            model: 模型名称 (默认: gpt-4o-mini)
            base_url: API 基础地址 (可选,默认使用官方地址)
            system_prompt: System Prompt (定义 AI 角色)
            user_prompt: User Prompt 模板
            report_example: 报告示例 (可选)
            use_example: 是否启用示例数据
            temperature: Temperature 参数 (0.0-2.0)
            prompt_template: 旧版 Prompt 模板 (向后兼容)
        """
        super().__init__(system_prompt, user_prompt, report_example, use_example, temperature, prompt_template)
        self.api_key = api_key
        self.model = model or self.DEFAULT_MODEL
        self.base_url = (base_url or self.BASE_URL).rstrip('/')

    @property
    def platform_name(self) -> str:
        return "OpenAI GPT"

    def generate_report(self, commit_summary: str) -> str:
        """
        调用 OpenAI API 生成报告

        Args:
            commit_summary: 提交摘要

        Returns:
            生成的报告文本

        Raises:
            Exception: API 调用失败
        """
        if not self.api_key:
            raise ValueError("API Key 未配置")

        # 构建消息列表 (包含 system 和 user 消息)
        messages = self._build_messages(commit_summary)

        # 构建请求
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature
        }

        api_endpoint = f"{self.base_url}/chat/completions"

        # 记录请求开始
        self._log_request_start(
            model=self.model,
            input_length=len(commit_summary),
            endpoint=api_endpoint
        )
        self._log_request_params(
            model=self.model,
            temperature=0.7,
            authorization=f"Bearer {self.api_key}"
        )

        # 记录完整的请求 Payload
        self._log_request_payload(payload)

        start_time = time.time()

        try:
            # 发送请求
            response = requests.post(
                api_endpoint,
                headers=headers,
                json=payload,
                timeout=60
            )

            duration = time.time() - start_time

            # 检查响应
            if response.status_code != 200:
                error_msg = f"API 请求失败: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f", 详情: {error_detail}"
                except:
                    error_msg += f", 响应: {response.text}"

                self._log_request_error(
                    error_type="API请求失败",
                    error_msg=error_msg,
                    status_code=response.status_code
                )
                raise Exception(error_msg)

            # 解析响应
            result = response.json()

            # 记录完整的响应数据
            self._log_response_data(result)

            if 'choices' not in result or len(result['choices']) == 0:
                error_msg = f"API 响应格式错误: {result}"
                self._log_request_error(
                    error_type="响应格式错误",
                    error_msg=error_msg,
                    status_code=response.status_code
                )
                raise Exception(error_msg)

            # 保存 Token 用量
            self.last_usage = result.get('usage', {})

            report = result['choices'][0]['message']['content'].strip()

            # 记录请求成功
            self._log_request_success(
                status_code=response.status_code,
                duration=duration,
                content_preview=report
            )

            return report

        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            error_msg = f"请求超时(耗时{duration:.2f}秒),请稍后重试"
            self._log_request_error(error_type="请求超时", error_msg=error_msg)
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求异常: {str(e)}"
            self._log_request_error(error_type="网络异常", error_msg=error_msg)
            raise Exception(f"API 请求失败: {str(e)}")
        except Exception as e:
            if "API 请求" in str(e) or "API 响应" in str(e) or "请求超时" in str(e):
                raise
            error_msg = str(e)
            self._log_request_error(error_type="生成报告失败", error_msg=error_msg)
            raise Exception(f"生成报告失败: {error_msg}")

    def _send_test_request(self) -> str:
        """
        发送测试请求验证连接

        Returns:
            测试响应

        Raises:
            Exception: 测试失败
        """
        if not self.api_key:
            raise ValueError("API Key 未配置")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 5
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )

        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

        return response.json()['choices'][0]['message']['content']
