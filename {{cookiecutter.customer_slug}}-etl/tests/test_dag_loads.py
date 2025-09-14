from pathlib import Path
import importlib.util

def test_example_dag_imports():
    p = Path("dags/example_dag.py")
    spec = importlib.util.spec_from_file_location("example_dag", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    assert hasattr(mod, "hello")
