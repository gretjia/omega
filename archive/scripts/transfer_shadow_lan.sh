#!/bin/bash
echo "Starting Shadow LAN SCP transfer..."
mkdir -p /home/zepher/logs
for f in /omega_pool/parquet_data/v63_subset_l1_shadow_w1/host=windows1/*.parquet; do
    filename=$(basename "$f")

    echo "Shadow Transferring $filename via LAN IP 192.168.3.112..."
    scp -i /tmp/win_key -o StrictHostKeyChecking=no "$f" jiazi@192.168.3.112:D:/Omega_frames/v63_subset_l1_shadow_w1/host=windows1/
    if [ $? -eq 0 ]; then
        echo "Successfully transferred $f"
    else
        echo "Failed to transfer $f"
    fi
done
echo "All shadow transfers completed."
