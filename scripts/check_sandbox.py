"""Non-benchmark check of native Pier proxy networks and daemon init.

Requires a transport-only HTTP fixture behind the sandbox's port-443 relay.
Creates only synthetic containers, never invokes a model or a DeepSWE task.
"""
import json
import os
from pathlib import Path
import subprocess


def main():
    from pier.environments.agent_setup import write_docker_proxy_compose, proxy_environment
    from pier.models.agent.network import NetworkAllowlist
    base = os.environ["OPENAI_BASE_URL"].removesuffix("/v1")
    host = base.split("//", 1)[1].split(":", 1)[0]
    directory = Path(os.environ["REPO_DIR"]) / "state/network-check"
    directory.mkdir(parents=True, exist_ok=True)
    compose = directory / "compose.json"
    token = "transport-fixture-only"
    write_docker_proxy_compose(path=compose, proxy_dir=directory / "proxy",
                               allowlist=NetworkAllowlist(domains=[host]), token=token)
    config = json.loads(compose.read_text())
    config["services"]["main"].update({"image": "curlimages/curl:8.17.0", "entrypoint": [],
                                         "command": ["sh", "-c", "sleep 600"]})
    compose.write_text(json.dumps(config, indent=2))
    command = ["docker", "compose", "-p", "minimax-repro-network-check", "-f", str(compose)]
    try:
        subprocess.run(command + ["up", "-d", "--build", "--wait"], check=True)
        proxy = proxy_environment(token, "pier-egress-proxy")["HTTP_PROXY"]
        subprocess.run(command + ["exec", "-T", "main", "curl", "-fsS", "--max-time", "15",
                                  "--proxy", proxy, "--noproxy", "", base + "/health"], check=True)
        denied = subprocess.run(command + ["exec", "-T", "main", "curl", "-sS", "--max-time", "15",
                                           "--proxy", proxy, "--noproxy", "", "-o", "/dev/null", "-w", "%{http_code}",
                                           "http://example.com/"], capture_output=True, text=True)
        assert denied.stdout.strip() == "403", denied
        direct = subprocess.run(command + ["exec", "-T", "main", "curl", "-sS", "--max-time", "5",
                                           "--noproxy", "*", "http://1.1.1.1/"], capture_output=True, text=True)
        assert direct.returncode != 0, "Synthetic agent unexpectedly has direct internet access"
        processes = subprocess.check_output(command + ["exec", "-T", "main", "ps"], text=True)
        assert "docker-init" in processes, processes
        print("PASS: local proxy allowed, public host denied, direct egress blocked, init=true")
    finally:
        subprocess.run(command + ["down", "--remove-orphans"], check=True)


if __name__ == "__main__":
    main()
