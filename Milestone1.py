# SENSOR DATA PROCESSING SYSTEM
# Milestone 1: Computational Foundations
# In Milestone 1, we focus on basic computation.
# We simulate sensor readings and process them using simple logic.

sensor_id = "SENSOR_001"
moisture_level = 0.35
temperature = 28.5
rainfall = 12.4

print("\n SENSOR SYSTEM INITIALIZATION ")
print(f"Sensor ID      : {sensor_id}")
print(f"Moisture Level : {moisture_level}")
print(f"Temperature    : {temperature} °C")
print(f"Rainfall       : {rainfall} mm")

#  Data Analysis 
# Here we analyze multiple moisture readings to understand field condition

moisture_readings = [0.35, 0.42, 0.28, 0.51, 0.39]

average = sum(moisture_readings) / len(moisture_readings)
highest = max(moisture_readings)
lowest = min(moisture_readings)

print("\n  Moisture Analysis")
print(f"Readings : {moisture_readings}")
print(f"Average  : {average:.2f}")
print(f"Highest  : {highest}")
print(f"Lowest   : {lowest}")

# Classification 
# We classify moisture levels into agricultural categories

print("\n Classification ")
for i, m in enumerate(moisture_readings):
    if m < 0.2:
        label = "DRY"
    elif m < 0.4:
        label = "LOW"
    elif m < 0.7:
        label = "OPTIMAL"
    else:
        label = "HIGH"
    print(f"Reading {i+1}: {m} -> {label}")



#  Decision 
# Based on the processed data, the system makes simple decisions

print("\n  Decision ")

if moisture_level < 0.4:
    print("Irrigation needed")
else:
    print("Moisture sufficient")

if temperature > 35:
    print("High temperature warning")

if rainfall < 10:
    print("Low rainfall detected")
