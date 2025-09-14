#!/usr/bin/env python3
"""
Intelligent deployment script for Airflow with caching optimization.

Inspired by Astronomer's deployment model:
- DAG-only deployments for fast iterations
- Full image builds only when dependencies change  
- Automatic change detection
- Performance monitoring and optimization
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import tempfile

# Import Hydra for configuration management
try:
    import hydra
    from omegaconf import DictConfig
    from hydra import compose, initialize_config_dir
except ImportError:
    print("Warning: Hydra not available. Using basic configuration.")
    hydra = None

# Colors for terminal output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(message: str, color: str = Colors.END):
    """Print colored message to terminal."""
    print(f"{color}{message}{Colors.END}")

def print_step(message: str):
    """Print a deployment step."""
    print_colored(f"🚀 {message}", Colors.BLUE)

def print_success(message: str):
    """Print a success message."""
    print_colored(f"✅ {message}", Colors.GREEN)

def print_warning(message: str):
    """Print a warning message."""
    print_colored(f"⚠️  {message}", Colors.YELLOW)

def print_error(message: str):
    """Print an error message."""
    print_colored(f"❌ {message}", Colors.RED)

class DeploymentStrategy:
    """Enumeration of deployment strategies."""
    DAG_ONLY = "dags-only"
    FULL = "full"
    IMAGE_AND_DAGS = "image-and-dags"
    DETECT = "detect"

class ChangeDetector:
    """Detects what files have changed to determine deployment strategy."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.cache_file = project_root / ".deploy_cache.json"
    
    def get_file_hash(self, file_path: Path) -> str:
        """Get SHA256 hash of a file."""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (FileNotFoundError, PermissionError):
            return ""
    
    def get_directory_hash(self, dir_path: Path, include_patterns: List[str] = None) -> str:
        """Get hash of all files in a directory matching patterns."""
        if not dir_path.exists():
            return ""
        
        include_patterns = include_patterns or ["**/*"]
        hasher = hashlib.sha256()
        
        files = []
        for pattern in include_patterns:
            files.extend(sorted(dir_path.glob(pattern)))
        
        for file_path in sorted(set(files)):
            if file_path.is_file():
                hasher.update(str(file_path.relative_to(self.project_root)).encode())
                hasher.update(self.get_file_hash(file_path).encode())
        
        return hasher.hexdigest()
    
    def get_current_hashes(self) -> Dict[str, str]:
        """Get current hashes of all relevant files/directories."""
        return {
            "dags": self.get_directory_hash(self.project_root / "dags"),
            "dependencies": self.get_file_hash(self.project_root / "pyproject.toml") + 
                          self.get_file_hash(self.project_root / "uv.lock") +
                          self.get_file_hash(self.project_root / "airflow" / "requirements.txt"),
            "plugins": self.get_directory_hash(self.project_root / "airflow" / "plugins"),
            "transforms": self.get_directory_hash(self.project_root / "transforms"),
            "config": self.get_directory_hash(self.project_root / "conf"),
            "dockerfile": self.get_file_hash(self.project_root / "Dockerfile.airflow"),
        }
    
    def load_cached_hashes(self) -> Dict[str, str]:
        """Load previously cached hashes."""
        if not self.cache_file.exists():
            return {}
        
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def save_hashes(self, hashes: Dict[str, str]):
        """Save current hashes to cache."""
        with open(self.cache_file, 'w') as f:
            json.dump(hashes, f, indent=2)
    
    def detect_changes(self) -> Tuple[DeploymentStrategy, Set[str]]:
        """Detect what changed and recommend deployment strategy."""
        current_hashes = self.get_current_hashes()
        cached_hashes = self.load_cached_hashes()
        
        changed_areas = set()
        
        for area, current_hash in current_hashes.items():
            if area not in cached_hashes or cached_hashes[area] != current_hash:
                changed_areas.add(area)
        
        # Determine strategy based on what changed
        if not changed_areas:
            return DeploymentStrategy.DAG_ONLY, changed_areas  # No changes, fast deploy
        
        dependencies_changed = any(area in changed_areas for area in ["dependencies", "dockerfile"])
        code_changed = any(area in changed_areas for area in ["dags", "plugins", "transforms", "config"])
        
        if dependencies_changed:
            strategy = DeploymentStrategy.FULL
        elif code_changed:
            if "dags" in changed_areas and len(changed_areas) == 1:
                strategy = DeploymentStrategy.DAG_ONLY
            else:
                strategy = DeploymentStrategy.IMAGE_AND_DAGS
        else:
            strategy = DeploymentStrategy.DAG_ONLY
        
        return strategy, changed_areas

class DeploymentTimer:
    """Times deployment operations."""
    
    def __init__(self):
        self.start_time = None
        self.steps = []
    
    def start(self):
        """Start timing."""
        self.start_time = time.time()
    
    def step(self, name: str):
        """Record a step."""
        if self.start_time is None:
            self.start()
        
        current_time = time.time()
        duration = current_time - self.start_time
        self.steps.append((name, duration))
        print_colored(f"⏱️  {name}: {duration:.2f}s", Colors.YELLOW)
    
    def total(self) -> float:
        """Get total elapsed time."""
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time
    
    def summary(self):
        """Print timing summary."""
        total_time = self.total()
        print_colored(f"\n📊 Deployment completed in {total_time:.2f}s", Colors.BOLD)
        
        for step_name, step_time in self.steps:
            percentage = (step_time / total_time) * 100 if total_time > 0 else 0
            print(f"   {step_name}: {step_time:.2f}s ({percentage:.1f}%)")

class AirflowDeployer:
    """Main deployment orchestrator."""
    
    def __init__(self, project_root: Path, config: Optional[DictConfig] = None):
        self.project_root = project_root
        self.config = config
        self.change_detector = ChangeDetector(project_root)
        self.timer = DeploymentTimer()
    
    def run_command(self, cmd: List[str], check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
        """Run a shell command with error handling."""
        print_colored(f"Running: {' '.join(cmd)}", Colors.BLUE)
        
        try:
            result = subprocess.run(
                cmd, 
                cwd=self.project_root,
                check=check,
                capture_output=capture_output,
                text=True
            )
            return result
        except subprocess.CalledProcessError as e:
            print_error(f"Command failed: {' '.join(cmd)}")
            print_error(f"Error: {e}")
            if capture_output and e.stdout:
                print(f"STDOUT:\n{e.stdout}")
            if capture_output and e.stderr:
                print(f"STDERR:\n{e.stderr}")
            raise
    
    def build_docker_image(self, tag: str = "latest", use_cache: bool = True) -> bool:
        """Build Docker image with caching optimization."""
        print_step("Building Docker image")
        
        cmd = [
            "docker", "build",
            "-f", "Dockerfile.airflow",
            "-t", f"airflow-{self.project_root.name}:{tag}",
            "--target", "runtime"
        ]
        
        if use_cache:
            cmd.extend(["--cache-from", f"airflow-{self.project_root.name}:latest"])
        else:
            cmd.append("--no-cache")
        
        cmd.append(".")
        
        try:
            self.run_command(cmd)
            return True
        except subprocess.CalledProcessError:
            print_error("Docker build failed")
            return False
    
    def deploy_dags_only(self, dry_run: bool = False) -> bool:
        """Deploy only DAG files (fastest deployment)."""
        print_step("Deploying DAGs only")
        
        if dry_run:
            print_colored("🔍 DRY RUN: Would copy DAG files to running containers", Colors.YELLOW)
            return True
        
        # Copy DAGs to running Airflow containers
        compose_file = self.project_root / ".devcontainer" / "compose.yaml"
        
        if not compose_file.exists():
            print_error("DevContainer compose file not found")
            return False
        
        # Restart scheduler to pick up DAG changes
        cmd = ["docker-compose", "-f", str(compose_file), "restart", "airflow-scheduler"]
        
        try:
            self.run_command(cmd)
            print_success("DAGs deployed successfully")
            return True
        except subprocess.CalledProcessError:
            print_error("Failed to restart Airflow scheduler")
            return False
    
    def deploy_full(self, dry_run: bool = False) -> bool:
        """Deploy full image (dependencies + code)."""
        print_step("Deploying full image")
        
        if dry_run:
            print_colored("🔍 DRY RUN: Would build and deploy full Docker image", Colors.YELLOW)
            return True
        
        # Build new image
        if not self.build_docker_image():
            return False
        
        self.timer.step("Docker build")
        
        # Restart all services with new image
        compose_file = self.project_root / ".devcontainer" / "compose.yaml"
        
        if not compose_file.exists():
            print_error("DevContainer compose file not found")
            return False
        
        cmd = ["docker-compose", "-f", str(compose_file), "up", "-d", "--force-recreate"]
        
        try:
            self.run_command(cmd)
            print_success("Full deployment completed successfully")
            return True
        except subprocess.CalledProcessError:
            print_error("Failed to restart services")
            return False
    
    def deploy(self, strategy: DeploymentStrategy, dry_run: bool = False) -> bool:
        """Execute deployment based on strategy."""
        self.timer.start()
        
        print_step(f"Starting deployment with strategy: {strategy}")
        
        success = False
        
        if strategy == DeploymentStrategy.DAG_ONLY:
            success = self.deploy_dags_only(dry_run)
        elif strategy == DeploymentStrategy.FULL:
            success = self.deploy_full(dry_run)
        elif strategy == DeploymentStrategy.IMAGE_AND_DAGS:
            # Build image but deploy both
            success = self.deploy_full(dry_run)
        else:
            print_error(f"Unknown deployment strategy: {strategy}")
            return False
        
        if success and not dry_run:
            # Update cache with current hashes
            current_hashes = self.change_detector.get_current_hashes()
            self.change_detector.save_hashes(current_hashes)
        
        self.timer.summary()
        return success

def load_config(config_name: str = "config") -> Optional[DictConfig]:
    """Load Hydra configuration."""
    if hydra is None:
        return None
    
    try:
        # Initialize Hydra with the configuration directory
        config_dir = Path.cwd() / "conf"
        
        if not config_dir.exists():
            print_warning("Configuration directory not found, using defaults")
            return None
        
        with initialize_config_dir(config_dir=str(config_dir.absolute()), version_base=None):
            cfg = compose(config_name=config_name)
            return cfg
    except Exception as e:
        print_warning(f"Could not load Hydra configuration: {e}")
        return None

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Intelligent Airflow deployment script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --dags-only                 # Deploy only DAG files (fastest)
  %(prog)s --full                      # Deploy everything (dependencies + code)  
  %(prog)s --detect-changes           # Auto-detect what changed and deploy accordingly
  %(prog)s --detect-changes --dry-run # See what would be deployed without doing it
        """
    )
    
    parser.add_argument(
        "--dags-only", 
        action="store_const",
        dest="strategy",
        const=DeploymentStrategy.DAG_ONLY,
        help="Deploy only DAG files (fastest, for DAG-only changes)"
    )
    
    parser.add_argument(
        "--full", 
        action="store_const",
        dest="strategy", 
        const=DeploymentStrategy.FULL,
        help="Deploy full image (dependencies + code, slowest but complete)"
    )
    
    parser.add_argument(
        "--detect-changes",
        action="store_const",
        dest="strategy",
        const=DeploymentStrategy.DETECT,
        help="Automatically detect changes and choose deployment strategy (recommended)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deployed without actually doing it"
    )
    
    parser.add_argument(
        "--config",
        default="config",
        help="Hydra configuration name to use (default: config)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Default to change detection if no strategy specified
    if args.strategy is None:
        args.strategy = DeploymentStrategy.DETECT
    
    project_root = Path.cwd()
    
    print_colored("🚁 Airflow Deployment Tool", Colors.BOLD)
    print_colored(f"Project: {project_root.name}", Colors.BLUE)
    print()
    
    # Load configuration
    config = load_config(args.config)
    
    # Initialize deployer
    deployer = AirflowDeployer(project_root, config)
    
    try:
        if args.strategy == DeploymentStrategy.DETECT:
            # Detect changes and recommend strategy
            detected_strategy, changed_areas = deployer.change_detector.detect_changes()
            
            print_step("Change detection results:")
            if changed_areas:
                print(f"Changed areas: {', '.join(sorted(changed_areas))}")
            else:
                print("No changes detected")
            
            print(f"Recommended strategy: {detected_strategy}")
            
            if args.dry_run:
                print_colored(f"🔍 DRY RUN: Would deploy using strategy: {detected_strategy}", Colors.YELLOW)
                return
            
            strategy_to_use = detected_strategy
        else:
            strategy_to_use = args.strategy
        
        print(f"Deployment strategy: {strategy_to_use}")
        print()
        
        # Execute deployment
        success = deployer.deploy(strategy_to_use, args.dry_run)
        
        if success:
            print_success("🎉 Deployment completed successfully!")
            sys.exit(0)
        else:
            print_error("💥 Deployment failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print_error("\n⚡ Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"💥 Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()