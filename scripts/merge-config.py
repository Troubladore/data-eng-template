#!/usr/bin/env python3
"""
Merge organizational cookiecutter configuration with upstream template defaults.

This script combines:
- cookiecutter.json (upstream template - never modify)
- org-cookiecutter.json (organizational overrides - git ignored)

Into a final effective cookiecutter configuration for template generation.

Usage:
    python scripts/merge-config.py                    # Merge and validate
    python scripts/merge-config.py --check-only       # Validate only
    python scripts/merge-config.py --create-example   # Create example org config
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Set
import argparse


class ConfigMerger:
    def __init__(self, template_root: Path):
        self.template_root = template_root
        self.base_config_path = template_root / "cookiecutter.json"
        self.org_config_path = template_root / "org-cookiecutter.json"
        self.effective_config_path = template_root / "cookiecutter.json.effective"

    def load_base_config(self) -> Dict[str, Any]:
        """Load the upstream base configuration."""
        if not self.base_config_path.exists():
            raise FileNotFoundError(f"Base config not found: {self.base_config_path}")

        with open(self.base_config_path) as f:
            return json.load(f)

    def load_org_config(self) -> Dict[str, Any]:
        """Load organizational overrides if they exist."""
        if not self.org_config_path.exists():
            return {}

        with open(self.org_config_path) as f:
            return json.load(f)

    def merge_configs(self, base: Dict[str, Any], org: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge organizational config into base config.

        Rules:
        - Org values completely override base values (including arrays)
        - Base provides defaults for any missing org values
        - Warn about org keys that don't exist in base (potential deprecated config)
        """
        merged = base.copy()
        warnings = []

        # Check for deprecated org config (keys not in base)
        base_keys = set(base.keys())
        org_keys = set(org.keys())
        deprecated_keys = org_keys - base_keys

        if deprecated_keys:
            warnings.append(f"⚠️  Org config contains deprecated attributes: {sorted(deprecated_keys)}")
            warnings.append("   These will be ignored. Consider removing them from org-cookiecutter.json")

        # Check for new upstream attributes (in base but not customized by org)
        new_upstream_keys = base_keys - org_keys
        if new_upstream_keys:
            warnings.append(f"ℹ️  New upstream attributes available for customization: {sorted(new_upstream_keys)}")
            warnings.append("   Using upstream defaults. Add to org-cookiecutter.json to customize.")

        # Merge org overrides into base
        for key, value in org.items():
            if key in base:
                merged[key] = value

        return merged, warnings

    def create_example_org_config(self) -> None:
        """Create an example org-cookiecutter.json file."""
        base = self.load_base_config()

        # Create example with common organizational customizations
        example_org_config = {
            "_comment": "Organizational cookiecutter overrides - customize as needed",
            "_instructions": [
                "This file overrides upstream cookiecutter.json defaults",
                "Only include attributes you want to customize",
                "First item in arrays becomes the default choice",
                "Missing attributes will use upstream defaults"
            ],

            # Example technology stack customization
            "python_version": [
                "3.12.11",  # Your primary standard (becomes default)
                "3.11.13",  # Legacy compatibility option
                "3.13.7"    # Early adopter option (remove if not needed)
            ],

            # Example organizational infrastructure
            "image_repo": "your-registry.com/data-eng/{{ cookiecutter.customer_slug }}",
            "company_domain": "your-company.com",
            "license": "Proprietary",

            # Example security defaults
            "secrets_strategy": [
                "azure-key-vault",    # Your default
                "env-vars"            # Development option
            ]
        }

        print(f"Creating example org config: {self.org_config_path}")
        with open(self.org_config_path, 'w') as f:
            json.dump(example_org_config, f, indent=2)

        print("✅ Example org-cookiecutter.json created!")
        print("   Edit this file to customize your organizational defaults")

    def validate_and_merge(self, check_only: bool = False) -> bool:
        """
        Validate and merge configurations.

        Returns True if successful, False if there are issues.
        """
        try:
            base = self.load_base_config()
            org = self.load_org_config()

            if not org and not self.org_config_path.exists():
                print("ℹ️  No org-cookiecutter.json found - using upstream defaults only")
                print("   Run with --create-example to create organizational overrides")
                if not check_only:
                    # Copy base config as effective config
                    with open(self.effective_config_path, 'w') as f:
                        json.dump(base, f, indent=2)
                return True

            merged, warnings = self.merge_configs(base, org)

            # Print warnings
            for warning in warnings:
                print(warning)

            if check_only:
                print("✅ Configuration validation passed")
                return True

            # Write effective configuration
            with open(self.effective_config_path, 'w') as f:
                json.dump(merged, f, indent=2)

            print(f"✅ Effective configuration written to: {self.effective_config_path}")

            # Summary
            base_keys = len(base)
            org_keys = len(org)
            print(f"📊 Config summary: {base_keys} base attributes, {org_keys} org overrides")

            return True

        except Exception as e:
            print(f"❌ Error: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check-only', action='store_true',
                       help='Validate configuration without writing effective config')
    parser.add_argument('--create-example', action='store_true',
                       help='Create example org-cookiecutter.json file')

    args = parser.parse_args()

    template_root = Path(__file__).parent.parent
    merger = ConfigMerger(template_root)

    if args.create_example:
        merger.create_example_org_config()
        return

    success = merger.validate_and_merge(check_only=args.check_only)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()