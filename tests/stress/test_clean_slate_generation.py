"""Stress tests for clean slate generation - Ensures reliability from scratch."""

import subprocess
import time
from pathlib import Path
import pytest
import docker


class TestCleanSlateGeneration:
    """Test template works from completely clean Docker environment."""
    
    @pytest.mark.stress
    @pytest.mark.clean_slate
    @pytest.mark.slow
    def test_generation_after_complete_docker_cleanup(self, template_dir, temp_dir, default_cookiecutter_config):
        """Test template generation works after removing all Docker artifacts."""
        # This test ensures the template doesn't have hidden dependencies
        # on existing Docker images, networks, or volumes
        
        print("🧹 Performing complete Docker cleanup...")
        self._complete_docker_cleanup()
        
        print("📝 Generating project from clean slate...")
        project_dir = self._generate_project(template_dir, temp_dir, default_cookiecutter_config)
        
        # Verify generation succeeded
        assert project_dir.exists(), "Project should generate successfully"
        assert (project_dir / "README.md").exists(), "README should be generated"
        assert (project_dir / ".devcontainer" / "compose.yaml").exists(), "Compose file should exist"
        
        print("🐳 Testing Docker Compose startup from clean state...")
        # Test that compose can build and start from completely clean state
        compose_file = project_dir / ".devcontainer" / "compose.yaml"
        
        try:
            # This should work even with no pre-existing images
            start_result = subprocess.run([
                'docker', 'compose', '-f', str(compose_file), 'up', '-d', '--build'
            ], capture_output=True, text=True, timeout=600,  # Extended timeout for fresh builds
            cwd=project_dir / ".devcontainer")
            
            if start_result.returncode != 0:
                print(f"Docker Compose stderr: {start_result.stderr}")
                print(f"Docker Compose stdout: {start_result.stdout}")
                pytest.fail(f"Clean slate Docker Compose failed: {start_result.stderr}")
            
            # Wait a bit for services to initialize
            time.sleep(30)
            
            # Verify containers are running
            ps_result = subprocess.run([
                'docker', 'compose', '-f', str(compose_file), 'ps'
            ], capture_output=True, text=True, timeout=30,
            cwd=project_dir / ".devcontainer")
            
            assert "Up" in ps_result.stdout, "Services should be running"
            
        finally:
            # Always cleanup
            print("🧹 Cleaning up test containers...")
            subprocess.run([
                'docker', 'compose', '-f', str(compose_file), 'down', '-v', '--remove-orphans'
            ], capture_output=True, timeout=120, cwd=project_dir / ".devcontainer")
    
    @pytest.mark.stress 
    @pytest.mark.clean_slate
    def test_no_hidden_docker_dependencies(self, template_dir, temp_dir, default_cookiecutter_config):
        """Verify template doesn't rely on pre-existing Docker images."""
        # Generate project
        project_dir = self._generate_project(template_dir, temp_dir, default_cookiecutter_config)
        
        # Scan compose file for image references
        compose_file = project_dir / ".devcontainer" / "compose.yaml"
        content = compose_file.read_text()
        
        # Check for hardcoded image references that might not exist
        problematic_patterns = [
            "localhost:",           # Local registry references
            ":latest",             # Unversioned latest tags  
            "custom-",             # Custom images that might not exist
        ]
        
        for pattern in problematic_patterns:
            if pattern in content:
                # Allow some patterns in specific contexts
                if pattern == ":latest" and "postgres:16" in content:
                    continue  # postgres:16 is fine, postgres:latest is not
                pytest.fail(f"Potentially problematic Docker reference '{pattern}' in compose.yaml")
        
        # Verify all base images are standard public images
        lines = content.split('\n')
        image_lines = [line.strip() for line in lines if 'image:' in line and not line.strip().startswith('#')]
        
        for line in image_lines:
            image_name = line.split(':', 1)[1].strip()
            # Remove quotes and variable substitutions for analysis
            image_name = image_name.replace('"', '').replace("'", "")
            
            # Skip cookiecutter variables - they'll be resolved
            if "{{" in image_name:
                continue
                
            # Should be standard public registry images
            standard_registries = ['postgres:', 'python:', 'mcr.microsoft.com/']
            is_standard = any(registry in image_name for registry in standard_registries)
            
            assert is_standard, f"Non-standard Docker image reference: {image_name}"
    
    def _complete_docker_cleanup(self):
        """Perform complete Docker cleanup - DESTRUCTIVE!"""
        # WARNING: This removes ALL Docker artifacts on the system
        # Only use in isolated test environments
        
        cleanup_commands = [
            # Stop all containers
            ['docker', 'stop', '$(docker ps -aq)'],
            # Remove all containers  
            ['docker', 'rm', '$(docker ps -aq)'],
            # Remove all images
            ['docker', 'rmi', '$(docker images -aq)', '--force'],
            # Remove all volumes
            ['docker', 'volume', 'prune', '--force'],
            # Remove all networks
            ['docker', 'network', 'prune', '--force'],
            # Remove all build cache
            ['docker', 'builder', 'prune', '--all', '--force'],
        ]
        
        for cmd in cleanup_commands:
            # Use shell=True to handle command substitution
            full_cmd = ' '.join(cmd)
            try:
                subprocess.run(full_cmd, shell=True, capture_output=True, timeout=60)
            except subprocess.TimeoutExpired:
                print(f"Warning: Cleanup command timed out: {full_cmd}")
            except Exception as e:
                print(f"Warning: Cleanup command failed: {full_cmd} - {e}")
        
        # Verify cleanup worked
        try:
            images_result = subprocess.run(['docker', 'images', '-q'], 
                                         capture_output=True, text=True)
            remaining_images = len(images_result.stdout.strip().split('\n')) if images_result.stdout.strip() else 0
            print(f"Remaining Docker images after cleanup: {remaining_images}")
        except Exception:
            print("Could not verify Docker cleanup")
    
    def _generate_project(self, template_dir: str, temp_dir: Path, config: dict) -> Path:
        """Generate a test project."""
        cmd = [
            'cookiecutter', template_dir,
            '--output-dir', str(temp_dir),
            '--no-input'
        ]
        
        for key, value in config.items():
            cmd.append(f"{key}={value}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            pytest.fail(f"Project generation failed: {result.stderr}")
        
        return temp_dir / config["project_slug"]