import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import threading


class InMemoryStorage:
    """In-memory storage manager for loan applications and related data."""

    def __init__(self):
        self._lock = threading.RLock()
        self._applications: Dict[str, Any] = {}
        self._applicants: Dict[str, Any] = {}
        self._decisions: Dict[str, Any] = {}
        self._audit_logs: List[Dict[str, Any]] = []
        self._mcp_data: Dict[str, Any] = {}

    def generate_id(self, prefix: str = "app") -> str:
        return f"{prefix}_{uuid.uuid4().hex[:12]}"

    # Application Operations
    def create_application(self, app_data: Dict[str, Any]) -> str:
        with self._lock:
            app_id = self.generate_id("app")
            app_data["application_id"] = app_id
            app_data["created_at"] = datetime.now().isoformat()
            app_data["status"] = "submitted"
            self._applications[app_id] = app_data
            return app_id

    def get_application(self, app_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._applications.get(app_id)

    def get_all_applications(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._applications.values())

    def update_application(self, app_id: str, data: Dict[str, Any]) -> bool:
        with self._lock:
            if app_id in self._applications:
                data["updated_at"] = datetime.now().isoformat()
                self._applications[app_id].update(data)
                return True
            return False

    # Applicant Operations
    def create_applicant(self, applicant_data: Dict[str, Any]) -> str:
        with self._lock:
            applicant_id = applicant_data.get("applicant_id", self.generate_id("appl"))
            applicant_data["applicant_id"] = applicant_id
            applicant_data["created_at"] = datetime.now().isoformat()
            self._applicants[applicant_id] = applicant_data
            return applicant_id

    def get_applicant(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._applicants.get(applicant_id)

    # Decision Operations
    def create_decision(self, decision_data: Dict[str, Any]) -> str:
        with self._lock:
            decision_id = self.generate_id("dec")
            decision_data["decision_id"] = decision_id
            decision_data["created_at"] = datetime.now().isoformat()
            self._decisions[decision_id] = decision_data
            return decision_id

    def get_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._decisions.get(decision_id)

    def get_decision_by_application(self, app_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            for decision in self._decisions.values():
                if decision.get("application_id") == app_id:
                    return decision
            return None

    # Audit Log Operations
    def log_action(self, action_data: Dict[str, Any]) -> str:
        with self._lock:
            log_id = self.generate_id("log")
            action_data["log_id"] = log_id
            action_data["timestamp"] = datetime.now().isoformat()
            self._audit_logs.append(action_data)
            return log_id

    def get_audit_logs(self, app_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._lock:
            if app_id:
                return [log for log in self._audit_logs if log.get("application_id") == app_id]
            return list(self._audit_logs)

    # MCP Data Operations
    def set_mcp_data(self, key: str, data: Dict[str, Any]) -> None:
        with self._lock:
            self._mcp_data[key] = data

    def get_mcp_data(self, key: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._mcp_data.get(key)

    # Storage Summary
    def get_storage_summary(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "total_applications": len(self._applications),
                "total_applicants": len(self._applicants),
                "total_decisions": len(self._decisions),
                "total_audit_logs": len(self._audit_logs),
                "mcp_data_keys": list(self._mcp_data.keys()),
            }

    def clear_all(self) -> None:
        with self._lock:
            self._applications.clear()
            self._applicants.clear()
            self._decisions.clear()
            self._audit_logs.clear()
            self._mcp_data.clear()


class JSONStorage:
    """JSON file-based storage for persistence."""

    def __init__(self, file_path: str = "data/application_data.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not self.file_path.exists():
            initial_data = {
                "applications": {},
                "applicants": {},
                "decisions": {},
                "audit_logs": [],
            }
            with open(self.file_path, "w") as f:
                json.dump(initial_data, f, indent=2)

    def _load(self) -> Dict[str, Any]:
        with self._lock:
            try:
                with open(self.file_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {
                    "applications": {},
                    "applicants": {},
                    "decisions": {},
                    "audit_logs": [],
                }

    def _save(self, data: Dict[str, Any]):
        with self._lock:
            with open(self.file_path, "w") as f:
                json.dump(data, f, indent=2)

    def save_application(self, app_id: str, app_data: Dict[str, Any]):
        data = self._load()
        data["applications"][app_id] = app_data
        self._save(data)

    def load_application(self, app_id: str) -> Optional[Dict[str, Any]]:
        data = self._load()
        return data["applications"].get(app_id)

    def load_all_applications(self) -> Dict[str, Any]:
        data = self._load()
        return data["applications"]


# Global storage instance
_storage_instance = InMemoryStorage()


def get_storage() -> InMemoryStorage:
    return _storage_instance
