package trivy

default ignore = false

ignore {
  input.VulnerabilityID == "CVE-2025-30258"
  input.PkgName == "gpgv"
}
