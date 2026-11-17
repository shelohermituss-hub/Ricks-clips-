"""RunPod control for RicksClips GPU renders (GraphQL API https://api.runpod.io/graphql), 2026-11-17.
    python scripts/runpod/pod.py create <episode path from the skill root> [--gpu "NVIDIA GeForce RTX 4090"] [--branch <git branch>]
    python scripts/runpod/pod.py status <podId>
    python scripts/runpod/pod.py delete <podId>
Auth: header "Authorization: Bearer $RUNPOD_API_KEY". In Claude Code Web the key is a Network Secret for api.runpod.io that the
proxy injects (RUNPOD_API_KEY may then be the placeholder 'proxy-injected'). The pod clones this public repository, runs
scripts/runpod/render_pod.sh, and publishes its status at https://<podId>-8000.proxy.runpod.net/<pub_key>/status.json."""
import json, os, sys, secrets, urllib.request
API = "https://api.runpod.io/graphql"
REPO = "https://github.com/shelohermituss-hub/Ricks-clips-.git"
def gql(q, v=None):
    req = urllib.request.Request(API, json.dumps({"query": q, "variables": v or {}}).encode(), {"content-type": "application/json", "Authorization": "Bearer " + os.environ.get("RUNPOD_API_KEY", "proxy-injected")})
    r = json.load(urllib.request.urlopen(req, timeout=120))
    if r.get("errors"): raise SystemExit("RunPod API error: %s" % json.dumps(r["errors"])[:800])
    return r["data"]
a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
if a[0] == "create":
    ep, gpu, br, key = a[1], opt("--gpu", "NVIDIA GeForce RTX 4090"), opt("--branch", "main"), secrets.token_hex(16)
    boot = ("apt-get update -qq && apt-get install -y -qq git ca-certificates >/dev/null 2>&1; git clone -q --depth 1 -b %s %s /root/repo "
            "&& bash /root/repo/.claude/skills/ricks-clips/scripts/runpod/%s; sleep infinity") % (br, REPO, "gpu_diag.sh" if "--diag" in a else "render_pod.sh")
    inp = {"cloudType": opt("--cloud", "ALL"), "gpuCount": 1, "volumeInGb": 0, "containerDiskInGb": 60, "minVcpuCount": 8, "minMemoryInGb": 30,
           "gpuTypeId": gpu, "name": "ricksclips-diag" if "--diag" in a else "ricksclips-render", "imageName": opt("--image", "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04"),
           "dockerArgs": "bash -c '%s'" % boot, "ports": "8000/http", "volumeMountPath": "/workspace",
           "env": [{"key": "RICKCLIPS_EPISODE", "value": ep}, {"key": "RICKCLIPS_PUB_KEY", "value": key}, {"key": "RICKCLIPS_MAX_HOURS", "value": opt("--max-hours", "3")},
                   {"key": "NVIDIA_DRIVER_CAPABILITIES", "value": "all"}]}
    d = gql("mutation($i: PodFindAndDeployOnDemandInput) { podFindAndDeployOnDemand(input: $i) { id name desiredStatus costPerHr machine { gpuDisplayName } } }", {"i": inp})["podFindAndDeployOnDemand"]
    d["pub_key"] = key; d["status_url"] = "https://%s-8000.proxy.runpod.net/%s/status.json" % (d["id"], key); print(json.dumps(d))
elif a[0] == "status":
    print(json.dumps(gql("query($i: PodFilter) { pod(input: $i) { id name desiredStatus lastStatusChange costPerHr uptimeSeconds: runtime { uptimeInSeconds } } }", {"i": {"podId": a[1]}})["pod"]))
elif a[0] == "delete":
    gql("mutation($i: PodTerminateInput!) { podTerminate(input: $i) }", {"i": {"podId": a[1]}}); print(json.dumps({"deleted": a[1]}))
    left = [p["id"] for p in gql("query { myself { pods { id } } }")["myself"]["pods"]]; print(json.dumps({"pods_left": left}))
