
#Farm Sensor Monitoring System
#This program simulates a farm with 10 sensors spread across different zones.
#Each sensor tracks moisture, temperature, and rainfall. We analyze the data
#to tell the farmer which areas need water and which might be getting too much.

import random  # generates random sensor readings for cycles 2 and 3


# MILESTONE 1 - BUILDING THE BASICS


# SETTING UP THE SYSTEM

farm_name = "Kenyatta Agricultural Research Farm"
total_sensors = 10
current_cycle = 1  # which reading we're on
total_cycles = 3   # we'll check the farm 3 times

# Flag to track if something is wrong on the farm
system_alert = False

# These numbers help us decide if soil is too dry or too wet
# Soil moisture goes from 0 (bone dry) to 1 (waterlogged)
THRESHOLD_DRY      = 0.20   # anything below this = emergency
THRESHOLD_LOW      = 0.40   # below this = we should water
THRESHOLD_OPTIMAL  = 0.70   # below this = looks good
                             # above 0.70 = too much water

THRESHOLD_TEMP_HIGH = 35.0   # crops don't like it hotter than this
THRESHOLD_RAIN_LOW  = 5.0    # less than this means drought conditions


# SENSOR NETWORK DATA

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

# Starting moisture levels for each zone (0 to 1 scale)
moisture_readings = [0.35, 0.18, 0.62, 0.45, 0.71,
                     0.29, 0.55, 0.83, 0.14, 0.48]

# Temperature readings at each sensor location (°C)
temperature_readings = [28.5, 36.2, 24.1, 30.4, 27.8,
                        25.5, 31.0, 22.9, 29.3, 38.7]

# How much rain each location got (millimeters)
rainfall_readings = [12.4, 3.1, 18.6, 9.2, 7.5,
                     14.8, 6.3, 21.0, 2.8, 4.5]


# STARTING THE SYSTEM

print("\nSENSOR DATA PROCESSING SYSTEM")
print(f"Farm: {farm_name}")
print(f"Sensors: {total_sensors} deployed | Cycles: {total_cycles}")
print("-" * 50)

print("\nRegistered Sensors:")
for i in range(total_sensors):
    print(f"  {sensor_ids[i]} • {zone_names[i]}")
print(f"Status: All {total_sensors} sensors online\n")


# ANALYZING THE DATA

print("\nCYCLE 1 - INITIAL ANALYSIS")
print("-" * 50)

# Moisture Analysis - figure out which areas are driest and wettest
total_moisture  = 0.0
highest_moisture = moisture_readings[0]
lowest_moisture  = moisture_readings[0]
driest_zone      = zone_names[0]
wettest_zone     = zone_names[0]

for i in range(total_sensors):
    total_moisture += moisture_readings[i]
    if moisture_readings[i] > highest_moisture:
        highest_moisture = moisture_readings[i]
        wettest_zone     = zone_names[i]
    if moisture_readings[i] < lowest_moisture:
        lowest_moisture = moisture_readings[i]
        driest_zone     = zone_names[i]

average_moisture = total_moisture / total_sensors
print(f"\nMoisture:")
print(f"  Average: {average_moisture:.2f} | High: {highest_moisture} ({wettest_zone}) | Low: {lowest_moisture} ({driest_zone})")


# Temperature Analysis - same thing for heat
total_temperature   = 0.0
highest_temperature = temperature_readings[0]
lowest_temperature  = temperature_readings[0]
hottest_zone        = zone_names[0]
coolest_zone        = zone_names[0]
for i in range(total_sensors):
    total_temperature += temperature_readings[i]
    if temperature_readings[i] > highest_temperature:
        highest_temperature = temperature_readings[i]
        hottest_zone        = zone_names[i]
    if temperature_readings[i] < lowest_temperature:
        lowest_temperature = temperature_readings[i]
        coolest_zone       = zone_names[i]
average_temperature = total_temperature / total_sensors
print(f"Temperature:")
print(f"  Average: {average_temperature:.1f}°C | High: {highest_temperature}°C ({hottest_zone}) | Low: {lowest_temperature}°C ({coolest_zone})")


# Rainfall Analysis
total_rainfall  = 0.0
highest_rainfall = rainfall_readings[0]
lowest_rainfall  = rainfall_readings[0]
for i in range(total_sensors):
    total_rainfall += rainfall_readings[i]
    if rainfall_readings[i] > highest_rainfall:
        highest_rainfall = rainfall_readings[i]
    if rainfall_readings[i] < lowest_rainfall:
        lowest_rainfall = rainfall_readings[i]
average_rainfall = total_rainfall / total_sensors
print(f"Rainfall:")
print(f"  Total: {total_rainfall:.1f}mm | Average: {average_rainfall:.1f}mm | Range: {lowest_rainfall}-{highest_rainfall}mm")



# CHECK EACH ZONE

print(f"\nZone Status:")
print(f"{'ID':<10} {'Zone':<20} {'Moisture':<10} {'Status':<12} {'Action'}")
print("-" * 70)

# Counter to track how many zones need irrigation
zones_needing_irrigation = 0

for i in range(total_sensors):

    moisture = moisture_readings[i]

    # Decide what action to take based on soil moisture level
    if moisture < THRESHOLD_DRY:
        # This zone is in trouble - needs water NOW
        moisture_status = "CRITICAL"
        action          = "Irrigate immediately"
        system_alert    = True
        zones_needing_irrigation += 1

    elif moisture < THRESHOLD_LOW:
        # Getting dry - schedule watering
        moisture_status = "DRY"
        action          = "Schedule irrigation"
        zones_needing_irrigation += 1

    elif moisture < THRESHOLD_OPTIMAL:
        # Perfect - soil has enough water
        moisture_status = "OPTIMAL"
        action          = "No action needed"

    else:
        # Too wet - could cause problems with roots
        moisture_status = "WATERLOGGED"
        action          = "Check drainage"

    print(f"{sensor_ids[i]:<10} {zone_names[i]:<20} {moisture:<10} {moisture_status:<12} {action}")



# SIMULATE WHAT HAPPENS NEXT
print(f"\nSimulation Results:")
print("-" * 70)

# Use a seed so the random readings are the same every time we run the code
random.seed(99)

# Now simulate cycles 2 and 3 with random sensor readings
for cycle in range(2, total_cycles + 1):

    print(f"\nCycle {cycle}:")
    cycle_moisture     = [round(random.uniform(0.10, 0.90), 2) for _ in range(total_sensors)]
    cycle_temperature  = [round(random.uniform(22.0, 40.0), 1) for _ in range(total_sensors)]
    cycle_rainfall     = [round(random.uniform(0.0,  25.0), 1) for _ in range(total_sensors)]
    avg_moist = sum(cycle_moisture) / total_sensors
    avg_temp  = sum(cycle_temperature) / total_sensors
    avg_rain  = sum(cycle_rainfall) / total_sensors
    print(f"  Avg Moisture: {avg_moist:.2f} | Avg Temp: {avg_temp:.1f}°C | Avg Rain: {avg_rain:.1f}mm")
    critical_count = sum(1 for m in cycle_moisture if m < THRESHOLD_DRY)
    print(f"  Critical Zones: {critical_count}")
    if avg_moist < THRESHOLD_LOW:
        print(f"  Decision: Activate irrigation network")
    elif avg_moist > THRESHOLD_OPTIMAL:
        print(f"  Decision: Monitor drainage")
    else:
        print(f"  Decision: Continue routine monitoring")



# FINAL REPORT

print(f"\n{'=' * 70}")
print("MILESTONE 1 - FINAL SYSTEM REPORT")
print(f"{'=' * 70}")
print(f"Farm: {farm_name}")
print(f"Sensors: {total_sensors} | Cycles: {total_cycles}")
print(f"Zones Needing Irrigation: {zones_needing_irrigation}")
print(f"System Alert: {'YES - Critical conditions' if system_alert else 'NO'}")
print(f"Temp Alert: {'YES - {:.1f}°C exceeds threshold'.format(average_temperature) if average_temperature > THRESHOLD_TEMP_HIGH else 'NO - {:.1f}°C safe'.format(average_temperature)}")
print(f"Rainfall: {'CRITICAL - {:.1f}mm'.format(average_rainfall) if average_rainfall < THRESHOLD_RAIN_LOW else 'Adequate - {:.1f}mm'.format(average_rainfall)}")
print(f"{'=' * 70}")
