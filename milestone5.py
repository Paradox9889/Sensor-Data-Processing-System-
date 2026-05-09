import threading
import time
from enum import Enum

# >>> ENUMERATIONS: Replace raw strings with fixed set of valid states
# >>> SensorState enum catches invalid states immediately as errors


class SensorState(Enum):
    """Enumeration of all valid sensor operational states."""
    ACTIVE      = 1
    NORMAL      = 2
    WARNING     = 3
    ALERT       = 4
    FAULTY      = 5
    OFFLINE     = 6


class SensorType(Enum):
    """Enumeration of sensor measurement types."""
    MOISTURE    = "MOISTURE"
    TEMPERATURE = "TEMPERATURE"
    PH          = "PH"


# Shared resources and synchronization locks
results_list = []
results_lock = threading.Lock()   # >>> THREAD LOCK: Prevents race conditions
print_lock = threading.Lock()     # >>> Only one thread writes at a time
log_lock = threading.Lock()


class Sensor(threading.Thread):
    """A sensor that runs as its own independent thread."""
    # >>> MULTITHREADING: Each sensor runs in its own thread
    # >>> All 21 threads start concurrently, not sequentially

    def __init__(self, sensor_id, zone, sensor_type, reading, unit, timestamp):
        super().__init__()
        self.__sensor_id   = sensor_id
        self.__zone        = zone
        self.__sensor_type = sensor_type
        self.__reading     = reading
        self.__unit        = unit
        self.__timestamp   = timestamp
        self.__state       = SensorState.ACTIVE
        self.__assessment  = ""

    def run(self):
        """Thread main task — validates and processes the reading."""
        time.sleep(0.05)
        self.__validate()
        self.__process()

        result = {
            "sensor_id"  : self.__sensor_id,
            "zone"       : self.__zone,
            "type"       : self.__sensor_type.value,
            "reading"    : self.__reading,
            "unit"       : self.__unit,
            "state"      : self.__state.name,
            "assessment" : self.__assessment,
            "timestamp"  : self.__timestamp,
        }

        with results_lock:
            results_list.append(result)

        with print_lock:
            print(
                f"  [{self.__state.name:<7}] "
                f"{self.__sensor_id:<10} | "
                f"{self.__zone:<20} | "
                f"{self.__reading} {self.__unit:<5} | "
                f"{self.__assessment}"
            )

    def __validate(self):
        """Validates the reading range."""
        if self.__reading is None:
            self.__state = SensorState.OFFLINE
            self.__assessment = "No reading received — sensor offline"
            return

        if self.__sensor_type == SensorType.MOISTURE:
            if not (0.0 <= self.__reading <= 1.0):
                self.__state = SensorState.FAULTY
                self.__assessment = f"Moisture {self.__reading} out of range (0.0–1.0)"

        elif self.__sensor_type == SensorType.TEMPERATURE:
            if not (0.0 <= self.__reading <= 60.0):
                self.__state = SensorState.FAULTY
                self.__assessment = f"Temperature {self.__reading}°C out of range"

        elif self.__sensor_type == SensorType.PH:
            if not (0.0 <= self.__reading <= 14.0):
                self.__state = SensorState.FAULTY
                self.__assessment = f"pH {self.__reading} out of valid range"

    def __process(self):
        """Classifies the reading and assigns a SensorState."""
        if self.__state in (SensorState.FAULTY, SensorState.OFFLINE):
            return

        if self.__sensor_type == SensorType.MOISTURE:
            m = self.__reading
            if m < 0.20:
                self.__state      = SensorState.ALERT
                self.__assessment = "CRITICAL DRY — irrigate immediately"
            elif m < 0.35:
                self.__state      = SensorState.WARNING
                self.__assessment = "DRY — schedule irrigation within 24hrs"
            elif m < 0.65:
                self.__state      = SensorState.NORMAL
                self.__assessment = "OPTIMAL — soil conditions good"
            elif m < 0.80:
                self.__state      = SensorState.WARNING
                self.__assessment = "WET — monitor drainage"
            else:
                self.__state      = SensorState.ALERT
                self.__assessment = "WATERLOGGED — activate drainage"

        elif self.__sensor_type == SensorType.TEMPERATURE:
            t = self.__reading
            if t < 15.0:
                self.__state      = SensorState.ALERT
                self.__assessment = "COLD STRESS — frost risk"
            elif t < 20.0:
                self.__state      = SensorState.WARNING
                self.__assessment = "COOL — suboptimal for crops"
            elif t <= 30.0:
                self.__state      = SensorState.NORMAL
                self.__assessment = "OPTIMAL — ideal temperature"
            elif t <= 35.0:
                self.__state      = SensorState.WARNING
                self.__assessment = "WARM — monitor crop stress"
            else:
                self.__state      = SensorState.ALERT
                self.__assessment = "HEAT STRESS — crops at risk"

        elif self.__sensor_type == SensorType.PH:
            ph = self.__reading
            if ph < 4.5:
                self.__state      = SensorState.ALERT
                self.__assessment = "HIGHLY ACIDIC — lime required urgently"
            elif ph < 5.5:
                self.__state      = SensorState.WARNING
                self.__assessment = "ACIDIC — consider lime treatment"
            elif ph <= 6.8:
                self.__state      = SensorState.NORMAL
                self.__assessment = "OPTIMAL — ideal for crops"
            elif ph <= 7.5:
                self.__state      = SensorState.WARNING
                self.__assessment = "ALKALINE — nutrient availability reduced"
            else:
                self.__state      = SensorState.ALERT
                self.__assessment = "HIGHLY ALKALINE — soil amendment required"

    def get_sensor_id(self):  return self.__sensor_id
    def get_state(self):      return self.__state
    def get_reading(self):    return self.__reading
    def get_zone(self):       return self.__zone


def apply_filter(results, filter_func):
    """Applies a lambda filter function to the results list."""
    # >>> LAMBDA EXPRESSIONS: Anonymous functions for functional filtering
    # >>> Filter results after all threads complete
    return list(filter(filter_func, results))


if __name__ == "__main__":
    print("=" * 65)
    print("  SENSOR DATA PROCESSING SYSTEM — MILESTONE 5")
    print("  Concurrency & Advanced Computation")
    print("=" * 65)

    sensor_threads = [
        Sensor("SNS-M01", "North Field A",    SensorType.MOISTURE,    0.32, "VWC", "2024-05-01 06:00"),
        Sensor("SNS-M02", "North Field B",    SensorType.MOISTURE,    0.15, "VWC", "2024-05-01 06:00"),
        Sensor("SNS-M03", "East Greenhouse",  SensorType.MOISTURE,    0.61, "VWC", "2024-05-01 06:00"),
        Sensor("SNS-M04", "East Orchard",     SensorType.MOISTURE,    0.44, "VWC", "2024-05-01 06:00"),
        Sensor("SNS-M05", "Central Paddock",  SensorType.MOISTURE,    0.72, "VWC", "2024-05-01 06:00"),
        Sensor("SNS-M06", "Central Nursery",  SensorType.MOISTURE,    0.28, "VWC", "2024-05-01 06:00"),
        Sensor("SNS-M07", "West Cropland",    SensorType.MOISTURE,    0.53, "VWC", "2024-05-01 06:00"),
        Sensor("SNS-M08", "West Pasture",     SensorType.MOISTURE,    0.81, "VWC", "2024-05-01 06:00"),
        Sensor("SNS-M09", "South Wetland",    SensorType.MOISTURE,    0.13, "VWC", "2024-05-01 06:00"),
        Sensor("SNS-M10", "South Dryland",    SensorType.MOISTURE,    1.45, "VWC", "2024-05-01 06:00"),
        Sensor("SNS-T01", "North Field A",    SensorType.TEMPERATURE, 24.3, "°C",  "2024-05-01 06:00"),
        Sensor("SNS-T02", "East Greenhouse",  SensorType.TEMPERATURE, 22.1, "°C",  "2024-05-01 06:00"),
        Sensor("SNS-T03", "Central Paddock",  SensorType.TEMPERATURE, 31.7, "°C",  "2024-05-01 06:00"),
        Sensor("SNS-T04", "West Cropland",    SensorType.TEMPERATURE, 36.8, "°C",  "2024-05-01 06:00"),
        Sensor("SNS-T05", "South Wetland",    SensorType.TEMPERATURE, 28.4, "°C",  "2024-05-01 06:00"),
        Sensor("SNS-T06", "South Dryland",    SensorType.TEMPERATURE, 38.5, "°C",  "2024-05-01 06:00"),
        Sensor("SNS-P01", "North Field A",    SensorType.PH,          6.2,  "pH",  "2024-05-01 06:00"),
        Sensor("SNS-P02", "East Orchard",     SensorType.PH,          4.8,  "pH",  "2024-05-01 06:00"),
        Sensor("SNS-P03", "Central Nursery",  SensorType.PH,          7.1,  "pH",  "2024-05-01 06:00"),
        Sensor("SNS-P04", "West Cropland",    SensorType.PH,          5.9,  "pH",  "2024-05-01 06:00"),
        Sensor("SNS-P05", "South Dryland",    SensorType.PH,          8.1,  "pH",  "2024-05-01 06:00"),
    ]

    print(f"\n  Starting {len(sensor_threads)} sensor threads concurrently...\n")
    print(f"  {'STATE':<9} {'ID':<10} {'ZONE':<21} {'READING':<12} ASSESSMENT")
    print(f"  {'-'*8} {'-'*9} {'-'*20} {'-'*11} {'-'*30}")

    for sensor in sensor_threads:
        sensor.start()

    # >>> THREAD SYNCHRONIZATION: join() waits for all 21 threads
    # >>> Ensures all results are collected before filtering
    for sensor in sensor_threads:
        sensor.join()

    print(f"\n  All {len(sensor_threads)} sensor threads completed.\n")

    print("=" * 65)
    print("  LAMBDA-BASED RESULTS FILTERING")
    print("=" * 65)

    alerts = apply_filter(
        results_list,
        lambda r: r["state"] == SensorState.ALERT.name
    )
    print(f"\n  [Lambda 1] Sensors in ALERT state: {len(alerts)}")
    for r in alerts:
        print(f"    → {r['sensor_id']} | {r['zone']} | {r['assessment']}")

    warnings = apply_filter(
        results_list,
        lambda r: r["state"] == SensorState.WARNING.name
    )
    print(f"\n  [Lambda 2] Sensors in WARNING state: {len(warnings)}")
    for r in warnings:
        print(f"    → {r['sensor_id']} | {r['zone']} | {r['assessment']}")

    faulty = apply_filter(
        results_list,
        lambda r: r["state"] == SensorState.FAULTY.name
    )
    print(f"\n  [Lambda 3] Faulty sensors detected: {len(faulty)}")
    for r in faulty:
        print(f"    → {r['sensor_id']} | {r['zone']} | {r['assessment']}")

    normal_moisture = apply_filter(
        results_list,
        lambda r: r["type"] == SensorType.MOISTURE.value and r["state"] == SensorState.NORMAL.name
    )
    print(f"\n  [Lambda 4] Moisture sensors at OPTIMAL level: {len(normal_moisture)}")
    for r in normal_moisture:
        print(f"    → {r['sensor_id']} | {r['zone']} | Reading: {r['reading']} VWC")

    moisture_results = apply_filter(
        results_list,
        lambda r: r["type"] == SensorType.MOISTURE.value and r["state"] != SensorState.FAULTY.name
    )
    if moisture_results:
        avg_moisture = sum(r["reading"] for r in moisture_results) / len(moisture_results)
        print(f"\n  [Lambda 5] Average moisture (valid sensors): {avg_moisture:.3f} VWC")

    print(f"\n{'=' * 65}")
    print("  MILESTONE 5 — CONCURRENT SYSTEM SUMMARY")
    print(f"{'=' * 65}")
    print(f"  Total threads run     : {len(sensor_threads)}")
    print(f"  Results collected     : {len(results_list)}")
    print(f"  ALERT sensors         : {len(alerts)}")
    print(f"  WARNING sensors       : {len(warnings)}")
    print(f"  FAULTY sensors        : {len(faulty)}")
    print(f"  NORMAL sensors        : {len(results_list) - len(alerts) - len(warnings) - len(faulty)}")
    print(f"\n  Enum states used      : {[s.name for s in SensorState]}")
    print(f"  Synchronization locks : results_lock, print_lock, log_lock")
    print(f"  Lambda filters applied: 5")
    print(f"\n  [Milestone 5 Complete]")
    print("=" * 65)
