"""Pull the task-declared prebuilt images into the dedicated daemon; no task edits."""
import os
from pathlib import Path
import subprocess
import tomllib


def main():
    tasks = Path(os.environ["TASKS_DIR"])
    images = set()
    for file in tasks.glob("*/task.toml"):
        image = tomllib.loads(file.read_text()).get("environment", {}).get("docker_image")
        if image:
            images.add(image)
    if not images:
        raise RuntimeError("No task images found")
    print(f"Pulling {len(images)} task images. Agent/verifier image builds remain separate.", flush=True)
    for image in sorted(images):
        subprocess.run(["docker", "pull", image], check=True)


if __name__ == "__main__":
    main()
