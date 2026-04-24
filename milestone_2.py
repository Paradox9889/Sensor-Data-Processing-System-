# MILESTONE 2 - BUILDING WITH CLASSES
import random

# Using the same data from Milestone 1
farm_name = "Kenyatta Agricultural Research Farm"
total_sensors = 10
current_cycle = 1
total_cycles = 3

THRESHOLD_DRY      = 0.20
THRESHOLD_LOW      = 0.40
THRESHOLD_OPTIMAL  = 0.70
THRESHOLD_TEMP_HIGH = 35.0
THRESHOLD_RAIN_LOW  = 5.0

sensor_ids = [
    "SNS-001", "SNS-002", "SNS-003", "SNS-004", "SNS-005",
    "SNS-006", "SNS-007", "SNS-008", "SNS-009", "SNS-010"
]

zone_names = [
    "North Field A",  "North Field B",  "East Greenhouse",
    "East Orchard",   "Central Paddock", "Central Nursery",
    "West Cropland",  "West Pasture",   "South Wetland",
    "South Dryland"
]

moisture_readings = [0.35, 0.18, 0.62, 0.45, 0.71, 0.29, 0.55, 0.83, 0.14, 0.48]
temperature_readings = [28.5, 36.2, 24.1, 30.4, 27.8, 25.5, 31.0, 22.9, 29.3, 38.7]
rainfall_readings = [12.4, 3.1, 18.6, 9.2, 7.5, 14.8, 6.3, 21.0, 2.8, 4.5]

print(f"\nMILESTONE 2 - OBJECT-ORIENTED SENSOR SYSTEM\n")


 
class Sensor:
    """A single sensor that tracks moisture, temp, and rainfall at one farm location."""

    def __init__(self, sensor_id, zone, moisture, temperature, rainfall):
        self.__sensor_id    = sensor_id
        self.__zone         = zone
        self.__moisture     = moisture
        self.__temperature  = temperature
        self.__rainfall     = rainfall
        self.__status       = "ACTIVE"
        self.__alert        = False
        self.__cycle_count  = 0

    def validate_reading(self):
        # Check if the readings make sense - catch sensor errors
        if self.__moisture < 0.0 or self.__moisture > 1.0:
            self.__status = "FAULTY"
            print(f"  [{self.__sensor_id}] ERROR: Moisture {self.__moisture} is out of range")
            return False
        if self.__temperature < 0.0 or self.__temperature > 60.0:
            self.__status = "FAULTY"
            print(f"  [{self.__sensor_id}] ERROR: Temperature {self.__temperature}°C is unrealistic")
            return False
        if self.__rainfall < 0.0:
            self.__status = "FAULTY"
            print(f"  [{self.__sensor_id}] ERROR: Rainfall can't be negative")
            return False
        return True

    def process_reading(self):
        if not self.validate_reading():
            return "INVALID"
        self.__cycle_count += 1
        
        # Decide what the soil moisture level means
        if self.__moisture < THRESHOLD_DRY:
            moisture_class = "CRITICAL DRY"
            action         = "Irrigate immediately"
            self.__alert   = True
            self.__status  = "ALERT"
        elif self.__moisture < THRESHOLD_LOW:
            moisture_class = "DRY"
            action         = "Schedule irrigation soon"
            self.__status  = "WARNING"
        elif self.__moisture < THRESHOLD_OPTIMAL:
            moisture_class = "OPTIMAL"
            action         = "Looks good"
            self.__status  = "NORMAL"
        else:
            moisture_class = "WATERLOGGED"
            action         = "Check drainage"
            self.__status  = "WARNING"
        
        # Add temperature info to the result
        if self.__temperature > THRESHOLD_TEMP_HIGH:
            temp_note = f" | HEAT ALERT: {self.__temperature}°C"
        else:
            temp_note = f" | {self.__temperature}°C"
        return f"{moisture_class:<14} | {action}{temp_note}"

    def update_reading(self, new_moisture, new_temperature, new_rainfall):
        # Update the sensor with new readings for the next cycle
        self.__moisture    = new_moisture
        self.__temperature = new_temperature
        self.__rainfall    = new_rainfall
        self.__status      = "ACTIVE"
        self.__alert       = False

    # Methods to get the sensor's information
    def get_sensor_id(self):
        return self.__sensor_id
    def get_zone(self):
        return self.__zone
    def get_moisture(self):
        return self.__moisture
    def get_temperature(self):
        return self.__temperature
    def get_rainfall(self):
        return self.__rainfall
    def get_status(self):
        return self.__status
    def get_alert(self):
        return self.__alert
    def get_cycle_count(self):
        return self.__cycle_count


# CREATE ALL THE SENSORS
sensor_network = []
for i in range(total_sensors):
    sensor = Sensor(
        sensor_ids[i],
        zone_names[i],
        moisture_readings[i],
        temperature_readings[i],
        rainfall_readings[i]
    )
    sensor_network.append(sensor)
print(f"Sensor network ready: {len(sensor_network)} sensors online\n")


# RUN THE SIMULATION
random.seed(42)
for cycle in range(1, total_cycles + 1):
    print(f"{'=' * 70}")
    print(f"CYCLE {cycle} of {total_cycles}")
    print(f"{'=' * 70}")
    print(f"{'ID':<10} {'Zone':<20} {'M':>5}  {'Result'}")
    print("-" * 70)

    # Track what happens this cycle
    alerts_this_cycle   = 0
    warnings_this_cycle = 0
    total_moist_cycle   = 0.0
    
    # Check each sensor
    for sensor in sensor_network:
        result = sensor.process_reading()
        print(f"{sensor.get_sensor_id():<10} {sensor.get_zone():<20} {sensor.get_moisture():>5}  {result}")
        if sensor.get_alert():
            alerts_this_cycle += 1
        if sensor.get_status() == "WARNING":
            warnings_this_cycle += 1
        total_moist_cycle += sensor.get_moisture()
    
    # Calculate average for all sensors
    cycle_avg_moisture = total_moist_cycle / len(sensor_network)
    print(f"\nCycle {cycle} Summary:")
    print(f"  Average Moisture: {cycle_avg_moisture:.2f}")
    print(f"  Critical Alerts: {alerts_this_cycle} zone(s)")
    print(f"  Warnings: {warnings_this_cycle} zone(s)")

    if cycle_avg_moisture < THRESHOLD_LOW:
        print(f"  Decision: Activate full irrigation network")
    elif cycle_avg_moisture > THRESHOLD_OPTIMAL:
        print(f"  Decision: Inspect drainage across all zones")
    else:
        print(f"  Decision: Continue routine monitoring")

    if cycle < total_cycles:
        print(f"\nGetting new readings for Cycle {cycle + 1}...")
        for sensor in sensor_network:
            new_m = round(random.uniform(0.10, 0.90), 2)
            new_t = round(random.uniform(22.0, 40.0), 1)
            new_r = round(random.uniform(0.0,  25.0), 1)
            sensor.update_reading(new_m, new_t, new_r)
    print()


# FINAL REPORT
print(f"{'=' * 70}")
print("MILESTONE 2 - FINAL SENSOR NETWORK STATUS")
print(f"{'=' * 70}")
print(f"{'ID':<10} {'Zone':<20} {'Status':<12} {'Cycles Run'}")
print("-" * 70)
for sensor in sensor_network:
    print(f"{sensor.get_sensor_id():<10} {sensor.get_zone():<20} {sensor.get_status():<12} {sensor.get_cycle_count()}")
print(f"\nTotal sensors processed: {len(sensor_network)}")
print(f"Total cycles completed: {total_cycles}")
print(f"{'=' * 70}")