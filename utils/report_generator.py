import os
import json
from datetime import datetime
from utils.log_analyzer import LogAnalyzer


class ReportGenerator:
    """
    Generates structured test reports combining PyTest results
    and log analysis into a unified summary.
    Useful for sharing results with the engineering team after test runs.
    """

    def __init__(
        self,
        log_file: str = "logs/cloudvault.log",
        output_dir: str = "reports"
    ):
        self.log_file = log_file
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_json_report(self, test_results: dict = None) -> str:
        """
        Generates a JSON report combining test results and log analysis.
        Returns the path to the generated report file.
        """
        analyzer = LogAnalyzer(self.log_file)
        analyzer.parse()
        log_report = analyzer.get_failure_report()

        report = {
            "report_metadata": {
                "project": "CloudVault Test Automation Framework",
                "generated_at": datetime.now().isoformat(),
                "version": "1.0.0"
            },
            "test_results": test_results or {
                "note": "Run via pytest --json-report for full results"
            },
            "log_analysis": log_report,
            "component_summary": analyzer.get_component_summary(),
            "health_indicators": {
                "has_errors": log_report["error_count"] > 0,
                "has_sync_failures": log_report["sync_failures"] > 0,
                "has_offline_events": log_report["offline_events"] > 0,
                "overall_status": (
                    "UNHEALTHY"
                    if log_report["error_count"] > 0
                    else "HEALTHY"
                )
            }
        }

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(
            self.output_dir, f"cloudvault_report_{timestamp}.json"
        )

        with open(output_path, "w") as f:
            json.dump(report, f, indent=4)

        print(f"JSON report generated: {output_path}")
        return output_path

    def generate_text_report(self) -> str:
        """
        Generates a plain text report for quick terminal review.
        Returns the path to the generated report file.
        """
        analyzer = LogAnalyzer(self.log_file)
        analyzer.parse()
        log_report = analyzer.get_failure_report()
        component_summary = analyzer.get_component_summary()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(
            self.output_dir, f"cloudvault_report_{timestamp}.txt"
        )

        with open(output_path, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("   CLOUDVAULT TEST AUTOMATION - FULL REPORT\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"Generated At  : {log_report['generated_at']}\n")
            f.write(f"Log File      : {log_report['log_file']}\n")
            f.write(f"Total Entries : {log_report['total_entries']}\n\n")

            f.write("── FAILURE SUMMARY ──\n")
            f.write(f"  Errors        : {log_report['error_count']}\n")
            f.write(f"  Warnings      : {log_report['warning_count']}\n")
            f.write(f"  Offline Events: {log_report['offline_events']}\n")
            f.write(f"  Sync Failures : {log_report['sync_failures']}\n\n")

            f.write("── COMPONENT BREAKDOWN ──\n")
            for component, counts in component_summary.items():
                f.write(
                    f"  {component:<25} "
                    f"INFO={counts.get('INFO', 0)} "
                    f"WARN={counts.get('WARNING', 0)} "
                    f"ERR={counts.get('ERROR', 0)}\n"
                )

            if log_report["errors"]:
                f.write("\n── ERROR DETAILS ──\n")
                for e in log_report["errors"]:
                    f.write(
                        f"  [{e['timestamp']}] "
                        f"{e['component']}: {e['message']}\n"
                    )

            f.write("\n" + "=" * 60 + "\n")

        print(f"Text report generated: {output_path}")
        return output_path