from __future__ import annotations

import argparse
from dataclasses import replace
import os

from parallel_config import (
    ParallelTrainerRunConfig,
    ParallelismConfig,
    ParallelPathsConfig,
    ParallelCheckpointConfig,
    load_root_kernel_config,
    load_root_trainer_config,
)
from parallel_trainer import ParallelOmegaTrainer


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=None)
    p.add_argument("--prefetch-files", type=int, default=None)
    p.add_argument("--disable-parallel", action="store_true")
    p.add_argument("--artifact-name", type=str, default=None)
    p.add_argument("--output-dir", type=str, default=None)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--no-resume", action="store_true")
    p.add_argument("--checkpoint-path", type=str, default=None)
    p.add_argument("--checkpoint-every-files", type=int, default=None)
    return p.parse_args()


def main() -> None:
    args = parse_args()

    run_cfg = ParallelTrainerRunConfig()
    par = run_cfg.parallelism

    if args.disable_parallel:
        par = ParallelismConfig(
            enabled=False,
            workers=par.workers,
            prefetch_files=par.prefetch_files,
            worker_blas_threads=par.worker_blas_threads,
        )
    else:
        if args.workers is not None:
            par = ParallelismConfig(
                enabled=True,
                workers=int(args.workers),
                prefetch_files=par.prefetch_files if args.prefetch_files is None else int(args.prefetch_files),
                worker_blas_threads=par.worker_blas_threads,
            )
        elif args.prefetch_files is not None:
            par = ParallelismConfig(
                enabled=True,
                workers=par.workers,
                prefetch_files=int(args.prefetch_files),
                worker_blas_threads=par.worker_blas_threads,
            )

    paths = run_cfg.paths
    if args.artifact_name is not None or args.output_dir is not None:
        paths = replace(
            paths,
            artifact_name=paths.artifact_name if args.artifact_name is None else str(args.artifact_name),
            output_dir=paths.output_dir if args.output_dir is None else str(args.output_dir),
        )

    ckpt = run_cfg.checkpoint
    if args.resume:
        ckpt = replace(ckpt, resume=True, enabled=True)
    if args.no_resume:
        ckpt = replace(ckpt, resume=False)
    if args.checkpoint_path is not None:
        ckpt = replace(ckpt, checkpoint_path=str(args.checkpoint_path), enabled=True)
    if args.checkpoint_every_files is not None:
        ckpt = replace(ckpt, save_every_files=int(args.checkpoint_every_files), enabled=True)

    run_cfg = replace(run_cfg, parallelism=par, paths=paths, checkpoint=ckpt)

    os.makedirs(run_cfg.paths.audit_dir, exist_ok=True)

    kcfg = load_root_kernel_config()
    tcfg = load_root_trainer_config()

    trainer = ParallelOmegaTrainer(kcfg, tcfg, run_cfg)
    artifacts = trainer.fit()
    path = trainer.save_artifacts(artifacts, output_dir=run_cfg.paths.output_dir, artifact_name=run_cfg.paths.artifact_name)
    print(path)


if __name__ == "__main__":
    main()
