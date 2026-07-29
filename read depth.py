from pathlib import Path

import numpy as np


# 直接在这里设置要遍历的场景名，或填写完整目录路径。
SCENE = "holes_dry_30p"


def find_depth_files(root: Path):
    return sorted(p for p in root.rglob("*.npy") if p.is_file())


def resolve_depth_root(scene_or_path: str) -> Path:
    input_path = Path(scene_or_path)
    if input_path.exists() and input_path.is_dir():
        if input_path.name != "depth" and (input_path / "depth").is_dir():
            return input_path / "depth"
        return input_path

    scene_dir = Path("output") / scene_or_path
    if (scene_dir / "depth").is_dir():
        return scene_dir / "depth"
    if scene_dir.is_dir():
        return scene_dir

    available_scenes = sorted(
        p.name for p in Path("output").iterdir() if p.is_dir() and (p / "depth").is_dir()
    )
    raise FileNotFoundError(
        f"找不到场景或目录: {scene_or_path}. 可用场景: {', '.join(available_scenes)}"
    )


def main():
    root = resolve_depth_root(SCENE)

    depth_files = find_depth_files(root)
    if not depth_files:
        print(f"在目录 {root} 下未找到 .npy 深度图")
        return

    global_min = None
    global_max = None
    global_min_file = None
    global_max_file = None
    total_sum = 0.0
    total_count = 0
    file_means = []
    file_medians = []

    for fp in depth_files:
        depth = np.load(fp)
        min_val = float(np.min(depth))
        max_val = float(np.max(depth))
        median_val = float(np.median(depth))
        mean_val = float(np.mean(depth))
        rel = fp.relative_to(root)
        print(f"{rel}: min={min_val}, max={max_val}, median={median_val}, mean={mean_val}")

        total_sum += float(np.sum(depth, dtype=np.float64))
        total_count += int(depth.size)
        file_means.append(mean_val)
        file_medians.append(median_val)

        if global_min is None or min_val < global_min:
            global_min = min_val
            global_min_file = rel
        if global_max is None or max_val > global_max:
            global_max = max_val
            global_max_file = rel

    print("=" * 80)
    print(f"总文件数: {len(depth_files)}")
    print(f"全局最小值: {global_min} (文件: {global_min_file})")
    print(f"全局最大值: {global_max} (文件: {global_max_file})")
    print(f"全局平均值(所有像素): {total_sum / total_count}")
    print(f"按帧平均值(每帧mean再平均): {float(np.mean(file_means))}")
    print(f"按帧中位数(每帧median再平均): {float(np.mean(file_medians))}")


if __name__ == "__main__":
    main()