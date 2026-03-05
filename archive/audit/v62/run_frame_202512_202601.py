import os
import sys

sys.path.append(os.getcwd())

from pipeline.config.loader import ConfigLoader
from pipeline.adapters.v3_adapter import OmegaCoreAdapter
from pipeline.engine.framer import Framer
from config import load_l2_pipeline_config


def main():
    root = os.environ.get("OMEGA_ROOT", "C:/Omega_vNext")
    profile_path = os.environ.get("OMEGA_PROFILE", "configs/hardware/active_profile.yaml")
    output_dir = os.environ.get("OMEGA_OUTPUT", "D:/Omega_frames/v50/output")
    stage_dir = os.environ.get("OMEGA_STAGE", "D:/Omega_frames/v50/stage")

    os.chdir(root)
    profile = ConfigLoader.load_hardware_profile(profile_path)
    profile.storage.output_root = output_dir
    profile.storage.stage_root = stage_dir

    cfg = load_l2_pipeline_config()
    core = OmegaCoreAdapter()
    core.initialize({"pipeline_cfg": cfg})

    def logger(msg: str):
        print(msg, flush=True)

    fr = Framer(profile, core, logger=logger)
    fr.run(year_filter="202512", limit=0)
    fr.run(year_filter="202601", limit=0)


if __name__ == "__main__":
    main()
