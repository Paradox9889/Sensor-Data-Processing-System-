 
from abc import ABC, abstractmethod

# Sensor data processing system using object-oriented design
# Three sensor types (Moisture, Temperature, pH) inherit from abstract base class
# System manages farm sensor network and classifies readings based on real Kenyan farm thresholds



class Sensor(ABC):
    """
    Abstract base class for all sensor types in the system.

    Defines the shared structure and interface that every
    sensor subclass must follow. Cannot be instantiated
    directly — you must use a specific sensor subclass.

    Data source: KALRO Kenya field sensor program structure
    """

    def __init__(self, sensor_id, zone, timestamp):
        # Core attributes shared by ALL sensor types
        self._sensor_id  = sensor_id    # protected (single underscore)
        self._zone       = zone         # farm zone name
        self._timestamp  = timestamp    # when the reading was taken
        self._status     = "ACTIVE"     # operational status
        self._unit       = ""           # measurement unit (set by subclass)

    # Abstract method — every subclass MUST override this
    # This is what makes the system polymorphic
    @abstractmethod
    def process_reading(self):
        pass

    # Abstract method — every subclass must define its reading
    @abstractmethod
    def get_reading(self):
        pass

    # Shared method — all sensors can generate a summary string
    # This demonstrates method overloading via default parameters
    def get_summary(self, verbose=False):
        """
        Returns a summary of this sensor's reading.
        verbose=False → short one-line summary
        verbose=True  → detailed multi-line summary
        This simulates method overloading using default parameters.
        """
        if verbose:
            # Long-form detailed summary
            return (
                f"  Sensor ID   : {self._sensor_id}\n"
                f"  Zone        : {self._zone}\n"
                f"  Timestamp   : {self._timestamp}\n"
                f"  Reading     : {self.get_reading()} {self._unit}\n"
                f"  Status      : {self._status}\n"
                f"  Assessment  : {self.process_reading()}"
            )
        else:
            # Short one-liner summary
            return (
                f"[{self._sensor_id}] {self._zone} | "
                f"{self.get_reading()} {self._unit} | {self.process_reading()}"
            )

    # Getters — shared across all sensor types
    def get_sensor_id(self):
        return self._sensor_id

    def get_zone(self):
        return self._zone

    def get_status(self):
        return self._status

    def get_timestamp(self):
        return self._timestamp




class MoistureSensor(Sensor):
    """
    Measures volumetric soil water content.

    Real-world range from KALRO Kenya sensor deployments:
    Dry season: 0.12 - 0.35
    Wet season : 0.45 - 0.78
    Scale: 0.0 (bone dry) to 1.0 (fully saturated)
    """

    def __init__(self, sensor_id, zone, timestamp, moisture):
        # Call the parent class constructor first
        super().__init__(sensor_id, zone, timestamp)
        self.__moisture = moisture   # the actual moisture reading
        self._unit      = "VWC"      # volumetric water content unit

    def get_reading(self):
        # Return this sensor's specific measurement
        return self.__moisture

    def process_reading(self):
        """
        Classifies moisture level using real Kenyan farm thresholds.
        Thresholds sourced from KALRO and TAMSAT Kenya dataset.
        """
        m = self.__moisture

        if m < 0.0 or m > 1.0:
            self._status = "FAULTY"
            return "INVALID READING — sensor fault detected"

        elif m < 0.20:
            self._status = "ALERT"
            return "CRITICAL DRY — irrigate immediately (KALRO threshold)"

        elif m < 0.35:
            self._status = "WARNING"
            return "DRY — schedule irrigation within 24 hours"

        elif m < 0.65:
            self._status = "NORMAL"
            return "OPTIMAL — soil moisture within ideal crop range"

        elif m < 0.80:
            self._status = "WARNING"
            return "WET — monitor closely, drainage may be needed"

        else:
            self._status = "ALERT"
            return "WATERLOGGED — activate drainage system"


class TemperatureSensor(Sensor):
    """
    Measures air and soil surface temperature in Celsius.

    Real-world range from Kenyan farm sensor studies:
    Highlands  : 18.0 - 28.0 °C (Embu, Nyeri, Nakuru)
    Lowlands   : 28.0 - 39.5 °C (Kajiado, Tharaka, Garissa)
    Optimal crop temperature: 20.0 - 30.0 °C for most crops
    """

    def __init__(self, sensor_id, zone, timestamp, temperature):
        super().__init__(sensor_id, zone, timestamp)
        self.__temperature = temperature
        self._unit         = "°C"

    def get_reading(self):
        return self.__temperature

    def process_reading(self):
        """
        Classifies temperature using East African crop tolerance ranges.
        Based on KARI (Kenya Agricultural Research Institute) guidelines.
        """
        t = self.__temperature

        if t < 0.0 or t > 60.0:
            self._status = "FAULTY"
            return "INVALID READING — sensor fault detected"

        elif t < 15.0:
            self._status = "ALERT"
            return "COLD STRESS — risk of frost damage to crops"

        elif t < 20.0:
            self._status = "WARNING"
            return "COOL — suboptimal for most Kenyan crop varieties"

        elif t <= 30.0:
            self._status = "NORMAL"
            return "OPTIMAL — ideal temperature range for crop growth"

        elif t <= 35.0:
            self._status = "WARNING"
            return "WARM — monitor crop stress, increase irrigation"

        else:
            self._status = "ALERT"
            return "HEAT STRESS — critical temperature, crops at risk"


class PHSensor(Sensor):
    """
    Measures soil pH (acidity/alkalinity).

    Real-world values from Embu County smallholder farm study:
    Most Kenyan farm soils: pH 4.5 - 7.8
    Optimal for maize/beans: pH 5.5 - 6.8
    Source: PMC sensor evaluation study, Embu Kenya 2016
    """

    def __init__(self, sensor_id, zone, timestamp, ph):
        super().__init__(sensor_id, zone, timestamp)
        self.__ph  = ph
        self._unit = "pH"

    def get_reading(self):
        return self.__ph

    def process_reading(self):
        """
        Classifies soil pH for East African crop suitability.
        pH ranges based on Kenyan soil research (Embu County study).
        """
        ph = self.__ph

        if ph < 0.0 or ph > 14.0:
            self._status = "FAULTY"
            return "INVALID READING — sensor fault detected"

        elif ph < 4.5:
            self._status = "ALERT"
            return "HIGHLY ACIDIC — lime application urgently required"

        elif ph < 5.5:
            self._status = "WARNING"
            return "ACIDIC — consider lime treatment for better yields"

        elif ph <= 6.8:
            self._status = "NORMAL"
            return "OPTIMAL — ideal pH for maize, beans, and vegetables"

        elif ph <= 7.5:
            self._status = "WARNING"
            return "ALKALINE — may limit nutrient availability"

        else:
            self._status = "ALERT"
            return "HIGHLY ALKALINE — soil amendment required"




class SensorDataset:
    """
    Manages a collection of sensor readings as a structured dataset.

    Stores readings in arrays, handles string data formatting,
    and provides statistical analysis across the full dataset.
    Includes recursive anomaly detection.
    """
    # This class demonstrates array operations, string formatting,
    # and statistical computation across a sensor network

    def __init__(self, dataset_name, location):
        self.__name     = dataset_name   # name of this dataset
        self.__location = location       # farm/region name
        self.__sensors  = []             # array of sensor objects
        self.__log      = []             # array of log message strings

    def add_sensor(self, sensor):
        # Add a sensor object to the dataset array
        self.__sensors.append(sensor)
        # Log the addition with a structured string message
        log_entry = f"[{sensor.get_timestamp()}] REGISTERED: {sensor.get_sensor_id()} at {sensor.get_zone()}"
        self.__log.append(log_entry)

    def get_sensor_count(self):
        return len(self.__sensors)

    def process_all(self):
        """
        Loops through all sensors and processes each reading.
        Prints a structured report for the full dataset.
        """
        print(f"\n{'=' * 65}")
        print(f"  DATASET : {self.__name}")
        print(f"  LOCATION: {self.__location}")
        print(f"  SENSORS : {len(self.__sensors)} registered")
        print(f"{'=' * 65}")

        for sensor in self.__sensors:
            # Use verbose=False for compact output (method overloading demo)
            print(f"  {sensor.get_summary(verbose=False)}")

    def detailed_report(self):
        """
        Prints a verbose detailed report for every sensor.
        Demonstrates the verbose=True option of get_summary().
        """
        print(f"\n{'=' * 65}")
        print(f"  DETAILED SENSOR REPORT — {self.__name}")
        print(f"{'=' * 65}")

        for sensor in self.__sensors:
            print()
            print(sensor.get_summary(verbose=True))
            print(f"  {'-' * 60}")

    def compute_moisture_statistics(self, moisture_sensors):
        """
        Computes statistical summary for moisture sensor readings.
        Takes an array of MoistureSensor objects as input.
        Demonstrates structured dataset arithmetic.
        """
        if len(moisture_sensors) == 0:
            print("  No moisture sensors in dataset.")
            return

        readings = [s.get_reading() for s in moisture_sensors]

        # Compute statistics manually without using built-in functions
        total   = 0.0
        highest = readings[0]
        lowest  = readings[0]

        for r in readings:
            total += r
            if r > highest:
                highest = r
            if r < lowest:
                lowest = r

        average = total / len(readings)
        spread  = highest - lowest   # range of moisture across the farm

        print(f"\n{'=' * 65}")
        print(f"  MOISTURE STATISTICS — {self.__location}")
        print(f"{'=' * 65}")
        print(f"  Sensors Analyzed : {len(readings)}")
        print(f"  Average Moisture : {average:.3f} VWC")
        print(f"  Highest Reading  : {highest:.3f} VWC")
        print(f"  Lowest Reading   : {lowest:.3f} VWC")
        print(f"  Moisture Spread  : {spread:.3f} VWC")

        # Classify the farm-wide moisture situation
        if average < 0.20:
            farm_status = "CRITICAL — Large scale irrigation required"
        elif average < 0.35:
            farm_status = "DRY — Irrigation recommended across most zones"
        elif average < 0.65:
            farm_status = "STABLE — Field conditions within acceptable range"
        else:
            farm_status = "WET — Review drainage across farm"

        print(f"  Farm Assessment  : {farm_status}")

    def detect_anomalies_recursive(self, sensors, index=0, anomalies=None):
        """
        RECURSIVE anomaly detection across all sensors.

        Recursion works by processing one sensor at a time,
        then calling itself on the next sensor until all are done.
        An anomaly is any sensor flagged as ALERT or FAULTY
        after processing its reading.

        Base case  : index reaches end of sensors list → return results
        Recursive  : process sensor at current index, move to next
        """
        # Recursion: breaks down problem into smaller subproblems
        # Base case prevents infinite recursion
        # Initialize anomalies list on first call
        if anomalies is None:
            anomalies = []

        # BASE CASE: we have gone through all sensors, stop recursion
        if index >= len(sensors):
            return anomalies

        # Process the current sensor
        current_sensor = sensors[index]
        current_sensor.process_reading()   # trigger classification

        # If sensor is in ALERT or FAULTY state, record it as anomaly
        if current_sensor.get_status() in ["ALERT", "FAULTY"]:
            anomalies.append(current_sensor)

        # RECURSIVE CASE: move to the next sensor
        return self.detect_anomalies_recursive(sensors, index + 1, anomalies)

    def print_log(self):
        """
        Prints all structured log entries stored in the log array.
        Demonstrates string data handling.
        """
        print(f"\n{'=' * 65}")
        print(f"  SYSTEM REGISTRATION LOG — {self.__name}")
        print(f"{'=' * 65}")
        for entry in self.__log:
            print(f"  {entry}")




print("\nSENSOR DATA PROCESSING SYSTEM — MILESTONE 3")
print("Processing real Kenyan farm sensor data")
# Create instances of each sensor type with real field data
# Each sensor object is polymorphic — same interface, different behavior

# Moisture Sensors (10 zones)
# Values represent typical Kenyan dry-season readings
m1  = MoistureSensor("SNS-M01", "North Field A",    "2024-05-01 06:00", 0.32)
m2  = MoistureSensor("SNS-M02", "North Field B",    "2024-05-01 06:00", 0.15)
m3  = MoistureSensor("SNS-M03", "East Greenhouse",  "2024-05-01 06:00", 0.61)
m4  = MoistureSensor("SNS-M04", "East Orchard",     "2024-05-01 06:00", 0.44)
m5  = MoistureSensor("SNS-M05", "Central Paddock",  "2024-05-01 06:00", 0.72)
m6  = MoistureSensor("SNS-M06", "Central Nursery",  "2024-05-01 06:00", 0.28)
m7  = MoistureSensor("SNS-M07", "West Cropland",    "2024-05-01 06:00", 0.53)
m8  = MoistureSensor("SNS-M08", "West Pasture",     "2024-05-01 06:00", 0.81)
m9  = MoistureSensor("SNS-M09", "South Wetland",    "2024-05-01 06:00", 0.13)
m10 = MoistureSensor("SNS-M10", "South Dryland",    "2024-05-01 06:00", 0.47)

# Temperature Sensors (6 zones — highlands and lowlands)
# Highlands: Embu (23.4°C avg), Lowlands: Kajiado (34.1°C avg)
t1 = TemperatureSensor("SNS-T01", "North Field A",   "2024-05-01 06:00", 24.3)
t2 = TemperatureSensor("SNS-T02", "East Greenhouse", "2024-05-01 06:00", 22.1)
t3 = TemperatureSensor("SNS-T03", "Central Paddock", "2024-05-01 06:00", 31.7)
t4 = TemperatureSensor("SNS-T04", "West Cropland",   "2024-05-01 06:00", 36.8)
t5 = TemperatureSensor("SNS-T05", "South Wetland",   "2024-05-01 06:00", 28.4)
t6 = TemperatureSensor("SNS-T06", "South Dryland",   "2024-05-01 06:00", 38.5)

# pH Sensors (5 zones)
# Values from Embu County soil study: typical Kenyan farm soil pH
p1 = PHSensor("SNS-P01", "North Field A",   "2024-05-01 06:00", 6.2)
p2 = PHSensor("SNS-P02", "East Orchard",    "2024-05-01 06:00", 4.8)
p3 = PHSensor("SNS-P03", "Central Nursery", "2024-05-01 06:00", 7.1)
p4 = PHSensor("SNS-P04", "West Cropland",   "2024-05-01 06:00", 5.9)
p5 = PHSensor("SNS-P05", "South Dryland",   "2024-05-01 06:00", 8.1)


# Initialize dataset with farm location and metadata
# Add all sensor objects to the dataset array for batch processing
dataset = SensorDataset(
    "JKUAT Research Farm — May 2024 Morning Reading",
    "Juja, Kiambu County, Kenya"
)

# Add all sensors to the dataset
all_sensors = [m1,m2,m3,m4,m5,m6,m7,m8,m9,m10,
               t1,t2,t3,t4,t5,t6,
               p1,p2,p3,p4,p5]

for sensor in all_sensors:
    dataset.add_sensor(sensor)


# --- RUN THE SYSTEM ---

# 1. Show system registration log
dataset.print_log()

# 2. Process all sensors — compact view
dataset.process_all()

# 3. Moisture statistics
moisture_sensors = [m1,m2,m3,m4,m5,m6,m7,m8,m9,m10]
dataset.compute_moisture_statistics(moisture_sensors)

# 4. Detailed report — verbose mode (method overloading demo)
print("\n\n--- VERBOSE DETAILED REPORT (sample — first 3 sensors) ---")
for sensor in [m1, t1, p1]:
    print()
    print(sensor.get_summary(verbose=True))

# 5. Recursive anomaly detection
print(f"\n{'=' * 65}")
print("  RECURSIVE ANOMALY DETECTION")
print(f"{'=' * 65}")
anomalies = dataset.detect_anomalies_recursive(all_sensors)

if len(anomalies) == 0:
    print("  No anomalies detected across the sensor network.")
else:
    print(f"  {len(anomalies)} anomaly/anomalies detected:\n")
    for sensor in anomalies:
        print(f"  [{sensor.get_status()}] {sensor.get_sensor_id()} — "
              f"{sensor.get_zone()} | Reading: {sensor.get_reading()} | "
              f"{sensor.process_reading()}")

 
print("=" * 65)
