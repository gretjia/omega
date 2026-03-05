#!/bin/bash
echo "Starting ultra-fast LAN SCP transfer..."
for f in /omega_pool/parquet_data/v63_subset_l1_assist_w1/host=windows1/*.parquet; do
    filename=$(basename "$f")
    # Check if we should skip (already fully transferred before we killed it or just transferred)
    if [ "$filename" == "20251105_fbd5c8b.parquet" ] || \
       [ "$filename" == "20251106_fbd5c8b.parquet" ] || \
       [ "$filename" == "20251107_fbd5c8b.parquet" ] || \
       [ "$filename" == "20251111_fbd5c8b.parquet" ] || \
       [ "$filename" == "20251112_fbd5c8b.parquet" ] || \
       [ "$filename" == "20251113_fbd5c8b.parquet" ] || \
       [ "$filename" == "20251118_fbd5c8b.parquet" ] || \
       [ "$filename" == "20251120_fbd5c8b.parquet" ] || \
       [ "$filename" == "20251121_fbd5c8b.parquet" ] || \
       [ "$filename" == "20251124_fbd5c8b.parquet" ] || \
       [ "$filename" == "20251128_fbd5c8b.parquet" ] || \
       [ "$filename" == "20251202_fbd5c8b.parquet" ] || \
       [ "$filename" == "20251203_fbd5c8b.parquet" ] || \
       [ "$filename" == "20251204_fbd5c8b.parquet" ]; then
        echo "Skipping $filename (already transferred)"
        continue
    fi

    echo "Transferring $filename via LAN IP 192.168.3.112..."
    scp -i /tmp/win_key -o StrictHostKeyChecking=no "$f" jiazi@192.168.3.112:D:/Omega_frames/v63_subset_l1_assist_w1/host=windows1/
    if [ $? -eq 0 ]; then
        echo "Successfully transferred $f"
    else
        echo "Failed to transfer $f"
    fi
done
echo "All transfers completed."
