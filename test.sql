+-------------------+
| Scheduled Scan    |
| (Start)           |
+-------------------+
          |
          v
+-------------------+
| Run Automatically |
| - Check Out Repos |
| - Execute Gitleaks|
+-------------------+
          |
          v
+-----------------------------+
| Scan Results                |
| - False Positives Detected? |
+-----------------------------+
       /    \
      /      \
   Yes        No
    |          |
    v          v
+---------------------------+   +-----------------------------+
| Manually Filter False Positives | | Share True Positive Alerts  |
| - Review Alerts             |   | - Generate Report            |
| - Update Results           |   | - Distribute Report          |
+---------------------------+   +-----------------------------+
            |                            |
            v                            v
+-------------------------+      +--------------------------+
| Team Receives Report    |      | End                      |
| - Remediation Required? |      +--------------------------+
+-------------------------+             |
        /        \                    v
       /          \      +-------------------------+
    Yes            No    | Team Triggers Remediation|
     |                 | - Review Issues          |
     v                 | - Implement Fixes        |
+-------------------------+ +-------------------------+
| Team Triggers Remediation |
+-------------------------+
        |
        v
     +-------------------+
     | Finish            |
     +-------------------+
