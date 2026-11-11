"""Apply only the reviewed PR63125 runtime hunk; reject unknown source hashes."""
import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile

ORIGINAL = "3a3179009acd47f896b12fd805c08986bea538764a584db918582fdcc5a914d1"
PATCHED = "3f3397675af6596964daf974ee3b22d10996d0ebc70a4c3b30cad0e78f8ac830"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--patch", type=Path, required=True)
    args = parser.parse_args()
    import vllm
    relative = Path("vllm/model_executor/layers/quantization/quark/quark_moe.py")
    target = Path(vllm.__file__).parent.parent / relative
    actual = hashlib.sha256(target.read_bytes()).hexdigest()
    if actual == PATCHED:
        print("PR63125 already applied:", actual)
        return
    if actual != ORIGINAL:
        raise RuntimeError("Unexpected quark_moe.py; refusing to patch: " + actual)
    blocks = args.patch.read_text().split("diff --git ")[1:]
    block = next(b for b in blocks if b.splitlines()[0] == f"a/{relative} b/{relative}")
    with tempfile.TemporaryDirectory() as directory:
        candidate = Path(directory) / relative
        candidate.parent.mkdir(parents=True)
        shutil.copyfile(target, candidate)
        subprocess.run(["patch", "--fuzz=0", "-p1", "-d", directory],
                       input="diff --git " + block, text=True, check=True)
        if hashlib.sha256(candidate.read_bytes()).hexdigest() != PATCHED:
            raise RuntimeError("Patched source differs from reviewed PR63125")
        target.write_bytes(candidate.read_bytes())
    print("Applied PR63125:", PATCHED)


if __name__ == "__main__":
    main()
