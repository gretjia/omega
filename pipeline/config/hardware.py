from dataclasses import dataclass, field
from typing import Optional, List, Dict

@dataclass
class StorageConfig:
    """
    Defines the topology for disk I/O.
    Separating Source (Read) from Stage (Write/Read) is critical for high IOPS.
    """
    source_root: str  # e.g., "F:/Data/Level2" (USB4 Archive)
    stage_root: str   # e.g., "D:/Omega_stage" (Fast NVMe)
    output_root: str  # e.g., "D:/Omega_vNext/data" (Fast NVMe)
    
    # I/O Throttling
    io_slots: int = 4  # Concurrent disk operations allowed
    
    # OS Optimization
    disable_indexing: bool = True
    check_defender_exclusion: bool = True

@dataclass
class ComputeConfig:
    """
    Defines the CPU/GPU resource allocation.
    """
    framing_workers: int = 22
    training_workers: int = 26
    backtest_workers: int = 20
    
    # Advanced: Pin workers to specific NUMA nodes (future)
    numa_pinning: bool = False
    
    # Memory Guard
    memory_threshold_percent: float = 88.0

@dataclass
class HardwareProfile:
    """
    The Master Hardware Configuration Entry Point.
    Load this from YAML to switch between 'Workstation' and 'Server' modes.
    """
    profile_name: str
    storage: StorageConfig
    compute: ComputeConfig
    
    # Versioning for the config file itself
    schema_version: str = "1.0"

    @classmethod
    def default_32core_workstation(cls) -> "HardwareProfile":
        """Factory for the current 32-Core + 990 Pro setup."""
        return cls(
            profile_name="32Core_Hybrid_Storage",
            storage=StorageConfig(
                source_root="E:/data/level2",                 # USB4 external archive source
                stage_root="D:/Omega_frames/v50/stage",       # High-IOPS NVMe staging
                output_root="D:/Omega_frames/v50/output"      # Framing output
            ),
            compute=ComputeConfig(
                framing_workers=22, # Tuned for C: limit, can go higher on D:
                training_workers=26,
                backtest_workers=20
            )
        )
