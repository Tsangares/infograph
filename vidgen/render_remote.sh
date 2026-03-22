#!/usr/bin/env bash
#
# Remote Remotion Render — syncs project to a remote host, renders, fetches MP4 back.
#
# Usage:
#   ./render_remote.sh <topic>               # auto-pick best host
#   ./render_remote.sh <topic> --host=llama  # force specific host
#   ./render_remote.sh <topic> --local       # force local render
#   ./render_remote.sh --list-hosts          # show available hosts
#
# Hosts are tried in priority order: llama (12 cores) > juno (8 cores) > local (4 cores)

set -euo pipefail

VIDGEN_DIR="$(cd "$(dirname "$0")" && pwd)"
REMOTION_DIR="$VIDGEN_DIR/remotion"
SSH_OPTS="-o IdentitiesOnly=yes -i $HOME/.ssh/id_ed25519 -o StrictHostKeyChecking=accept-new -o ConnectTimeout=5 -o BatchMode=yes"
REMOTE_BASE="~/tkk-render"

# Host definitions: name, ssh_target, cores
declare -A HOSTS_SSH=(
  [llama]="wil@10.0.0.99"
  [juno]="wil@10.0.0.111"
)
declare -A HOSTS_CORES=(
  [llama]=12
  [juno]=8
)
HOST_PRIORITY=(llama juno)

# ── Helpers ──────────────────────────────────────────────────

log()  { echo "  $*"; }
die()  { echo "  ERROR: $*" >&2; exit 1; }

ssh_cmd() {
  local target="$1"; shift
  ssh $SSH_OPTS "$target" "bash -c '$*'" 2>/dev/null
}

check_host() {
  local name="$1"
  local target="${HOSTS_SSH[$name]}"
  ssh_cmd "$target" "echo OK" >/dev/null 2>&1
}

list_hosts() {
  echo "  Available remote render hosts:"
  echo "  ───────────────────────────────"
  for name in "${HOST_PRIORITY[@]}"; do
    local target="${HOSTS_SSH[$name]}"
    local cores="${HOSTS_CORES[$name]}"
    if check_host "$name" 2>/dev/null; then
      echo "  ✓ $name ($target) — $cores cores — reachable"
    else
      echo "  ✗ $name ($target) — $cores cores — unreachable"
    fi
  done
  echo "  ───────────────────────────────"
  echo "  local (this machine) — $(nproc) cores — always available"
}

pick_host() {
  for name in "${HOST_PRIORITY[@]}"; do
    if check_host "$name" 2>/dev/null; then
      echo "$name"
      return 0
    fi
  done
  echo "local"
}

# ── Parse args ───────────────────────────────────────────────

TOPIC=""
FORCE_HOST=""
FORCE_LOCAL=false

for arg in "$@"; do
  case "$arg" in
    --host=*)   FORCE_HOST="${arg#--host=}" ;;
    --local)    FORCE_LOCAL=true ;;
    --list-hosts) list_hosts; exit 0 ;;
    --help|-h)  head -12 "$0" | tail -10; exit 0 ;;
    *)          TOPIC="$arg" ;;
  esac
done

if [[ -z "$TOPIC" ]]; then
  die "Usage: $0 <topic> [--host=llama|juno] [--local]"
fi

# Validate topic
MANIFEST="$REMOTION_DIR/src/manifests/${TOPIC}.json"
[[ -f "$MANIFEST" ]] || die "Manifest not found: $MANIFEST"

# Pick host
if $FORCE_LOCAL; then
  HOST="local"
elif [[ -n "$FORCE_HOST" ]]; then
  HOST="$FORCE_HOST"
  [[ -v "HOSTS_SSH[$HOST]" ]] || die "Unknown host: $HOST (known: ${!HOSTS_SSH[*]})"
  check_host "$HOST" || die "Host $HOST is unreachable"
else
  HOST=$(pick_host)
fi

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║  TKK Remote Render                   ║"
echo "  ╚══════════════════════════════════════╝"
log "Topic:  $TOPIC"
log "Host:   $HOST"

# ── Local render path ────────────────────────────────────────

if [[ "$HOST" == "local" ]]; then
  log "Rendering locally..."
  cd "$VIDGEN_DIR"
  exec npx tsx remotion/render.mts "$TOPIC"
fi

# ── Remote render path ───────────────────────────────────────

TARGET="${HOSTS_SSH[$HOST]}"
CORES="${HOSTS_CORES[$HOST]}"
log "Target: $TARGET ($CORES cores)"

# Step 1: Sync project to remote
log ""
log "Step 1/4: Syncing project to $HOST..."

# Rsync the remotion dir + needed vidgen files (exclude heavy stuff)
rsync -az --delete \
  --exclude='node_modules/' \
  --exclude='.git/' \
  --exclude='media/' \
  --exclude='previews/' \
  --exclude='*_final.mp4' \
  --exclude='*.pyc' \
  --exclude='__pycache__/' \
  --exclude='.venv/' \
  -e "ssh $SSH_OPTS" \
  "$REMOTION_DIR/" "$TARGET:$REMOTE_BASE/remotion/"

# Sync needed vidgen-level files (TTS audio, resolved JSON, .env)
rsync -az \
  -e "ssh $SSH_OPTS" \
  "$VIDGEN_DIR/tts_${TOPIC}.mp3" \
  "$TARGET:$REMOTE_BASE/" 2>/dev/null || true

rsync -az \
  -e "ssh $SSH_OPTS" \
  "$VIDGEN_DIR/${TOPIC}_resolved.json" \
  "$TARGET:$REMOTE_BASE/" 2>/dev/null || true

log "  Synced."

# Step 2: Install deps on remote (if needed)
log ""
log "Step 2/4: Checking remote dependencies..."

NEED_INSTALL=$(ssh_cmd "$TARGET" "
  if [[ -d $REMOTE_BASE/remotion/node_modules ]]; then
    echo NO
  else
    echo YES
  fi
")

if [[ "$NEED_INSTALL" == "YES" ]]; then
  log "  Installing node_modules on $HOST..."
  ssh_cmd "$TARGET" "cd $REMOTE_BASE/remotion && npm install --prefer-offline 2>&1" | while read line; do
    echo "    $line"
  done
  log "  Installed."
else
  log "  node_modules present."
fi

# Step 3: Render on remote
log ""
log "Step 3/4: Rendering on $HOST ($CORES cores)..."

# Build the render command — override concurrency based on host cores
ssh $SSH_OPTS "$TARGET" "bash -c '
  cd $REMOTE_BASE
  export REMOTION_CONCURRENCY=$CORES
  npx tsx remotion/render.mts $TOPIC 2>&1
'" | while IFS= read -r line; do
  echo "  [$HOST] $line"
done
RENDER_EXIT=${PIPESTATUS[0]}

if [[ $RENDER_EXIT -ne 0 ]]; then
  die "Remote render failed on $HOST (exit $RENDER_EXIT)"
fi

# Step 4: Fetch the final MP4 back
log ""
log "Step 4/4: Fetching ${TOPIC}_final.mp4 from $HOST..."

rsync -az \
  -e "ssh $SSH_OPTS" \
  "$TARGET:$REMOTE_BASE/${TOPIC}_final.mp4" \
  "$VIDGEN_DIR/${TOPIC}_final.mp4"

log "  Done: $VIDGEN_DIR/${TOPIC}_final.mp4"
log ""
log "  Render complete on $HOST ($CORES cores)"
echo ""
