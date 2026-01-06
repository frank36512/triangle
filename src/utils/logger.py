"""
日志模块
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logger(name: str = "ad_tool", log_dir: str = "./logs") -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_dir: 日志文件目录
        
    Returns:
        配置好的日志记录器
    """
    # 创建日志目录
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 文件处理器 - 使用 RotatingFileHandler
    # maxBytes=1MB, backupCount=0 (超过1MB后清空重写)
    log_file = os.path.join(log_dir, "app.log")
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=1024*1024,  # 1MB
        backupCount=0,       # 不保留备份，直接清空
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 格式化器 - 增加文件名、行号、函数名等详细信息
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# 创建全局日志记录器
logger = setup_logger()
