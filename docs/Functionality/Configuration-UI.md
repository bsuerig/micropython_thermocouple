# ESP32-P4-ETH Configuration UI — Functional Specification

## Scope

This specification covers the Ethernet address-mode and MQTT enable controls on the device configuration page. The page continues to save changes through its existing protected POST operation.

## Requirements

### FR-ETH-UI-01 — Ethernet address mode

- `type: functional`
- `priority: must`
- `source: user`
- `status: approved`
- The configuration page shall present mutually exclusive modes labeled `DHCP` and `Static IP`. The selected mode shall match the saved Ethernet configuration when the page loads. Selecting DHCP shall immediately hide the static IP, netmask, gateway, and DNS fields. Selecting Static IP shall immediately show those fields. Saving shall persist the selected mode and the entered field values.

**Verification contract**

- Preconditions: The device has a valid configuration in DHCP mode or Static IP mode.
- Stimulus: Load the configuration page, change the address-mode control, and inspect the form before saving; then save and load the page again.
- Expected observations: The saved mode is selected on load; the four static fields are hidden for DHCP and visible for Static IP; the selected mode remains selected after saving.
- Timing: Visibility changes in the current page without a reload.
- Tolerance: None.
- Prohibited outcomes: Changing mode clears any of the four entered static values.
- Tier: Host.
- Evidence: Rendered-page assertions and form/configuration round-trip tests.
- Cleanup: Restore the original test configuration.

### FR-MQTT-UI-01 — MQTT configuration visibility

- `type: functional`
- `priority: must`
- `source: user`
- `status: approved`
- The configuration page shall present mutually exclusive MQTT modes labeled `Ein` and `Aus`. The selected mode shall match the saved MQTT enable state when the page loads. Selecting Aus shall immediately hide the MQTT broker, port, topic, username, password, and password-clear controls. Selecting Ein shall immediately show those fields.

**Verification contract**

- Preconditions: The configuration page can be loaded with MQTT enabled or disabled.
- Stimulus: Load the page and select each MQTT mode.
- Expected observations: The saved mode is selected on load; MQTT fields are hidden for Aus and visible for Ein.
- Timing: Visibility changes in the current page without a reload.
- Tolerance: None.
- Prohibited outcomes: Switching modes submits a request or clears configuration fields before the user saves.
- Tier: Host.
- Evidence: Rendered-page assertions and form/configuration round-trip tests.
- Cleanup: Restore the original test configuration.

### FR-MQTT-UI-02 — MQTT enable state and retained settings

- `type: functional`
- `priority: must`
- `source: user`
- `status: approved`
- Saving MQTT mode Aus shall persist MQTT as disabled while retaining the broker and other MQTT settings. While disabled, the device shall not connect to the broker or publish messages. Saving mode Ein shall persist MQTT as enabled and permit the existing connection and publish behavior when a broker is configured.

**Verification contract**

- Preconditions: A configuration contains a broker and MQTT is enabled.
- Stimulus: Save with MQTT mode Aus, reload the configuration, and execute a device step with a connected LAN and due publish time; repeat after saving Ein.
- Expected observations: Aus persists as disabled, retains all MQTT settings, and produces no MQTT connection or publish call. Ein persists as enabled and preserves the existing MQTT behavior.
- Timing: Disabled behavior applies after the configuration is loaded at startup.
- Tolerance: No MQTT connection or publish calls are permitted while disabled.
- Prohibited outcomes: Disabling MQTT clears or changes saved broker settings.
- Tier: Host.
- Evidence: Configuration round-trip and mocked Device tests.
- Cleanup: Restore the original test configuration and stubbed MQTT client.

### FR-CONFIG-01 — Legacy MQTT configuration

- `type: functional`
- `priority: must`
- `source: derived`
- `status: approved`
- When loading a configuration created before the MQTT enable state was stored, the device shall infer MQTT enabled when the saved broker field is non-empty and disabled when it is empty. All other valid saved settings shall be retained.

**Verification contract**

- Preconditions: A valid legacy configuration file has no MQTT enable field.
- Stimulus: Load one legacy configuration with a broker and one without a broker.
- Expected observations: The resulting configurations respectively enable and disable MQTT, with all legacy values unchanged.
- Timing: During configuration loading.
- Tolerance: None.
- Prohibited outcomes: A valid legacy configuration falls back to defaults or loses saved values.
- Tier: Host.
- Evidence: Temporary-file migration tests.
- Cleanup: Remove temporary configuration files.

### FR-CONFIG-02 — Grouped configuration file

- `type: functional`
- `priority: must`
- `source: user`
- `status: approved`
- The persisted configuration shall group Ethernet address settings under the top-level `ip` object and MQTT settings under the top-level `mqtt` object. The `ip` object shall contain `dhcp`, `address`, `netmask`, `gateway`, and `dns`; the `mqtt` object shall contain `enabled`, `server`, `port`, `topic`, `user`, `password`, and `interval`. The device shall continue loading the existing flat configuration format and write the grouped format on the next save.

**Verification contract**

- Preconditions: A valid internal configuration is available, or a valid old flat configuration file exists.
- Stimulus: Save a configuration and reload it; separately load a legacy flat file and save it.
- Expected observations: The saved JSON has exactly the `ip` and `mqtt` groups with the defined fields; reloading preserves every value; legacy values remain available and are written grouped after save.
- Timing: During config save/load operations.
- Tolerance: None.
- Prohibited outcomes: MQTT credentials or Ethernet values are lost or written into the wrong group.
- Tier: Host.
- Evidence: Temporary-file serialization, deserialization, and migration tests.
- Cleanup: Remove temporary configuration files.

### FR-STATUS-01 — Runtime status order and optional MQTT status

- `type: functional`
- `priority: must`
- `source: user`
- `status: approved`
- The status row shall display the Ethernet MAC address first, the IP address second, the MQTT status third only while MQTT is enabled, the sensor status next, and the temperature at the far right. When MQTT is disabled, the temperature shall remain at the far right. At viewport widths of 600 px or less, entries shall use one readable column without horizontal overflow.

**Verification contract**

- Preconditions: The device can render its status page with MQTT enabled or disabled.
- Stimulus: Load the status page in each MQTT state.
- Expected observations: Status values appear in the required order; the MQTT status is absent while disabled; temperature occupies the last status column in both states; narrow viewports display one column without horizontal overflow.
- Timing: On the next page load after the runtime state is established.
- Tolerance: None.
- Prohibited outcomes: An empty MQTT column shifts the temperature away from the right edge while MQTT is disabled.
- Tier: Host.
- Evidence: Rendered-page assertions for both MQTT states and status order.
- Cleanup: Restore the original test status.

### FR-STATUS-02 — Live sensor status and temperature

- `type: functional`
- `priority: must`
- `source: user`
- `status: approved`
- While the configuration page is open, it shall update the sensor status and temperature from the device status endpoint every second without reloading the page or changing form values. A failed poll shall leave the last displayed values unchanged.

**Verification contract**

- Preconditions: The configuration page is open and the status endpoint is reachable.
- Stimulus: Change the reported sensor status and temperature between two successful polls.
- Expected observations: The page displays the new sensor status and temperature after the next successful poll; the form remains loaded with its current values.
- Timing: Poll interval is one second; values update on the next successful poll.
- Tolerance: None.
- Prohibited outcomes: A status update reloads the document or clears unsaved form values.
- Tier: Host.
- Evidence: Page-script, CSP, and status-endpoint tests.
- Cleanup: Restore the original status provider.

### FR-STATUS-03 — Temperature unit and API link

- `type: functional`
- `priority: must`
- `source: user`
- `status: approved`
- The status row shall display the temperature in degrees Celsius using the `°C` unit. It shall provide a visible `API` link to `GET /api/temperature` that opens in a new tab.

**Verification contract**

- Preconditions: The configuration page can render a valid temperature reading.
- Stimulus: Load the page and follow the displayed temperature link.
- Expected observations: The page shows the reading followed by `°C`; a visible `API` link opens the existing temperature JSON endpoint in a new tab.
- Timing: The initial reading is rendered with the page; subsequent readings retain the same unit and link.
- Tolerance: None.
- Prohibited outcomes: Following the link changes device configuration.
- Tier: Host.
- Evidence: Rendered-page and HTTP API tests.
- Cleanup: Restore the original status provider.

### FR-UI-LANG-01 — English interface

- `type: functional`
- `priority: must`
- `source: user`
- `status: approved`
- All text presented by the configuration web UI, including field labels, status values, validation errors, and save messages, shall be in English. The HTML document language shall be `en`.

**Verification contract**

- Preconditions: The configuration page can be rendered with valid device status.
- Stimulus: Load the page and submit valid and invalid configuration forms.
- Expected observations: Page labels, dynamic statuses, and visible response messages are in English; the document language is `en`.
- Timing: On page render or response to the submitted form.
- Tolerance: None.
- Prohibited outcomes: German text appears in visible UI strings.
- Tier: Host.
- Evidence: Rendered-page, status, and form-response assertions.
- Cleanup: Restore the original configuration and status provider.

### FR-CAL-01 — Thermocouple calibration profiles

- `type: functional`
- `priority: must`
- `source: user`
- `status: approved`
- The configuration UI shall list saved `Thermocouple_ID` profiles in a dropdown and allow the user to select one or choose `Create new profile`. The user shall configure 2 to 10 pairs of sensor reading and reference temperature in degrees Celsius. The active profile and all profiles shall be persisted in `calibration.json` under `active_id` and `profiles.<Thermocouple_ID>.points`; each point shall contain numeric `measured` and `reference` values. Existing profiles embedded in `config.json` shall be migrated to `calibration.json` on load.

**Verification contract**

- Preconditions: The device configuration page is available.
- Stimulus: Create or select a profile ID, enter the point count and corresponding sensor/reference temperatures, and save.
- Expected observations: The active ID and all profile points are saved and restored on the next page load; other profiles remain unchanged.
- Timing: On the save/reboot cycle.
- Tolerance: Point values are represented as finite numeric Celsius values; profile IDs are 1 to 32 ASCII letters, digits, spaces, periods, hyphens, or underscores, with no leading or trailing whitespace.
- Prohibited outcomes: Saving one profile deletes or changes another profile.
- Tier: Host.
- Evidence: Form, JSON round-trip, and profile-retention tests.
- Cleanup: Restore the original config fixture.

### FR-CAL-02 — Piecewise linear correction

- `type: functional`
- `priority: must`
- `source: user`
- `status: approved`
- For a valid active profile, the device shall convert sensor readings to reference temperatures by piecewise linear interpolation between the profile's ordered calibration points. It shall not extrapolate outside the range; readings outside the range shall remain uncorrected.

**Verification contract**

- Preconditions: At least two valid, strictly increasing sensor-reading and reference-temperature values exist in the active profile.
- Stimulus: Provide readings at a point, between points, and outside both ends of the profile.
- Expected observations: Exact point readings map to their reference values; intermediate readings use linear interpolation; out-of-range readings are unchanged.
- Timing: During the sensor sampling operation.
- Tolerance: Absolute difference no greater than 0.001 °C in host calculations.
- Prohibited outcomes: Extrapolated correction outside the calibrated range.
- Tier: Host.
- Evidence: Pure interpolation tests and a mocked Device sampling test.
- Cleanup: Restore the original active profile.

### FR-CAL-03 — Visible calibration identity and applied state

- `type: functional`
- `priority: must`
- `source: user`
- `status: approved`
- The status row shall show the active calibration profile ID between MQTT status and sensor status. It shall show a `Calibrated` indicator when correction changes the raw sensor value and omit that indicator otherwise. The live status endpoint shall provide these values without changing the existing temperature API or MQTT payload.

**Verification contract**

- Preconditions: A calibration profile is active and the status page is open.
- Stimulus: Sample a reading that is corrected, then one that remains unchanged; poll the live status endpoint.
- Expected observations: The active ID appears in the required status-row position; `Calibrated` appears only when the numeric temperature changes; live updates refresh both values.
- Timing: On the next one-second status poll.
- Tolerance: Correction indicator is true exactly when corrected and raw numeric values differ.
- Prohibited outcomes: Existing `/api/temperature` JSON or MQTT payload gains calibration metadata.
- Tier: Host.
- Evidence: Device status, status endpoint, page rendering, and MQTT payload tests.
- Cleanup: Restore the original calibration profile and sensor reading.

### FR-CAL-04 — Calibration profile API

- `type: functional`
- `priority: must`
- `source: user`
- `status: approved`
- `GET /api/calibration` shall return the active profile and all saved profiles. `POST /api/calibration` shall activate an existing profile when given `sensor_id`, or create/update and activate a profile when given `sensor_id` and `points`. Updates shall retain all other profiles. MQTT, `GET /api/temperature`, and `GET /api/status` shall emit identical JSON containing `temperature`, `unit`, `sensor`, `sensor_id`, `calibrated`, and `raw_temperature`.

**Verification contract**

- Preconditions: The device has zero or more valid profiles and accepts JSON requests on the local network.
- Stimulus: GET the calibration resource; POST a new profile, update it, and POST an existing ID without points to activate it; GET temperature afterward.
- Expected observations: Profile data round-trips, active_id changes, unrelated profiles remain, and MQTT plus both temperature endpoints return identical raw/corrected metadata.
- Timing: API responses complete within the existing request timeout.
- Tolerance: Same profile and point validation rules as the web UI.
- Prohibited outcomes: An API update removes unrelated profiles or makes MQTT and temperature API JSON differ.
- Tier: Host.
- Evidence: API GET/POST tests, JSON persistence tests, and MQTT/API schema assertions.
- Cleanup: Restore the original calibration file fixture.
