#!/usr/bin/env bash
# Run the existing suites against a fresh local checkout; preserve all evidence.
set -Eeuo pipefail

if [[ ${1:-} == --help ]]; then
  cat <<'HELP'
Usage: bash scripts/validate_wsl.sh

Validates committed HEAD in a clean local clone under reports/runs/.
Requires Ubuntu WSL, Python 3.12, Node 22+, npm 10+, Docker, and free
loopback ports 8000/5173. Does not install OS packages or publish code.
Stops at the first failed stage; logs, status and the clone are retained.
HELP
  exit 0
fi
if (( $# )); then
  printf 'Unexpected argument: %s\n' "$1" >&2
  exit 2
fi

repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd -- "$repo"
for program in git python3.12 node npm docker; do
  command -v "$program" >/dev/null
done
if ! git diff --quiet || ! git diff --cached --quiet; then
  printf 'Tracked changes are uncommitted. Review and commit them before validating HEAD.\n' >&2
  exit 2
fi
source_commit=$(git rev-parse HEAD)
mkdir -p "$repo/reports/runs"
run_dir=$(mktemp -d "$repo/reports/runs/wsl-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
workspace="$run_dir/workspace"
mkdir -p "$run_dir/logs"
printf '%s\n' "$source_commit" > "$run_dir/source-commit.txt"
printf 'stage\texit_code\tfinished_utc\n' > "$run_dir/stages.tsv"
printf 'Evidence: %s\nSource commit: %s\n' "$run_dir" "$source_commit"
managed_services=0

finish() {
  local result=$?
  local stop_result=0
  trap - EXIT
  set +e
  if (( managed_services )); then
    (cd -- "$workspace" && python3.12 scripts/manage.py stop) > "$run_dir/logs/cleanup.log" 2>&1
    stop_result=$?
    if (( result == 0 && stop_result != 0 )); then result=$stop_result; fi
  fi
  printf '%s\n' "$result" > "$run_dir/exit-code.txt"
  if (( result == 0 )); then
    printf 'PASS: automatic WSL validation. Evidence: %s\n' "$run_dir"
  else
    printf 'FAIL: exit %s. Inspect %s/stages.tsv and logs/.\n' "$result" "$run_dir" >&2
  fi
  exit "$result"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

step() {
  local name=$1
  shift
  local result=0
  printf '\n[%s]' "$name"
  printf ' %q' "$@"
  printf '\n'
  "$@" > "$run_dir/logs/$name.log" 2>&1 || result=$?
  cat "$run_dir/logs/$name.log"
  printf '%s\t%s\t%s\n' "$name" "$result" "$(date -u +%FT%TZ)" >> "$run_dir/stages.tsv"
  if (( result != 0 )); then exit "$result"; fi
}

free_ports() {
  python3.12 - <<'PY'
import socket
for port in (8000, 5173):
    with socket.socket() as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(('127.0.0.1', port))
        except OSError as error:
            raise SystemExit(f'Port {port} unavailable: {error}. Stop its owner before rerunning.')
print('Ports 8000 and 5173 are free.')
PY
}

step 00-wsl python3.12 -c 'import platform; assert "microsoft" in platform.release().lower(), "Run inside WSL"; print(platform.platform())'
step 01-docker docker info --format '{{json .}}'
step 02-ports free_ports
step 03-clone git clone --no-hardlinks --no-checkout -- "$repo" "$workspace"
cd -- "$workspace"
step 04-checkout git checkout --detach "$source_commit"

# Only defaults from the tested commit; retain Docker client connection settings.
while IFS= read -r name; do unset "$name"; done < <(compgen -v | sed -n '/^PSEUDO_STUDIO_/p')
export PSEUDO_STUDIO_OCI_ENGINE=docker
export PSEUDO_STUDIO_DATA_DIR="$workspace/data"
export PSEUDO_STUDIO_DB_PATH="$workspace/data/projects.sqlite3"
export PSEUDO_STUDIO_ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
export CI=1

# Historical reports cannot be mistaken for outputs from this run.
if [[ -d reports ]]; then mv reports "$run_dir/historical-reports"; fi
mkdir reports
step 05-python python3.12 --version
step 06-node node --version
step 07-npm npm --version
step 08-bootstrap python3.12 scripts/manage.py bootstrap
step 09-verify python3.12 scripts/manage.py verify
step 10-precommit .venv/bin/pre-commit run --all-files
step 11-lint .venv/bin/ruff check backend scripts
step 12-format .venv/bin/ruff format --check backend scripts
step 13-pytest .venv/bin/pytest -q --junitxml=reports/pytest.xml --cov-report=xml:reports/coverage.xml --cov-report=term-missing
step 14-official python3.12 scripts/run_official_acceptance.py
step 15-official-records python3.12 - <<'PY'
import json
from pathlib import Path
fixtures = json.loads(Path('examples/official-cases.json').read_text())
report = json.loads(Path('reports/acceptance-results.json').read_text())
expected = {(case['id'], target) for case in fixtures['cases'] for target in ('python', 'javascript')}
actual = {(run['case_id'], run['target']) for run in report['runs']}
assert len(expected) == 30 and actual == expected
assert report['total'] == report['passed'] == len(report['runs']) == 30 and report['failed'] == 0
assert all(run['passed'] and run['status'] == 'completed' and run['exit_code'] == 0
           and not run['stderr'] and run['actual_stdout'] == run['expected_stdout']
           and len(run['source_hash']) == len(run['artifact_hash']) == 64
           and run['runtime_version'] and run['duration_ms'] >= 0 for run in report['runs'])
print('30 distinct official case/target pairs passed with runtime and hash evidence.')
PY
step 16-benchmark python3.12 scripts/benchmark_compile.py
step 17-build npm --prefix frontend run build
step 18-e2e-ports free_ports
# Playwright owns its servers. Never reuse an application from another checkout.
step 19-e2e npm --prefix frontend run test:e2e -- --workers=1 --retries=0
step 20-start-ports free_ports
managed_services=1
step 21-start python3.12 scripts/manage.py start
step 22-smoke python3.12 scripts/manage.py smoke
step 23-backup python3.12 scripts/manage.py backup --output reports/projects-backup.sqlite3
step 24-stop python3.12 scripts/manage.py stop
managed_services=0
step 25-stopped-ports free_ports
step 26-python-audit .venv/bin/pip-audit --strict --no-deps --disable-pip -r requirements.lock --format json -o reports/python-dependency-audit.json
step 27-npm-audit npm --prefix frontend audit --audit-level=moderate --json
cp "$run_dir/logs/27-npm-audit.log" reports/npm-dependency-audit.json
step 28-source-unchanged git diff --exit-code -- backend scripts frontend examples sandbox requirements.lock pyproject.toml
step 29-hashes python3.12 - <<'PY'
import hashlib
from pathlib import Path
roots = [Path('reports'), Path('frontend/playwright-report'), Path('frontend/test-results')]
lines = []
for root in roots:
    for file in sorted(root.rglob('*')):
        if file.is_file() and file.name != 'SHA256SUMS':
            lines.append(f'{hashlib.sha256(file.read_bytes()).hexdigest()}  {file.as_posix()}')
Path('reports/SHA256SUMS').write_text('\n'.join(lines) + '\n')
print(f'Hashed {len(lines)} evidence files; paths relative to the clean workspace.')
PY
printf 'Manual WCAG, remote CI and other platforms still require their own evidence.\n'
