import re
import os
from datetime import datetime
from collections import defaultdict


class LogAnalyzer:
    """
    Analyzes CloudVault test logs to detect failures, warnings,
    and patterns useful for debugging distributed system issues.
    """

    def __init__(self, log_file_path: str = "logs/cloudvault.log"):
        self.log_file_path = log_file_path
        self.entries = []
        self._parsed = False

    def parse(self):
        """Parse the log file into structured entries."""
        if not os.path.exists(self.log_file_path):
            raise FileNotFoundError(f"Log file not found: {self.log_file_path}")

        self.entries = []
        pattern = re.compile(
            r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)"
            r"\s+\|\s+(?P<level>\w+)"
            r"\s+\|\s+(?P<component>[\w.]+)"
            r"\s+\|\s+(?P<message>.+)"
        )

        with open(self.log_file_path, "r") as f:
            for line in f:
                line = line.strip()
                match = pattern.match(line)
                if match:
                    self.entries.append({
                        "timestamp": match.group("timestamp"),
                        "level": match.group("level"),
                        "component": match.group("component"),
                        "message": match.group("message")
                    })

        self._parsed = True
        return self

    def get_errors(self) -> list:
        """Return all ERROR level log entries."""
        self._ensure_parsed()
        return [e for e in self.entries if e["level"] == "ERROR"]

    def get_warnings(self) -> list:
        """Return all WARNING level log entries."""
        self._ensure_parsed()
        return [e for e in self.entries if e["level"] == "WARNING"]

    def get_by_component(self, component: str) -> list:
        """Return all log entries for a specific component."""
        self._ensure_parsed()
        return [e for e in self.entries if component.lower() in e["component"].lower()]

    def get_offline_events(self) -> list:
        """
        Return all events where a node went offline.
        Critical for debugging distributed system failures.
        """
        self._ensure_parsed()
        return [
            e for e in self.entries
            if "OFFLINE" in e["message"] or "offline" in e["message"].lower()
        ]

    def get_sync_failures(self) -> list:
        """Return all sync failure events between edge and cloud."""
        self._ensure_parsed()
        return [
            e for e in self.entries
            if "sync failed" in e["message"].lower() or
               "sync aborted" in e["message"].lower()
        ]

    def get_component_summary(self) -> dict:
        """
        Returns a summary of log entry counts grouped by component.
        Useful for identifying the noisiest or most error-prone components.
        """
        self._ensure_parsed()
        summary = defaultdict(lambda: {"INFO": 0, "WARNING": 0, "ERROR": 0})
        for entry in self.entries:
            level = entry["level"]
            component = entry["component"]
            if level in summary[component]:
                summary[component][level] += 1
        return dict(summary)

    def get_failure_report(self) -> dict:
        """
        Generates a structured failure report from the log file.
        Used for post-test debugging and reporting to the team.
        """
        self._ensure_parsed()
        errors = self.get_errors()
        warnings = self.get_warnings()
        offline_events = self.get_offline_events()
        sync_failures = self.get_sync_failures()

        return {
            "log_file": self.log_file_path,
            "total_entries": len(self.entries),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "offline_events": len(offline_events),
            "sync_failures": len(sync_failures),
            "errors": errors,
            "warnings": warnings,
            "generated_at": datetime.now().isoformat()
        }

    def print_summary(self):
        """Prints a human-readable summary to the terminal."""
        report = self.get_failure_report()
        print("\n" + "=" * 60)
        print("        CLOUDVAULT LOG ANALYSIS REPORT")
        print("=" * 60)
        print(f"  Log File     : {report['log_file']}")
        print(f"  Total Entries: {report['total_entries']}")
        print(f"  Errors       : {report['error_count']}")
        print(f"  Warnings     : {report['warning_count']}")
        print(f"  Offline Events: {report['offline_events']}")
        print(f"  Sync Failures : {report['sync_failures']}")
        print(f"  Generated At : {report['generated_at']}")
        print("=" * 60)

        if report["errors"]:
            print("\n  ERRORS FOUND:")
            for e in report["errors"]:
                print(f"    [{e['timestamp']}] {e['component']}: {e['message']}")

        if report["offline_events"] > 0:
            print(f"\n  WARNING: {report['offline_events']} node offline event(s) detected!")

        print("=" * 60 + "\n")

    def _ensure_parsed(self):
        """Internal guard to ensure log is parsed before analysis."""
        if not self._parsed:
            raise RuntimeError("Call .parse() before analyzing logs.")
