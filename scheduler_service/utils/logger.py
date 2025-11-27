import logging
import sys
from logging import Formatter, Logger, StreamHandler

from scheduler_service.config import Config

# 定义日志颜色
COLORS = {
    'DEBUG': '\033[36m',  # 青色
    'INFO': '\033[32m',   # 绿色
    'WARNING': '\033[33m',  # 黄色
    'ERROR': '\033[31m',    # 红色
    'CRITICAL': '\033[41m\033[37m',  # 红底白字
    'RESET': '\033[0m'      # 重置颜色
}


class ColoredFormatter(Formatter):
    """带颜色的日志格式化器"""

    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)

    def format(self, record):
        # 保存原始的消息格式
        original_fmt = self._fmt

        # 根据日志级别添加颜色
        levelname = record.levelname
        if levelname in COLORS:
            # 修改消息格式，添加颜色
            self._fmt = f"{COLORS[levelname]}{original_fmt}{COLORS['RESET']}"

        # 格式化日志记录
        result = super().format(record)

        # 恢复原始格式
        self._fmt = original_fmt

        return result


def get_logger(name: str = 'scheduler-service', level: int = None) -> Logger:
    """
    获取配置好的logger

    Args:
        name: logger名称，默认'scheduler-service'
        level: 日志级别，如果为None则从Config中读取

    Returns:
        配置好的Logger实例
    """
    # 确定日志级别
    if level is None:
        level = Config.LOG_LEVEL

    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加handler
    if not logger.handlers:
        # 创建handler，输出到控制台
        stream_handler = StreamHandler(sys.stdout)
        stream_handler.setLevel(level) # 现在使用正确的level值

        # 创建带颜色的formatter
        formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 给handler设置formatter
        stream_handler.setFormatter(formatter)

        # 给logger添加handler
        logger.addHandler(stream_handler)

    return logger


# 创建默认的logger实例
logger = get_logger()
