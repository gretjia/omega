"""
OMEGA Node Paths Configuration
================================
Auto-detects current host and provides the correct paths.
Single source of truth for all node-specific paths.

Usage:
    from configs.node_paths import get_node_config
    cfg = get_node_config()

    print(cfg.raw_root)        # /omega_pool/raw_7z_archives (linux)
    print(cfg.stage1_output)   # /omega_pool/parquet_data/v62_base_l1/host=linux1
    print(cfg.stage2_output)   # /omega_pool/parquet_data/v62_feature_l2/host=linux1
    print(cfg.cache_dir)       # /home/zepher/framing_cache
    print(cfg.repo_root)       # /home/zepher/work/Omega_vNext

    # Or force a node:
    cfg = get_node_config(node="windows1")
"""
from __future__ import annotations

import os
import platform
import socket
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

_REPO_ROOT = Path(__file__).resolve().parent.parent
_REGISTRY_PATH = _REPO_ROOT / "handover" / "ops" / "HOSTS_REGISTRY.yaml"


@dataclass
class NodeConfig:
    """All paths and metadata for a single cluster node."""
    node_name: str
    hostname: str
    os_type: str
    role: str
    repo_root: str
    ssh_alias: Optional[str] = None
    git_remote: Optional[str] = None

    # Data paths
    raw_root: Optional[str] = None
    stage1_output: Optional[str] = None
    stage2_output: Optional[str] = None
    cache_dir: Optional[str] = None
    polars_temp_dir: Optional[str] = None
    log_dir: Optional[str] = None


# ── Static node definitions ──
# These are the canonical definitions. HOSTS_REGISTRY.yaml is the source
# for SSH aliases and probes; these are the path configs.

_NODE_CONFIGS = {
    "controller": NodeConfig(
        node_name="controller",
        hostname="zephrymac-studio",
        os_type="darwin",
        role="controller",
        repo_root=str(_REPO_ROOT),
        log_dir=str(_REPO_ROOT / "audit"),
    ),
    "linux1": NodeConfig(
        node_name="linux1",
        hostname="zepher-linux",
        os_type="linux",
        role="worker stage1/stage2",
        repo_root="/home/zepher/work/Omega_vNext",
        ssh_alias="linux1-lx",
        git_remote="linux",
        raw_root="/omega_pool/raw_7z_archives",
        stage1_output="/omega_pool/parquet_data/v62_base_l1/host=linux1",
        stage2_output="/omega_pool/parquet_data/latest_feature_l2/host=linux1",
        cache_dir="/home/zepher/framing_cache",
        polars_temp_dir="/home/zepher/framing_cache",
        log_dir="/home/zepher/work/Omega_vNext/audit",
    ),
    "windows1": NodeConfig(
        node_name="windows1",
        hostname="DESKTOP-41JIDL2",
        os_type="windows",
        role="worker stage1/stage2",
        repo_root=r"D:\work\Omega_vNext",
        ssh_alias="windows1-w1",
        git_remote="windows",
        raw_root=r"D:\Omega_level2_raw",
        stage1_output=r"D:\Omega_frames\v62_base_l1\host=windows1",
        stage2_output=r"D:\Omega_frames\latest_feature_l2\host=windows1",
        cache_dir=r"D:\Omega_cache",
        polars_temp_dir=r"D:\Omega_cache",
        log_dir=r"D:\work\Omega_vNext\audit",
    ),
}

# Hostname fragments for auto-detection
_HOSTNAME_PATTERNS = {
    "zephrymac": "controller",
    "zepher-linux": "linux1",
    "DESKTOP-41JIDL2": "windows1",
}


def _detect_node() -> str:
    """Auto-detect current node from hostname."""
    hostname = socket.gethostname().lower()

    for pattern, node_name in _HOSTNAME_PATTERNS.items():
        if pattern.lower() in hostname:
            return node_name

    # Fallback: detect by OS
    system = platform.system().lower()
    if system == "darwin":
        return "controller"
    elif system == "linux":
        return "linux1"
    elif system == "windows":
        return "windows1"

    return "controller"  # ultimate fallback


def get_node_config(node: Optional[str] = None) -> NodeConfig:
    """
    Get configuration for the specified or current node.

    Args:
        node: Node name ("controller", "linux1", "windows1").
              If None, auto-detects from hostname.

    Returns:
        NodeConfig with all paths for that node.
    """
    if node is None:
        node = _detect_node()

    if node not in _NODE_CONFIGS:
        available = list(_NODE_CONFIGS.keys())
        raise ValueError(f"Unknown node '{node}'. Available: {available}")

    return _NODE_CONFIGS[node]


def get_all_nodes() -> dict[str, NodeConfig]:
    """Return all node configs."""
    return dict(_NODE_CONFIGS)


def get_worker_nodes() -> dict[str, NodeConfig]:
    """Return only worker node configs (excludes controller)."""
    return {k: v for k, v in _NODE_CONFIGS.items() if k != "controller"}


# ── Convenience: module-level auto-detect ──
# Import this for quick access: from configs.node_paths import NODE
NODE = get_node_config()
