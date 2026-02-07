import inspect
import pkgutil
import strategies
from strategies.base import Strategy


def discover_strategies() -> dict[str, type[Strategy]]:
    """
    Auto-discover all Strategy subclasses in strategies package.
    """
    registry = {}

    for _, module_name, _ in pkgutil.iter_modules(strategies.__path__):
        module = __import__(f"strategies.{module_name}", fromlist=["*"])

        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, Strategy) and obj is not Strategy:
                registry[obj.name()] = obj

    return registry
