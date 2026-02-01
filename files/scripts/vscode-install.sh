#!/usr/bin/env bash
set -euo pipefail

VSCODE_KEY_URL="https://packages.microsoft.com/keys/microsoft.asc"
VSCODE_REPO_FILE="[code]
name=Visual Studio Code
baseurl=https://packages.microsoft.com/yumrepos/vscode
enabled=0
gpgcheck=1
gpgkey=$VSCODE_KEY_URL
"

main() {
    rpm --import "$VSCODE_KEY_URL"
    tee /etc/yum.repos.d/vscode.repo <<< "$VSCODE_REPO_FILE" > /dev/null
    dnf install -y --enablerepo=code code
}

_entry() {
    set -euo pipefail
    main "$@"
    eval "exit $?"
}

_entry "$@"
