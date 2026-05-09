 


from abc import ABC, abstractmethod   # for interface simulation
import os                             # for file path handling
import datetime                       # for real timestamps on logs

# Modular sensor system with exception handling and file persistence
# Custom exceptions provide specific error types for different failure scenarios

# >>> CUSTOM EXCEPTIONS: Specific exception types for different errors
# >>> Replaces simple if/else with typed exception handling
class SensorException(Exception):
    """Base exception for all sensor system errors."""
    pass

class InvalidReadingError(SensorException):
    """Raised when a sensor reading is outside acceptable range."""
    pass

class SensorOfflineError(SensorException):
    """Raised when a sensor is offline or unresponsive."""
    pass

class FileLoggingError(SensorException):
    """Raised when the system fails to write to a log file."""
    pass


# >>> INTERFACES: IReadable and ILoggable enforce contracts
# >>> Sensor class implements both — get_reading(), validate(), log_to_file()
class IReadable(ABC):
    """
    Interface for any component that provides sensor readings.
    Forces all implementing classes to define get_reading()
    and validate() — ensuring consistent data access patterns.
    """
    @abstractmethod
    def get_reading(self):
        pass

    @abstractmethod
    def validate(self):
        pass


class ILoggable(ABC):
    """
    Interface for any component that supports file logging.
    Forces all implementing classes to define log_to_file()
    so every module can persist its data consistently.
    """
    @abstractmethod
    def log_to_file(self, filepath):
        pass



class Sensor(IReadable, ILoggable):
    """
    Concrete sensor class implementing both interfaces.
    Handles its own validation, processing and file logging.
    Extended from Milestone 3 to add exception handling
    and file persistence.
    """

    def __init__(self, sensor_id, zone, sensor_type, reading, unit, timestamp):
        self.__sensor_id   = sensor_id
        self.__zone        = zone
        self.__sensor_type = sensor_type   # "MOISTURE", "TEMPERATURE", "PH"
        self.__reading     = reading
        self.__unit        = unit
        self.__timestamp   = timestamp
        self.__status      = "ACTIVE"
        self.__assessment  = ""



    def get_reading(self):
        return self.__reading
    def validate(self):
        """
        Validates sensor reading using exception handling.
        Raises specific custom exceptions for different error types.
        This replaces the simple if/else validation from Milestone 2.
        """
        # >>> EXCEPTION HANDLING: Try-except catches specific error types
        # >>> SensorOfflineError, InvalidReadingError each handled separately
        try:
            # Check if the sensor is even online
            if self.__reading is None:
                raise SensorOfflineError(
                    f"Sensor {self.__sensor_id} is offline — no reading received"
                )

            # Validate based on sensor type
            if self.__sensor_type == "MOISTURE":
                if not (0.0 <= self.__reading <= 1.0):
                    raise InvalidReadingError(
                        f"Moisture {self.__reading} out of range (0.0–1.0)"
                    )

            elif self.__sensor_type == "TEMPERATURE":
                if not (0.0 <= self.__reading <= 60.0):
                    raise InvalidReadingError(
                        f"Temperature {self.__reading}°C out of range (0–60°C)"
                    )

            elif self.__sensor_type == "PH":
                if not (0.0 <= self.__reading <= 14.0):
                    raise InvalidReadingError(
                        f"pH {self.__reading} out of range (0–14)"
                    )

            return True   # validation passed

        except InvalidReadingError as e:
            # Reading exists but is out of valid range
            self.__status = "FAULTY"
            print(f"  [VALIDATION ERROR] {self.__sensor_id}: {e}")
            return False

        except SensorOfflineError as e:
            # Sensor sent no reading at all
            self.__status = "OFFLINE"
            print(f"  [SENSOR OFFLINE] {self.__sensor_id}: {e}")
            return False

        except Exception as e:
            # Catch any other unexpected errors
            self.__status = "ERROR"
            print(f"  [UNEXPECTED ERROR] {self.__sensor_id}: {e}")
            return False

    def process(self):
        """
        Processes the reading after validation.
        Wrapped in try/except to handle any processing errors.
        """
        # Try-except wrapping ensures one sensor error doesn’t crash the entire system
        try:
            # Stop processing if validation fails
            if not self.validate():
                return

            if self.__sensor_type == "MOISTURE":
                m = self.__reading
                if m < 0.20:
                    self.__status     = "ALERT"
                    self.__assessment = "CRITICAL DRY — irrigate immediately"
                elif m < 0.35:
                    self.__status     = "WARNING"
                    self.__assessment = "DRY — schedule irrigation within 24hrs"
                elif m < 0.65:
                    self.__status     = "NORMAL"
                    self.__assessment = "OPTIMAL — conditions good"
                elif m < 0.80:
                    self.__status     = "WARNING"
                    self.__assessment = "WET — monitor drainage"
                else:
                    self.__status     = "ALERT"
                    self.__assessment = "WATERLOGGED — activate drainage"

            elif self.__sensor_type == "TEMPERATURE":
                t = self.__reading
                if t < 15.0:
                    self.__status     = "ALERT"
                    self.__assessment = "COLD STRESS — frost risk"
                elif t < 20.0:
                    self.__status     = "WARNING"
                    self.__assessment = "COOL — suboptimal for crops"
                elif t <= 30.0:
                    self.__status     = "NORMAL"
                    self.__assessment = "OPTIMAL — ideal temperature"
                elif t <= 35.0:
                    self.__status     = "WARNING"
                    self.__assessment = "WARM — monitor crop stress"
                else:
                    self.__status     = "ALERT"
                    self.__assessment = "HEAT STRESS — crops at risk"

            elif self.__sensor_type == "PH":
                ph = self.__reading
                if ph < 4.5:
                    self.__status     = "ALERT"
                    self.__assessment = "HIGHLY ACIDIC — lime required urgently"
                elif ph < 5.5:
                    self.__status     = "WARNING"
                    self.__assessment = "ACIDIC — consider lime treatment"
                elif ph <= 6.8:
                    self.__status     = "NORMAL"
                    self.__assessment = "OPTIMAL — ideal for crops"
                elif ph <= 7.5:
                    self.__status     = "WARNING"
                    self.__assessment = "ALKALINE — nutrient availability reduced"
                else:
                    self.__status     = "ALERT"
                    self.__assessment = "HIGHLY ALKALINE — soil amendment required"

        except Exception as e:
            self.__status     = "ERROR"
            self.__assessment = f"Processing failed: {e}"
            print(f"  [PROCESSING ERROR] {self.__sensor_id}: {e}")



    def log_to_file(self, filepath):
        """
        Writes this sensor's reading and assessment to a log file.
        Uses exception handling to manage file I/O errors safely.
        """
        # File I/O wrapped in exception handling to catch write/permission errors
        try:
            # Open file in append mode so each sensor adds to the log
            with open(filepath, "a") as f:
                f.write(
                    f"{self.__timestamp} | {self.__sensor_id} | "
                    f"{self.__zone} | {self.__sensor_type} | "
                    f"{self.__reading} {self.__unit} | "
                    f"{self.__status} | {self.__assessment}\n"
                )

        except PermissionError:
            raise FileLoggingError(
                f"Permission denied writing to {filepath}"
            )
        except OSError as e:
            raise FileLoggingError(
                f"File system error writing log: {e}"
            )

    # Getters
    def get_sensor_id(self):   return self.__sensor_id
    def get_zone(self):        return self.__zone
    def get_type(self):        return self.__sensor_type
    def get_status(self):      return self.__status
    def get_assessment(self):  return self.__assessment
    def get_unit(self):        return self.__unit
    def get_timestamp(self):   return self.__timestamp



class FileLogger(ILoggable):
    """
    Handles all file logging operations for the sensor system.
    Creates, writes, and reads system log files.
    Implements ILoggable interface.
    """
    # Dedicated module for file I/O — separates concerns from sensor logic
    # >>> THREE LOG FILES: sensor_readings.txt, alerts.txt, daily_summary.txt
    def __init__(self, log_directory):
        self.__log_dir        = log_directory
        self.__readings_file  = os.path.join(log_directory, "sensor_readings.txt")
        self.__alerts_file    = os.path.join(log_directory, "alerts.txt")
        self.__summary_file   = os.path.join(log_directory, "daily_summary.txt")
        self.__initialize_logs()

    def __initialize_logs(self):
        """
        Creates the log directory and initializes log files
        with headers. Uses exception handling for safety.
        """
        try:
            # Create log directory if it doesn't exist
            os.makedirs(self.__log_dir, exist_ok=True)

            # Write header to readings log
            with open(self.__readings_file, "w") as f:
                f.write("=" * 80 + "\n")
                f.write("  SENSOR DATA PROCESSING SYSTEM — READINGS LOG\n")
                f.write(f"  Generated: {datetime.datetime.now()}\n")
                f.write(f"  Farm: JKUAT Research Farm, Juja, Kenya\n")
                f.write("=" * 80 + "\n")
                f.write(
                    "TIMESTAMP            | SENSOR ID  | ZONE               | "
                    "TYPE        | READING    | STATUS  | ASSESSMENT\n"
                )
                f.write("-" * 80 + "\n")

            # Write header to alerts log
            with open(self.__alerts_file, "w") as f:
                f.write("=" * 80 + "\n")
                f.write("  SENSOR DATA PROCESSING SYSTEM — ALERTS LOG\n")
                f.write(f"  Generated: {datetime.datetime.now()}\n")
                f.write("=" * 80 + "\n")

            print(f"  Log files initialized in: {self.__log_dir}")

        except OSError as e:
            raise FileLoggingError(f"Failed to initialize log directory: {e}")

    def log_to_file(self, filepath):
        """Implements ILoggable — logs a system event."""
        try:
            with open(filepath, "a") as f:
                f.write(f"[{datetime.datetime.now()}] System log entry\n")
        except OSError as e:
            raise FileLoggingError(f"Failed to write log: {e}")

    def log_sensor(self, sensor):
        """Logs a single sensor's data to the readings file."""
        try:
            sensor.log_to_file(self.__readings_file)
        except FileLoggingError as e:
            print(f"  [LOG ERROR] Could not log {sensor.get_sensor_id()}: {e}")

    def log_alert(self, sensor):
        """Logs an alert sensor to the dedicated alerts file."""
        try:
            with open(self.__alerts_file, "a") as f:
                f.write(
                    f"[ALERT] {sensor.get_timestamp()} | "
                    f"{sensor.get_sensor_id()} | {sensor.get_zone()} | "
                    f"{sensor.get_type()} | {sensor.get_reading()} "
                    f"{sensor.get_unit()} | {sensor.get_assessment()}\n"
                )
        except OSError as e:
            raise FileLoggingError(f"Failed to write alert: {e}")

    def write_daily_summary(self, sensors, total_alerts, total_warnings):
        """
        Writes a complete daily summary report to file.
        Demonstrates file creation and structured data writing.
        """
        try:
            with open(self.__summary_file, "w") as f:
                f.write("=" * 80 + "\n")
                f.write("  DAILY SUMMARY REPORT — JKUAT RESEARCH FARM\n")
                f.write(f"  Date     : {datetime.datetime.now().strftime('%Y-%m-%d')}\n")
                f.write(f"  Location : Juja, Kiambu County, Kenya\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"  Total Sensors   : {len(sensors)}\n")
                f.write(f"  Total Alerts    : {total_alerts}\n")
                f.write(f"  Total Warnings  : {total_warnings}\n")
                f.write(f"  Total Normal    : {len(sensors) - total_alerts - total_warnings}\n\n")
                f.write("  SENSOR BREAKDOWN:\n")
                f.write("  " + "-" * 70 + "\n")

                for sensor in sensors:
                    f.write(
                        f"  {sensor.get_sensor_id():<12} | "
                        f"{sensor.get_zone():<20} | "
                        f"{sensor.get_status():<8} | "
                        f"{sensor.get_assessment()}\n"
                    )

                f.write("\n" + "=" * 80 + "\n")
                f.write("  END OF DAILY SUMMARY\n")
                f.write("=" * 80 + "\n")

            print(f"  Daily summary written to: {self.__summary_file}")

        except OSError as e:
            raise FileLoggingError(f"Failed to write daily summary: {e}")

    def read_log_preview(self, num_lines=8):
        """
        Reads back the first few lines of the readings log.
        Demonstrates file reading capability.
        """
        try:
            print(f"\n  --- Log File Preview ({self.__readings_file}) ---")
            with open(self.__readings_file, "r") as f:
                lines = f.readlines()
                for line in lines[:num_lines]:
                    print(f"  {line}", end="")
            print(f"  ... ({len(lines)} total lines in log)")

        except FileNotFoundError:
            print(f"  [ERROR] Log file not found: {self.__readings_file}")
        except OSError as e:
            print(f"  [ERROR] Could not read log: {e}")

    def get_readings_filepath(self):
        return self.__readings_file

    def get_alerts_filepath(self):
        return self.__alerts_file

    def get_summary_filepath(self):
        return self.__summary_file


class SensorNetwork:
    """
    Top-level system coordinator.
    Manages all sensors, runs the processing pipeline,
    and delegates file logging to the FileLogger module.
    This is the modular architecture in action — each concern
    is handled by a dedicated, specialized module.
    """
    # >>> MODULAR ARCHITECTURE: SensorNetwork orchestrates Sensor + FileLogger
    # >>> Separation of concerns — each class handles one responsibility

    def __init__(self, network_name, location, logger):
        self.__name     = network_name
        self.__location = location
        self.__logger   = logger      # injected FileLogger module
        self.__sensors  = []          # sensor array

    def register_sensor(self, sensor):
        """Adds a sensor to the network with error handling."""
        try:
            if sensor is None:
                raise SensorException("Cannot register a null sensor object")
            self.__sensors.append(sensor)
        except SensorException as e:
            print(f"  [REGISTRATION ERROR] {e}")

    def run_processing_cycle(self):
        """
        Main processing pipeline.
        Processes every sensor, logs each result, collects alerts.
        Demonstrates the full exception handling framework in action.
        """
        # >>> EXCEPTION HANDLING IN ACTION: Try-except wraps entire loop
        # >>> System continues processing even if individual sensors fail
        print(f"\n{'=' * 65}")
        print(f"  SENSOR NETWORK: {self.__name}")
        print(f"  LOCATION      : {self.__location}")
        print(f"  SENSORS       : {len(self.__sensors)}")
        print(f"{'=' * 65}")

        alerts   = []
        warnings = []

        for sensor in self.__sensors:
            try:
                # Process the sensor reading
                sensor.process()

                # Log every sensor to the readings file
                self.__logger.log_sensor(sensor)

                # Collect alerts separately
                if sensor.get_status() == "ALERT":
                    alerts.append(sensor)
                    self.__logger.log_alert(sensor)
                elif sensor.get_status() == "WARNING":
                    warnings.append(sensor)

                # Print result to console
                print(
                    f"  [{sensor.get_status():<7}] "
                    f"{sensor.get_sensor_id():<10} | "
                    f"{sensor.get_zone():<20} | "
                    f"{sensor.get_reading()} {sensor.get_unit():<5} | "
                    f"{sensor.get_assessment()}"
                )

            except SensorException as e:
                # Catch any sensor-specific errors
                print(f"  [SENSOR ERROR] {sensor.get_sensor_id()}: {e}")

            except Exception as e:
                # Catch any unexpected errors — system must keep running
                print(f"  [UNEXPECTED ERROR] {sensor.get_sensor_id()}: {e}")

        # Print cycle summary
        print(f"\n  CYCLE SUMMARY:")
        print(f"  Alerts   : {len(alerts)}")
        print(f"  Warnings : {len(warnings)}")
        print(f"  Normal   : {len(self.__sensors) - len(alerts) - len(warnings)}")

        # Write daily summary to file
        try:
            self.__logger.write_daily_summary(
                self.__sensors, len(alerts), len(warnings)
            )
        except FileLoggingError as e:
            print(f"  [LOGGING ERROR] Could not write summary: {e}")

        return alerts, warnings

    def get_sensor_count(self):
        return len(self.__sensors)




print("\nSENSOR DATA PROCESSING SYSTEM — MILESTONE 4")
print("Modular architecture with exception handling and file logging")
# Initialize system: FileLogger creates log directory and files, then SensorNetwork registers sensors

try:
    # Initialize the FileLogger module
    logger = FileLogger("sensor_logs")
except FileLoggingError as e:
    print(f"  [CRITICAL] Logger failed to initialize: {e}")
    exit(1)

# Initialize the SensorNetwork module
network = SensorNetwork(
    "JKUAT Research Farm Network",
    "Juja, Kiambu County, Kenya",
    logger
)

print("\nRegistering sensors...")

# All sensors created and registered to the network
# Each sensor stores: ID, zone, type (MOISTURE/TEMPERATURE/PH), reading value, unit, timestamp
sensors_data = [
    # (sensor_id, zone, type, reading, unit, timestamp)
    ("SNS-M01", "North Field A",    "MOISTURE",    0.32, "VWC", "2024-05-01 06:00"),
    ("SNS-M02", "North Field B",    "MOISTURE",    0.15, "VWC", "2024-05-01 06:00"),
    ("SNS-M03", "East Greenhouse",  "MOISTURE",    0.61, "VWC", "2024-05-01 06:00"),
    ("SNS-M04", "East Orchard",     "MOISTURE",    0.44, "VWC", "2024-05-01 06:00"),
    ("SNS-M05", "Central Paddock",  "MOISTURE",    0.72, "VWC", "2024-05-01 06:00"),
    ("SNS-M06", "Central Nursery",  "MOISTURE",    0.28, "VWC", "2024-05-01 06:00"),
    ("SNS-M07", "West Cropland",    "MOISTURE",    0.53, "VWC", "2024-05-01 06:00"),
    ("SNS-M08", "West Pasture",     "MOISTURE",    0.81, "VWC", "2024-05-01 06:00"),
    ("SNS-M09", "South Wetland",    "MOISTURE",    0.13, "VWC", "2024-05-01 06:00"),
    ("SNS-M10", "South Dryland",    "MOISTURE",    1.45, "VWC", "2024-05-01 06:00"),  # >>> FAULTY: 1.45 exceeds valid range 0.0-1.0
    ("SNS-T01", "North Field A",    "TEMPERATURE", 24.3, "°C",  "2024-05-01 06:00"),
    ("SNS-T02", "East Greenhouse",  "TEMPERATURE", 22.1, "°C",  "2024-05-01 06:00"),
    ("SNS-T03", "Central Paddock",  "TEMPERATURE", 31.7, "°C",  "2024-05-01 06:00"),
    ("SNS-T04", "West Cropland",    "TEMPERATURE", 36.8, "°C",  "2024-05-01 06:00"),
    ("SNS-T05", "South Wetland",    "TEMPERATURE", 28.4, "°C",  "2024-05-01 06:00"),
    ("SNS-T06", "South Dryland",    "TEMPERATURE", 38.5, "°C",  "2024-05-01 06:00"),
    ("SNS-P01", "North Field A",    "PH",          6.2,  "pH",  "2024-05-01 06:00"),
    ("SNS-P02", "East Orchard",     "PH",          4.8,  "pH",  "2024-05-01 06:00"),
    ("SNS-P03", "Central Nursery",  "PH",          7.1,  "pH",  "2024-05-01 06:00"),
    ("SNS-P04", "West Cropland",    "PH",          5.9,  "pH",  "2024-05-01 06:00"),
    ("SNS-P05", "South Dryland",    "PH",          8.1,  "pH",  "2024-05-01 06:00"),
]

for data in sensors_data:
    s = Sensor(data[0], data[1], data[2], data[3], data[4], data[5])
    network.register_sensor(s)

print(f"  {network.get_sensor_count()} sensors registered successfully")

# Execute main processing cycle: validate each sensor, assess status, log results
# Exception handling ensures system robustness even with faulty or offline sensors
alerts, warnings = network.run_processing_cycle()

if alerts:
    print(f"\n{'=' * 65}")
    print(f"  ACTIVE ALERTS — {len(alerts)} sensor(s) require immediate attention")
    print(f"{'=' * 65}")
    for sensor in alerts:
        print(
            f"  ⚠ {sensor.get_sensor_id()} | {sensor.get_zone()} | "
            f"{sensor.get_reading()} {sensor.get_unit()} | {sensor.get_assessment()}"
        )

logger.read_log_preview(num_lines=10)

print(f"\n  Log files saved:")
print(f"  → {logger.get_readings_filepath()}")
print(f"  → {logger.get_alerts_filepath()}")
print(f"  → {logger.get_summary_filepath()}")

 
print("=" * 65)
