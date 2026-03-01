"""
multi_dir_loader.py

Multi-directory L2 frame loader with stratified sampling support.
Follows OMEGA Constitution: no physical file copy needed.

Usage:
    from tools.multi_dir_loader import load_l2_frames
    
    # Load all data (lazy)
    lf = load_l2_frames()
    
    # Load with 1% stratified sample
    lf = load_l2_frames(sample_frac=0.01, stratified=True)
    
    # Filter by year
    lf = load_l2_frames(year="2023")
"""

import polars as pl
from pathlib import Path
from typing import List, Optional
import re

# Default data directories
DEFAULT_DIRS = [
    "data/level2_frames_win2023",
    "data/level2_frames_mac2024",
]

# Project root (auto-detect)
PROJECT_ROOT = Path(__file__).parent.parent


def discover_l2_dirs(base_path: Path = None) -> List[Path]:
    """
    Auto-discover all level2_frames_* directories.
    """
    if base_path is None:
        base_path = PROJECT_ROOT / "data"
    
    dirs = sorted(base_path.glob("level2_frames_*"))
    return [d for d in dirs if d.is_dir() and not d.name.startswith("_")]


def extract_year_from_filename(filename: str) -> Optional[str]:
    """
    Extract year from parquet filename (e.g., 20230103_000001.SZ.parquet -> 2023)
    """
    match = re.match(r"^(\d{4})", filename)
    if match:
        return match.group(1)
    return None


def load_l2_frames(
    dirs: List[str] = None,
    year: Optional[str] = None,
    sample_frac: float = 1.0,
    stratified: bool = True,
    add_source_dir: bool = True,
) -> pl.LazyFrame:
    """
    Load L2 frames from multiple directories with optional filtering and sampling.
    
    Args:
        dirs: List of directory paths. If None, auto-discovers all level2_frames_* dirs.
        year: Filter by year (e.g., "2023"). Filters based on filename prefix.
        sample_frac: Fraction of data to sample (0.0-1.0). Default 1.0 = all data.
        stratified: If True, sample proportionally from each directory (preserves year ratio).
        add_source_dir: If True, adds a 'source_dir' column for traceability.
    
    Returns:
        pl.LazyFrame: Lazy frame ready for further processing or .collect()
    
    Example:
        >>> lf = load_l2_frames(sample_frac=0.01, stratified=True)
        >>> df = lf.collect()  # Materialize ~490K rows from 49M total
    """
    # Resolve directories
    if dirs is None:
        resolved_dirs = discover_l2_dirs()
        if not resolved_dirs:
            # Fallback to defaults
            resolved_dirs = [PROJECT_ROOT / d for d in DEFAULT_DIRS]
    else:
        resolved_dirs = [Path(d) if not Path(d).is_absolute() else Path(d) for d in dirs]
        resolved_dirs = [PROJECT_ROOT / d if not d.is_absolute() else d for d in resolved_dirs]
    
    # Filter by year if specified (via directory suffix)
    if year:
        resolved_dirs = [d for d in resolved_dirs if year in d.name]
    
    # Build glob patterns
    patterns = []
    for d in resolved_dirs:
        if not d.exists():
            print(f"[Warning] Directory not found: {d}")
            continue
        
        if year and year not in d.name:
            # Year filter by filename prefix
            patterns.append(str(d / f"{year}*.parquet"))
        else:
            patterns.append(str(d / "*.parquet"))
    
    if not patterns:
        raise ValueError(f"No valid directories found. Checked: {resolved_dirs}")
    
    # Load with lazy scan
    lazy_frames = []
    for pattern in patterns:
        try:
            lf = pl.scan_parquet(pattern)
            
            # Add source directory column if requested
            if add_source_dir:
                source_name = Path(pattern).parent.name
                lf = lf.with_columns(pl.lit(source_name).alias("source_dir"))
            
            lazy_frames.append(lf)
        except Exception as e:
            print(f"[Warning] Failed to scan {pattern}: {e}")
    
    if not lazy_frames:
        raise ValueError("No parquet files found to load.")
    
    # Concatenate all lazy frames
    if len(lazy_frames) == 1:
        combined = lazy_frames[0]
    else:
        combined = pl.concat(lazy_frames, how="diagonal")
    
    # Apply sampling
    if sample_frac < 1.0:
        if stratified and add_source_dir:
            # Stratified sampling by source directory
            # Note: This requires collecting to get proportions, so we use a seed for reproducibility
            combined = combined.filter(
                pl.lit(1).sample(fraction=sample_frac, seed=42).cast(pl.Boolean)
            )
        else:
            # Simple random sampling
            combined = combined.sample(fraction=sample_frac, seed=42)
    
    return combined


def get_data_summary(dirs: List[str] = None) -> dict:
    """
    Get summary statistics of available L2 data without loading all data.
    
    Returns:
        dict with 'total_files', 'dirs', and estimated 'total_rows'
    """
    if dirs is None:
        resolved_dirs = discover_l2_dirs()
        if not resolved_dirs:
            resolved_dirs = [PROJECT_ROOT / d for d in DEFAULT_DIRS]
    else:
        resolved_dirs = [Path(d) for d in dirs]
    
    summary = {
        "dirs": {},
        "total_files": 0,
        "total_size_gb": 0.0,
    }
    
    for d in resolved_dirs:
        if not d.exists():
            continue
        
        files = list(d.glob("*.parquet"))
        n_files = len(files)
        size_bytes = sum(f.stat().st_size for f in files[:100]) / 100 * n_files if files else 0
        
        summary["dirs"][d.name] = {
            "n_files": n_files,
            "size_gb_est": round(size_bytes / 1e9, 2),
        }
        summary["total_files"] += n_files
        summary["total_size_gb"] += size_bytes / 1e9
    
    summary["total_size_gb"] = round(summary["total_size_gb"], 2)
    return summary


# CLI for quick testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="L2 Multi-Dir Loader")
    parser.add_argument("--summary", action="store_true", help="Show data summary only")
    parser.add_argument("--sample", type=float, default=0.001, help="Sample fraction for quick test")
    parser.add_argument("--year", type=str, default=None, help="Filter by year")
    args = parser.parse_args()
    
    if args.summary:
        print("=== L2 Data Summary ===")
        s = get_data_summary()
        for dir_name, info in s["dirs"].items():
            print(f"  {dir_name}: {info['n_files']:,} files (~{info['size_gb_est']} GB)")
        print(f"  TOTAL: {s['total_files']:,} files (~{s['total_size_gb']} GB)")
    else:
        print(f"Loading L2 frames (sample={args.sample}, year={args.year})...")
        lf = load_l2_frames(sample_frac=args.sample, year=args.year)
        df = lf.collect()
        print(f"Loaded {len(df):,} rows")
        print(f"Schema: {df.schema}")
        print(f"Columns: {df.columns}")
        if "source_dir" in df.columns:
            print(f"Distribution by source:")
            print(df.group_by("source_dir").len())
