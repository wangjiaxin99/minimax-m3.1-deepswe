"""Health/model check plus a 100-token smoke call; excluded from benchmark scores."""
import argparse
import json
import os
from pathlib import Path
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    base = os.environ["OPENAI_BASE_URL"].rstrip("/")
    with urllib.request.urlopen(base.removesuffix("/v1") + "/health", timeout=15) as response:
        assert response.status == 200
    with urllib.request.urlopen(base + "/models", timeout=15) as response:
        models = json.load(response)
    assert os.environ["MODEL_PATH"] in {m["id"] for m in models["data"]}, models
    payload = {"model": os.environ["MODEL_PATH"], "input": "What is the capital of China? and how many cities in China?",
               "max_output_tokens": 100, "temperature": 0}
    request = urllib.request.Request(base + "/responses", data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json", "Authorization": "Bearer EMPTY"})
    with urllib.request.urlopen(request, timeout=180) as response:
        result = json.load(response)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"models": models, "smoke": result}, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
