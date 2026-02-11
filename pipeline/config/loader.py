import yaml
import os
from typing import Type, TypeVar
from dataclasses import fields, is_dataclass

from pipeline.config.hardware import HardwareProfile, StorageConfig, ComputeConfig

T = TypeVar("T")

class ConfigLoader:
    @staticmethod
    def load_hardware_profile(yaml_path: str) -> HardwareProfile:
        """
        Loads a YAML file and converts it into a typed HardwareProfile object.
        """
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"Config file not found: {yaml_path}")
            
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        # Basic validation: Check if root keys exist
        if "hardware" not in data:
            raise ValueError("YAML must contain a top-level 'hardware' key")
            
        hw_data = data["hardware"]
        
        # Construct Sub-Configs
        storage = StorageConfig(**hw_data.get("storage", {}))
        compute = ComputeConfig(**hw_data.get("compute", {}))
        
        # Construct Profile
        return HardwareProfile(
            profile_name=hw_data.get("profile_name", "Unknown"),
            storage=storage,
            compute=compute
        )

    @staticmethod
    def create_default_yaml(output_path: str):
        """Generates a template config file for the user."""
        profile = HardwareProfile.default_32core_workstation()
        
        # Manual dict construction for clean YAML output
        data = {
            "hardware": {
                "profile_name": profile.profile_name,
                "schema_version": profile.schema_version,
                "storage": {
                    "source_root": profile.storage.source_root,
                    "stage_root": profile.storage.stage_root,
                    "output_root": profile.storage.output_root,
                    "io_slots": profile.storage.io_slots,
                    "disable_indexing": profile.storage.disable_indexing
                },
                "compute": {
                    "framing_workers": profile.compute.framing_workers,
                    "training_workers": profile.compute.training_workers,
                    "backtest_workers": profile.compute.backtest_workers,
                    "memory_threshold_percent": profile.compute.memory_threshold_percent
                }
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, sort_keys=False, default_flow_style=False)
        print(f"Generated default config: {output_path}")
