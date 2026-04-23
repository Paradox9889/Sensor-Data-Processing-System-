# SENSOR DATA PROCESSING SYSTEM
# Milestone 2: Object-Oriented Design
 
# In Milestone 2, we improve the system by introducing OOP.
# We model each sensor as an object with its own data and behavior.

class Sensor:
    def __init__(self, sensor_id, moisture, temperature, rainfall):
        self.sensor_id = sensor_id
        self.moisture = moisture
        self.temperature = temperature
        self.rainfall = rainfall
        self.status = "ACTIVE"
 
    # This method ensures the sensor readings are valid
    def validate(self):
        if not (0.0 <= self.moisture <= 1.0):
            self.status = "FAULTY"
            return False
        if not (0 <= self.temperature <= 60):
            self.status = "FAULTY"
            return False
        return True

     
    # This method processes the data and generates decisions
    def process(self):
        if not self.validate():
            print(f"[{self.sensor_id}] Faulty sensor detected")
            return

        if self.moisture < 0.2:
            condition = "DRY"
            action = "Irrigate immediately"
        elif self.moisture < 0.4:
            condition = "LOW"
            action = "Irrigate soon"
        elif self.moisture < 0.7:
            condition = "OPTIMAL"
            action = "No action"
        else:
            condition = "HIGH"
            action = "Check drainage"

        print(f"[{self.sensor_id}] {condition} -> {action}")

        if self.temperature > 35:
            print(f"[{self.sensor_id}] High temperature warning")

        if self.rainfall < 10:
            print(f"[{self.sensor_id}] Low rainfall detected")

    
    # This simulates new incoming sensor data
    def update(self, moisture, temperature, rainfall):
        self.moisture = moisture
        self.temperature = temperature
        self.rainfall = rainfall


#  Simulation 
 
# We simulate multiple sensors to represent a real farm environment

print("\n SENSOR SIMULATION ")

sensors = [
    Sensor("S1", 0.35, 28.5, 12.4),
    Sensor("S2", 0.18, 31.0, 5.0),
    Sensor("S3", 0.72, 26.5, 20.1),
    Sensor("S4", 1.5, 29.0, 8.3)  # faulty sensor
]

print("\n Processing Sensors ")
for s in sensors:
    s.process()

#  Update cycle 
print("\n Updating Sensors with new data ")
sensors[0].update(0.25, 30.0, 6.0)
sensors[1].update(0.45, 28.0, 15.0)

for s in sensors[:2]:
    s.process()
