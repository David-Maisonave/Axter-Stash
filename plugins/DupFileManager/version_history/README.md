##### This page was added starting on version 0.2.0 to keep track of changes between versions.
### 0.2.0
- For report, added logic to transfer option settings **[Disable Complete Confirmation]** and **[Disable Delete Confirmation]** when paginating.
- Fixed minor bug in advance_options.html for GQL params.
- Added logic to have reports and advanced menu to work with Stash settings requiring a password by adding API-Key as param argument for advance menu, and adding API-Key as variable in reports.
- When **[Advance Tag Menu]** is called from reports, it's given both the GQL URL and the apiKey on the URL param, which allows advance menu to work with non-standard URL's and with API-Key.
### 0.2.1
