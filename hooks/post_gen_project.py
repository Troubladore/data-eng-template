import base64, os, pathlib, json, subprocess

# Write base .env with Fernet key and defaults
key = base64.urlsafe_b64encode(os.urandom(32)).decode()
env_path = pathlib.Path(".env")
lines = [
    f"AIRFLOW__CORE__FERNET_KEY={key}",
    "AIRFLOW__CORE__LOAD_EXAMPLES=False",
    "POSTGRES_DB=airflow",
    "POSTGRES_USER=airflow",
    "POSTGRES_PASSWORD=airflow",
    "PYTHON_VERSION={{cookiecutter.python_version}}",
    "AIRFLOW_VERSION={{cookiecutter.airflow_version}}",
    "POSTGRES_VERSION={{cookiecutter.postgres_version}}",
    "_AIRFLOW_WWW_USER_USERNAME=admin",
    "_AIRFLOW_WWW_USER_PASSWORD=admin"
]
env_path.write_text("\n".join(lines) + "\n")

print("Generated .env with Fernet key.")

# Create a minimal uv.lock placeholder (users will run `uv sync`)
pathlib.Path("uv.lock").write_text("# created on first sync\n")

# Initialize git repository with professional defaults
try:
    # Check if git is available
    subprocess.run(["git", "--version"], check=True, capture_output=True)
    
    # Initialize git repo
    subprocess.run(["git", "init"], check=True, capture_output=True)
    
    # Check for basic git config and warn if missing
    try:
        subprocess.run(["git", "config", "user.name"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Warning: git user.name not configured. Run: git config --global user.name 'Your Name'")
        
    try:
        subprocess.run(["git", "config", "user.email"], check=True, capture_output=True) 
    except subprocess.CalledProcessError:
        print("Warning: git user.email not configured. Run: git config --global user.email 'you@example.com'")
    
    # Set default branch
    subprocess.run(["git", "config", "init.defaultBranch", "main"], capture_output=True)
    
    # Add initial commit
    subprocess.run(["git", "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit from data-eng-template"], check=True, capture_output=True)
    
    print("Initialized git repository with initial commit.")
    
except (subprocess.CalledProcessError, FileNotFoundError) as e:
    print(f"Warning: git initialization failed: {e}")
