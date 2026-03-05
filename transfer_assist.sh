#!/bin/bash
echo "Starting SCP transfer..."
for f in /omega_pool/parquet_data/v63_subset_l1_assist_w1/host=windows1/*.parquet; do
    echo "Transferring $f"
    scp -i /tmp/win_key -o StrictHostKeyChecking=no "$f" jiazi@100.123.90.25:D:/Omega_frames/v63_subset_l1_assist_w1/host=windows1/
    if [ $? -eq 0 ]; then
        echo "Successfully transferred $f"
    else
        echo "Failed to transfer $f"
    fi
done
echo "All transfers completed."
