
import hashlib

def get_shard(filename, total_shards):
    """Deterministic sharding logic."""
    # Use MD5 hash of filename for stable distribution across platforms
    h = hashlib.md5(filename.encode()).hexdigest()
    return int(h, 16) % total_shards

def test_distribution():
    files = [f"file_{i}.7z" for i in range(1000)]
    shards = {0: 0, 1: 0}
    for f in files:
        s = get_shard(f, 2)
        shards[s] += 1
    
    print(f"Distribution for 1000 files across 2 shards: {shards}")
    assert shards[0] > 400 and shards[1] > 400, "Shard distribution is too uneven!"
    print("Unit Test Passed: Deterministic Sharding is stable.")

if __name__ == "__main__":
    test_distribution()
