#!/bin/bash
# VPN check script for QA Test Automation Framework
# Purpose: verify that a VPN is connected when required. Supports multiple clients and fallbacks.

set -o errexit
set -o nounset
set -o pipefail

# Behavior control via environment variables:
# - VPN_REQUIRED: "true" to enforce VPN connectivity (default: "true" in CI, else optional)
# - VPN_CLIENT: preferred client binary to use (e.g., nmcli, scutil, nordvpn, openvpn, wg, tailscale, expressvpn, protonvpn)
# - VPN_NAME: friendly VPN name for messages or profile name for some clients
# - VPN_INTERFACE: specific interface to verify (e.g., tun0, wg0)
# - VPN_SUBNET: CIDR or subnet hint to check in routing table (e.g., 10.0.0.0/8)

VPN_REQUIRED=${VPN_REQUIRED:-"true"}
VPN_CLIENT=${VPN_CLIENT:-""}
VPN_NAME=${VPN_NAME:-"corporate VPN"}
VPN_INTERFACE=${VPN_INTERFACE:-""}
VPN_SUBNET=${VPN_SUBNET:-""}

if [ "${VPN_REQUIRED}" != "true" ]; then
    echo "VPN check skipped - VPN not required for this environment"
    exit 0
fi

autodetect_client() {
    local candidates=(
        "nmcli"      # NetworkManager (Linux)
        "scutil"     # macOS Network Configuration
        "nordvpn"
        "openvpn"
        "wg"         # WireGuard
        "tailscale"
        "expressvpn"
        "protonvpn"
    )
    for c in "${candidates[@]}"; do
        if command -v "$c" >/dev/null 2>&1; then
            echo "$c"
            return 0
        fi
    done
    echo ""
}

is_connected_by_interface() {
    local iface="$1"
    if [ -z "$iface" ]; then
        return 1
    fi
    if command -v ip >/dev/null 2>&1; then
        ip link show "$iface" >/dev/null 2>&1 && return 0 || return 1
    elif command -v ifconfig >/dev/null 2>&1; then
        ifconfig "$iface" >/dev/null 2>&1 && return 0 || return 1
    else
        return 1
    fi
}

is_connected_by_route() {
    local subnet="$1"
    if [ -z "$subnet" ]; then
        return 1
    fi
    if command -v ip >/dev/null 2>&1; then
        ip route show | grep -q "$subnet" && return 0 || return 1
    elif command -v route >/dev/null 2>&1; then
        route -n | grep -q "$subnet" && return 0 || return 1
    else
        return 1
    fi
}

is_connected_by_client() {
    local client="$1"
    case "$client" in
        nmcli)
            nmcli -t -f NAME,TYPE,DEVICE connection show --active | grep -iq "vpn" && return 0 || return 1
            ;;
        scutil)
            # macOS: if VPN_NAME provided, use it; else check any Connected VPN service
            if [ -n "$VPN_NAME" ]; then
                scutil --nc show "$VPN_NAME" 2>/dev/null | grep -iq "Connected" && return 0 || return 1
            else
                # List services and check any connected
                while IFS= read -r line; do
                    local svc
                    svc=$(echo "$line" | sed 's/.*\: //')
                    scutil --nc show "$svc" 2>/dev/null | grep -iq "Connected" && return 0 || true
                done < <(scutil --nc list | grep -iE "connected|connected\)|vpn")
                return 1
            fi
            ;;
        nordvpn)
            nordvpn status 2>/dev/null | grep -iq "Status: Connected" && return 0 || return 1
            ;;
        openvpn)
            # Heuristic: presence of tun/tap interface
            if command -v ip >/dev/null 2>&1; then
                ip link show | grep -iqE "\b(tun|tap)[0-9]*\b" && return 0 || return 1
            else
                ifconfig 2>/dev/null | grep -iqE "\b(tun|tap)[0-9]*\b" && return 0 || return 1
            fi
            ;;
        wg)
            wg show 2>/dev/null | grep -iq "interface" && return 0 || return 1
            ;;
        tailscale)
            tailscale status 2>/dev/null | grep -iq "Connected" && return 0 || return 1
            ;;
        expressvpn)
            expressvpn status 2>/dev/null | grep -iq "Connected" && return 0 || return 1
            ;;
        protonvpn)
            protonvpn status 2>/dev/null | grep -iq "Status: Connected" && return 0 || return 1
            ;;
        *)
            return 1
            ;;
    esac
}

# Determine client if not explicitly set
if [ -z "$VPN_CLIENT" ]; then
    VPN_CLIENT="$(autodetect_client)"
fi

# Try checks in order of specificity: interface -> route -> client
if is_connected_by_interface "$VPN_INTERFACE"; then
    echo "VPN connected (interface '${VPN_INTERFACE}' is up)"
    exit 0
fi

if is_connected_by_route "$VPN_SUBNET"; then
    echo "VPN connected (route for '${VPN_SUBNET}' present)"
    exit 0
fi

if [ -n "$VPN_CLIENT" ] && command -v "$VPN_CLIENT" >/dev/null 2>&1; then
    if is_connected_by_client "$VPN_CLIENT"; then
        echo "VPN connected via ${VPN_CLIENT}${VPN_NAME:+ to ${VPN_NAME}}"
        exit 0
    fi
else
    echo "Note: No known VPN client found; relying on interface/route checks only."
fi

echo "VPN not connected${VPN_NAME:+ to ${VPN_NAME}}"
echo "Please connect to ${VPN_NAME} before running CI jobs or local runners."
exit 1