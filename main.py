import os
import json

def read_config(config_file):
    """读取 JSON 配置文件"""
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"配置文件 {config_file} 不存在！")
    with open(config_file, 'r') as f:
        config = json.load(f)
    pairs = config.get("pairs")
    history_file = config.get("history_file")
    if not pairs or not history_file:
        raise ValueError("配置文件中必须包含 'pairs' 和 'history_file'")
    return pairs, history_file

def read_history(history_file):
    """读取 history 文件中的记录"""
    if not os.path.exists(history_file):
        return set()
    with open(history_file, 'r') as f:
        return set(line.strip() for line in f)

def write_history(history_file, paths):
    """将新路径写入 history 文件"""
    with open(history_file, 'a') as f:
        for path in paths:
            f.write(path + '\n')

def create_hard_links(source_dir, dest_dir, history, new_paths):
    """创建硬链接并记录新路径"""
    for root, _, files in os.walk(source_dir):
        for file in files:
            source_path = os.path.join(root, file)
            relative_path = os.path.relpath(source_path, source_dir)
            dest_path = os.path.join(dest_dir, relative_path)

            # 如果文件路径已存在于 history 中，跳过
            if source_path in history:
                continue

            # 创建目标目录（如果不存在）
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            # 创建硬链接
            try:
                os.link(source_path, dest_path)
                print(f"硬链接创建成功: {source_path} -> {dest_path}")
                new_paths.add(source_path)
            except OSError as e:
                print(f"创建硬链接失败: {source_path} -> {dest_path}, 错误: {e}")

def process_pairs(pairs, history_file):
    """处理多组输入输出配对"""
    # 读取历史记录
    history = read_history(history_file)
    new_paths = set()

    # 遍历每组配对
    for pair in pairs:
        source_dir = pair.get("source_directory")
        dest_dir = pair.get("destination_directory")
        if not source_dir or not dest_dir:
            print("配置中的 source_directory 或 destination_directory 缺失，跳过此配对")
            continue
        print(f"处理配对: {source_dir} -> {dest_dir}")
        create_hard_links(source_dir, dest_dir, history, new_paths)

    # 更新历史文件
    if new_paths:
        write_history(history_file, new_paths)
        print("历史文件已更新。")
    else:
        print("没有新文件需要处理。")

if __name__ == "__main__":
    # 配置文件路径
    config_file_path = "config.json"

    # 从配置文件中读取路径配对和历史文件
    try:
        pairs, history_file_path = read_config(config_file_path)
        process_pairs(pairs, history_file_path)
    except Exception as e:
        print(f"发生错误: {e}")
