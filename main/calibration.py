"""Validate thermocouple calibration profiles and correct readings."""

import math

MIN_CALIBRATION_POINTS = 2
MAX_CALIBRATION_POINTS = 10
MAX_PROFILE_ID_LENGTH = 32
DEFAULT_CALIBRATION = {"active_id": "", "profiles": {}}


def _valid_profile_id(value):
    """Accept readable ASCII profile names while excluding markup characters."""
    if (not isinstance(value, str)
            or not 1 <= len(value) <= MAX_PROFILE_ID_LENGTH):
        return False
    if value != value.strip():
        return False
    return all((48 <= ord(char) <= 57) or (65 <= ord(char) <= 90)
               or (97 <= ord(char) <= 122) or char in " ._-" for char in value)


def _valid_temperature(value):
    """Accept finite JSON numeric temperatures, excluding booleans."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return math.isfinite(value)


def validate_calibration(value):
    """Return validated active ID and copies of all profile point tables."""
    if not isinstance(value, dict) or set(value) != {"active_id", "profiles"}:
        raise ValueError("Calibration must contain active_id and profiles.")
    active_id = value["active_id"]
    profiles = value["profiles"]
    if (not isinstance(active_id, str)
            or (active_id and not _valid_profile_id(active_id))):
        raise ValueError("Use 1-32 ASCII letters, numbers, spaces, periods, underscores, or hyphens for the profile ID.")
    if not isinstance(profiles, dict):
        raise ValueError("Calibration profiles must be an object.")

    checked_profiles = {}
    for profile_id, profile in profiles.items():
        if not _valid_profile_id(profile_id):
            raise ValueError("Use 1-32 ASCII letters, numbers, spaces, periods, underscores, or hyphens for the profile ID.")
        if not isinstance(profile, dict) or set(profile) != {"points"}:
            raise ValueError("Each calibration profile must contain points.")
        points = profile["points"]
        if (not isinstance(points, list)
                or not MIN_CALIBRATION_POINTS <= len(points) <= MAX_CALIBRATION_POINTS):
            raise ValueError("Each profile must contain 2 to 10 calibration points.")
        checked_points = []
        previous_measured = None
        previous_reference = None
        for point in points:
            if (not isinstance(point, dict)
                    or set(point) != {"measured", "reference"}):
                raise ValueError("Each point needs measured and reference values.")
            measured = point["measured"]
            reference = point["reference"]
            if (not _valid_temperature(measured)
                    or not _valid_temperature(reference)):
                raise ValueError("Calibration values must be finite numbers.")
            if previous_measured is not None and measured <= previous_measured:
                raise ValueError("Measured values must be strictly increasing.")
            if (previous_reference is not None
                    and reference <= previous_reference):
                raise ValueError("Reference values must be strictly increasing.")
            checked_points.append({"measured": measured, "reference": reference})
            previous_measured = measured
            previous_reference = reference
        checked_profiles[profile_id] = {"points": checked_points}

    if active_id and active_id not in checked_profiles:
        raise ValueError("Active calibration profile does not exist.")
    return {"active_id": active_id, "profiles": checked_profiles}


def update_calibration(value, sensor_id, points=None):
    """Upsert a profile or activate an existing one without dropping others."""
    calibration = validate_calibration(value)
    if not _valid_profile_id(sensor_id):
        raise ValueError("Invalid thermocouple profile ID.")
    profiles = calibration["profiles"]
    if points is None:
        if sensor_id not in profiles:
            raise ValueError("Calibration profile does not exist.")
    else:
        profiles[sensor_id] = {"points": points}
    return validate_calibration({"active_id": sensor_id, "profiles": profiles})


def calibrate_temperature(temperature, points):
    """Interpolate between measured/reference points without extrapolating."""
    if temperature is None or not points:
        return temperature
    if (temperature < points[0]["measured"]
            or temperature > points[-1]["measured"]):
        return temperature
    for index in range(len(points) - 1):
        lower = points[index]
        upper = points[index + 1]
        if lower["measured"] <= temperature <= upper["measured"]:
            fraction = ((temperature - lower["measured"])
                        / (upper["measured"] - lower["measured"]))
            return (lower["reference"]
                    + fraction * (upper["reference"] - lower["reference"]))
    return temperature