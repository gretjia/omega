#!/bin/bash
# Sync Stage1 Parquet files between Linux and Windows via SMB (2.5G LAN)
# Assumes Windows Drive D is mounted at /mnt/windows_d on Linux.
# Usage: bash sync_l1_smb.sh

set -e

LINUX_L1="/omega_pool/parquet_data/latest_base_l1"
WIN_MOUNT="/mnt/windows_d/latest_base_l1"

echo "=== Syncing Linux -> Windows ==="
# We push the host=linux1 files to the Windows drive so Windows can have the full set
sudo mkdir -p "${WIN_MOUNT}/host=linux1"
sudo rsync -av --inplace "${LINUX_L1}/host=linux1/" "${WIN_MOUNT}/host=linux1/"

echo "=== Syncing Windows -> Linux ==="
# We pull the host=windows1 files to the Linux drive so Linux can have the full set
sudo mkdir -p "${LINUX_L1}/host=windows1"
sudo chown zepher:zepher "${LINUX_L1}/host=windows1"
sudo rsync -av --inplace "${WIN_MOUNT}/host=windows1/" "${LINUX_L1}/host=windows1/"

echo "Sync Complete!"
