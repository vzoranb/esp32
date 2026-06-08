# ESP32-S3 Diagnostics Guide

This document outlines the procedure to connect over WiFi and run diagnostics on the ESP32-S3 board in this workspace.

## Device Details
- **Hostname:** `ble-presence-tracker.lan`
- **IP Address:** `192.168.160.135`
- **Native API Port:** `6053`
- **Hardware:** ESP32-S3 rev0.2 (Dual-core, 16MB Flash, 8MB PSRAM)

## Diagnostic Procedure

1. **Locate Virtual Environment:**
   The Python virtual environment containing the correct `esphome` installation is located at:
   `./sniffer/venv`

2. **Temporary Secrets Configuration:**
   ESPHome requires a `secrets.yaml` file to validate the configuration file (`esphome-web-209108.yaml`), even when only streaming logs.
   Create a temporary `secrets.yaml` file in the root of the project:
   ```yaml
   wifi_ssid: "dummy_ssid_name"
   wifi_password: "dummy_password_long"
   ```

3. **Run Diagnostics Command:**
   Execute the following command to connect to the device over WiFi and stream its logs:
   ```bash
   ./sniffer/venv/bin/esphome logs esphome-web-209108.yaml --device 192.168.160.135
   ```

4. **Cleanup:**
   Once logs are obtained, terminate the process and remove the temporary `secrets.yaml` file:
   ```bash
   rm secrets.yaml
   ```
