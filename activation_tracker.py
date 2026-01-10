"""
Activation tracking for beta keys.
Limits each key to MAX_ACTIVATIONS_PER_KEY machines.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from config import DATA_DIR, MAX_ACTIVATIONS_PER_KEY


ACTIVATIONS_FILE = DATA_DIR / "activations.json"


@dataclass
class Activation:
    """Single activation record"""
    machine_id: str
    activated_at: str
    app_version: str = ""
    os_version: str = ""


@dataclass
class KeyActivations:
    """All activations for a single key"""
    key_id: str
    user_id: int
    activations: List[Activation]
    max_activations: int = MAX_ACTIVATIONS_PER_KEY


def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_activations() -> Dict[str, dict]:
    """Load all activation data"""
    _ensure_data_dir()
    if ACTIVATIONS_FILE.exists():
        with open(ACTIVATIONS_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_activations(data: Dict[str, dict]):
    """Save activation data"""
    _ensure_data_dir()
    with open(ACTIVATIONS_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_key_activations(key_id: str) -> Optional[KeyActivations]:
    """Get activation info for a key"""
    data = _load_activations()
    if key_id not in data:
        return None
    
    record = data[key_id]
    activations = [
        Activation(**a) for a in record.get("activations", [])
    ]
    return KeyActivations(
        key_id=key_id,
        user_id=record.get("user_id", 0),
        activations=activations,
        max_activations=record.get("max_activations", MAX_ACTIVATIONS_PER_KEY)
    )


def can_activate(key_id: str, machine_id: str) -> tuple[bool, str]:
    """
    Check if a key can be activated on a machine.
    Returns (can_activate, reason)
    """
    record = get_key_activations(key_id)
    
    if record is None:
        # First activation
        return True, "first_activation"
    
    # Check if already activated on this machine
    for activation in record.activations:
        if activation.machine_id == machine_id:
            return True, "already_activated"
    
    # Check activation limit
    if len(record.activations) >= record.max_activations:
        return False, f"limit_reached:{record.max_activations}"
    
    return True, "new_machine"


def record_activation(
    key_id: str,
    user_id: int,
    machine_id: str,
    app_version: str = "",
    os_version: str = ""
) -> tuple[bool, str]:
    """
    Record a new activation.
    Returns (success, message)
    """
    can, reason = can_activate(key_id, machine_id)
    
    if not can:
        return False, reason
    
    if reason == "already_activated":
        return True, "already_activated"
    
    data = _load_activations()
    
    if key_id not in data:
        data[key_id] = {
            "key_id": key_id,
            "user_id": user_id,
            "activations": [],
            "max_activations": MAX_ACTIVATIONS_PER_KEY
        }
    
    activation = Activation(
        machine_id=machine_id,
        activated_at=datetime.now().isoformat(),
        app_version=app_version,
        os_version=os_version
    )
    
    data[key_id]["activations"].append(asdict(activation))
    _save_activations(data)
    
    count = len(data[key_id]["activations"])
    return True, f"activated:{count}/{MAX_ACTIVATIONS_PER_KEY}"


def deactivate_machine(key_id: str, machine_id: str) -> bool:
    """Remove a machine from activations (allows re-activation elsewhere)"""
    data = _load_activations()
    
    if key_id not in data:
        return False
    
    original_count = len(data[key_id]["activations"])
    data[key_id]["activations"] = [
        a for a in data[key_id]["activations"]
        if a["machine_id"] != machine_id
    ]
    
    if len(data[key_id]["activations"]) < original_count:
        _save_activations(data)
        return True
    
    return False


def get_activation_stats() -> dict:
    """Get overall activation statistics"""
    data = _load_activations()
    
    total_keys = len(data)
    total_activations = sum(
        len(record.get("activations", []))
        for record in data.values()
    )
    
    return {
        "total_keys": total_keys,
        "total_activations": total_activations,
        "keys_at_limit": sum(
            1 for record in data.values()
            if len(record.get("activations", [])) >= record.get("max_activations", MAX_ACTIVATIONS_PER_KEY)
        )
    }
