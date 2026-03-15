import os
import shutil


def del_filedir(path: str) -> None:
    """
    清空目录（删除后重建），用于在每次推理前清空旧结果
    :param path: 目录路径字符串
    """
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)


def ensure_dir(path: str) -> None:
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)
