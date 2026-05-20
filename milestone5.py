import threading
import time
from enum import Enum
from kaggle_loader import load_kaggle_sensors
import csv
from datetime import datetime

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
    print("-" * 65)
    print("  SENSOR DATA PROCESSING SYSTEM — MILESTONE 5")
    print("   INTEGRATED WITH KAGGLE DATASET (1000 records × 3 sensor types)")
    print("-" * 65)

    # >>> KAGGLE INTEGRATION: Load real agricultural sensor data
    # >>> 1000 Kaggle records × 3 sensor types = 3000 concurrent threads
    print("\n  Loading the dataset...")
    kaggle_sensor_data = load_kaggle_sensors(limit=1000)
    
    if not kaggle_sensor_data:
        print("  [ERROR] Failed to load Kaggle dataset. Exiting.")
        exit(1)

    # Convert Kaggle sensor data into thread objects
    sensor_threads = [
        Sensor(
            s["sensor_id"],
            s["zone"],
            SensorType[s["sensor_type"]],
            s["reading"],
            s["unit"],
            s["timestamp"]
        )
        for s in kaggle_sensor_data
    ]

    print(f"\n  Starting {len(sensor_threads)} sensor threads concurrently...\n")
    
    # Clear global results list for fresh run
    results_list.clear()
    
    print(f"  {'STATE':<9} {'ID':<15} {'ZONE':<25} {'READING':<12} ASSESSMENT")
    print(f"  {'-'*8} {'-'*14} {'-'*24} {'-'*11} {'-'*30}")

    for sensor in sensor_threads:
        sensor.start()

    # >>> THREAD SYNCHRONIZATION: join() waits for all 21 threads
    # >>> Ensures all results are collected before filtering
    for sensor in sensor_threads:
        sensor.join()

    print(f"\n  All {len(sensor_threads)} sensor threads completed.\n")

    print("-" * 65)
    print("  LAMBDA-BASED RESULTS FILTERING")
    print("-" * 65)

    alerts = apply_filter(
        results_list,
        lambda r: r["state"] == SensorState.ALERT.name
    )
    print(f"\n  [Lambda 1] Sensors in ALERT state: {len(alerts)}")
    for r in alerts:
        print(f"    * {r['sensor_id']} | {r['zone']} | {r['assessment']}")

    warnings = apply_filter(
        results_list,
        lambda r: r["state"] == SensorState.WARNING.name
    )
    print(f"\n  [Lambda 2] Sensors in WARNING state: {len(warnings)}")
    for r in warnings:
        print(f"    * {r['sensor_id']} | {r['zone']} | {r['assessment']}")

    faulty = apply_filter(
        results_list,
        lambda r: r["state"] == SensorState.FAULTY.name
    )
    print(f"\n  [Lambda 3] Faulty sensors detected: {len(faulty)}")
    for r in faulty:
        print(f"    * {r['sensor_id']} | {r['zone']} | {r['assessment']}")

    normal_moisture = apply_filter(
        results_list,
        lambda r: r["type"] == SensorType.MOISTURE.value and r["state"] == SensorState.NORMAL.name
    )
    print(f"\n  [Lambda 4] Moisture sensors at OPTIMAL level: {len(normal_moisture)}")
    for r in normal_moisture:
        print(f"    * {r['sensor_id']} | {r['zone']} | Reading: {r['reading']} VWC")

    moisture_results = apply_filter(
        results_list,
        lambda r: r["type"] == SensorType.MOISTURE.value and r["state"] != SensorState.FAULTY.name
    )
    if moisture_results:
        avg_moisture = sum(r["reading"] for r in moisture_results) / len(moisture_results)
        print(f"\n  [Lambda 5] Average moisture (valid sensors): {avg_moisture:.3f} VWC")

    # >>> CSV EXPORT FOR POWER BI
    # >>> Export all results to CSV for external analytics and visualization
    csv_filename = "sensor_output.csv"
    try:
        with open(csv_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["sensor_id", "zone", "type", "reading", "unit", "state", "assessment", "timestamp"]
            )
            writer.writeheader()
            writer.writerows(results_list)
        
        print(f"\n  [CSV EXPORT] Results exported to {csv_filename} ({len(results_list)} records)")
    except Exception as e:
        print(f"\n  [CSV EXPORT ERROR] Failed to export: {e}")

    print(f"\n{'-' * 65}")
    print("  MILESTONE 5 — CONCURRENT SYSTEM SUMMARY")
    print(f"{'-' * 65}")
    print(f"  Total threads run     : {len(sensor_threads)}")
    print(f"  Results collected     : {len(results_list)}")
    print(f"  ALERT sensors         : {len(alerts)}")
    print(f"  WARNING sensors       : {len(warnings)}")
    print(f"  FAULTY sensors        : {len(faulty)}")
    print(f"  NORMAL sensors        : {len(results_list) - len(alerts) - len(warnings) - len(faulty)}")
    print(f"\n  Enum states used      : {[s.name for s in SensorState]}")
    print(f"  Synchronization locks : results_lock, print_lock, log_lock")
    print(f"  Lambda filters applied: 5")
    print("-" * 65)
