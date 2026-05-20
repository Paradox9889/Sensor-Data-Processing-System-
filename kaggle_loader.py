"""
Kaggle Dataset Loader for Sensor Data Processing System

This module loads agricultural sensor data from the Kaggle Crop Recommendation
dataset and converts it into sensor-compatible format for the multithreaded
processing pipeline.

Global dataset source:
- Kaggle Crop Recommendation Dataset (compiled by Atharva Ingle)
- Synthetic/aggregated agricultural data with soil, environmental, and crop parameters
- Used to validate system scalability with real-world sensor volumes
"""

import csv
from datetime import datetime


def load_kaggle_sensors(csv_file="kaggle_dataset.csv", limit=1000):
    """
    Loads Kaggle CSV and generates 3 sensors per row (MOISTURE, TEMPERATURE, PH).
    
    Args:
        csv_file (str): Path to kaggle_dataset.csv
        limit (int): Number of rows to process (default 1000)
    
    Returns:
        list: Sensor data dictionaries with structure:
              {
                  "sensor_id": "KAGGLE-00001-M",
                  "zone": "Kaggle Zone 1",
                  "sensor_type": "MOISTURE",
                  "reading": 0.294,
                  "unit": "VWC",
                  "timestamp": "2024-05-01",
                  "alert_triggered": False,
                  "anomaly": None
              }
    
    Scaling: 1000 rows × 3 sensors = 3000 sensor readings
    """
    
    sensors = []
    row_count = 0
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    try:
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                if row_count >= limit:
                    break
                
                # Strip whitespace from all column names in the row
                row = {k.strip(): v for k, v in row.items()}
                
                # Extract sensor values from Kaggle columns
                try:
                    soil_moisture_pct = float(row['soil_moisture'])  # 10-30 range
                    temperature = float(row['temperature'])            # Celsius
                    ph = float(row['ph'])                             # pH scale
                    pest_pressure = float(row['pest_pressure'])       # 0-99%
                    frost_risk = float(row['frost_risk'])             # 0-98%
                    crop_label = row.get('label', 'unknown')
                    
                except (ValueError, KeyError) as e:
                    print(f"  [WARNING] Row {row_count}: Skipping due to missing/invalid data: {e}")
                    continue
                
                # Generate unique zone name from crop type
                zone = f"Kaggle-{crop_label.capitalize()}-{row_count + 1}"
                
                # === SENSOR 1: MOISTURE ===
                # Normalize soil_moisture from 10-30% range to 0-1 VWC scale
                moisture_normalized = soil_moisture_pct / 100.0
                
                moisture_alert = False
                moisture_anomaly = None
                
                # Check for anomalies based on pest_pressure and frost_risk
                if pest_pressure > 80:
                    moisture_anomaly = f"HIGH PEST PRESSURE ({pest_pressure}%)"
                    moisture_alert = True
                
                sensors.append({
                    "sensor_id": f"KAGGLE-{row_count + 1:05d}-M",
                    "zone": zone,
                    "sensor_type": "MOISTURE",
                    "reading": round(moisture_normalized, 3),
                    "unit": "VWC",
                    "timestamp": timestamp,
                    "alert_triggered": moisture_alert,
                    "anomaly": moisture_anomaly
                })
                
                # === SENSOR 2: TEMPERATURE ===
                temp_alert = False
                temp_anomaly = None
                
                if temperature > 40:
                    temp_anomaly = "EXTREME HEAT"
                    temp_alert = True
                elif frost_risk > 70:
                    temp_anomaly = f"FROST RISK ({frost_risk}%)"
                    temp_alert = True
                
                sensors.append({
                    "sensor_id": f"KAGGLE-{row_count + 1:05d}-T",
                    "zone": zone,
                    "sensor_type": "TEMPERATURE",
                    "reading": round(temperature, 1),
                    "unit": "C",
                    "timestamp": timestamp,
                    "alert_triggered": temp_alert,
                    "anomaly": temp_anomaly
                })
                
                # === SENSOR 3: PH ===
                ph_alert = False
                ph_anomaly = None
                
                if ph < 4.5 or ph > 8.5:
                    ph_anomaly = "EXTREME pH"
                    ph_alert = True
                
                sensors.append({
                    "sensor_id": f"KAGGLE-{row_count + 1:05d}-P",
                    "zone": zone,
                    "sensor_type": "PH",
                    "reading": round(ph, 2),
                    "unit": "pH",
                    "timestamp": timestamp,
                    "alert_triggered": ph_alert,
                    "anomaly": ph_anomaly
                })
                
                row_count += 1
        
        print(f"\n  [SUCCESS] Loaded {row_count} Kaggle records --> {len(sensors)} sensors generated")
        print(f"  Sensors breakdown: {row_count} MOISTURE + {row_count} TEMPERATURE + {row_count} PH")
        
        return sensors
    
    except FileNotFoundError:
        print(f"  [ERROR] CSV file not found: {csv_file}")
        return []
    except Exception as e:
        print(f"  [ERROR] Failed to load Kaggle dataset: {e}")
        return []


if __name__ == "__main__":
    # Test the loader
    print("=" * 70)
    print("  KAGGLE DATASET LOADER -- TEST RUN")
    print("=" * 70)
    
    test_sensors = load_kaggle_sensors(limit=5)
    
    print("\n  Sample output (first 5 rows x 3 sensors = 15 sensors):\n")
    for sensor in test_sensors[:15]:
        print(f"  {sensor['sensor_id']:<18} | {sensor['zone']:<25} | "
              f"{sensor['reading']:<6} {sensor['unit']:<4} | {sensor.get('anomaly', 'NORMAL')}")
    
    print("\n" + "=" * 70)
