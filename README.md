# GROUP 3: SENSOR DATA PROCESSING SYSTEM

## 1. OVERVIEW

This project implements a Sensor Data Processing System designed for agricultural monitoring.
The same system is developed across four programming languages — Python, Java, C++ and
Smalltalk — to demonstrate that the underlying computational logic remains consistent
regardless of implementation language. The focus is not on syntax differences, but on how
a real-world agricultural problem can be translated into a structured computational system
and progressively improved using programming concepts.

The system is developed progressively across six milestones, where each milestone builds
directly on the previous one. No part of the system is discarded; instead, it is refined
and extended. This document currently covers Milestones 1 through 4.

---

## 2. PROBLEM DEFINITION

Modern farming increasingly depends on accurate and continuous monitoring of environmental
conditions such as soil moisture, temperature, rainfall and soil pH. Manual monitoring is
inefficient, especially when dealing with large-scale farms or multiple fields.

This project models a system that simulates how a network of farm sensors operates. Instead
of using real hardware, the system processes predefined data based on real agricultural
sensor readings from Kenyan farms to mimic sensor behavior.

The objective is to:
- Process environmental data from multiple sensor types
- Interpret conditions affecting crops across different farm zones
- Generate meaningful decisions such as irrigation recommendations or warnings
- Detect anomalies automatically across the sensor network
- Persist sensor data to log files for review and record-keeping

The system is designed to evolve from a simple procedural single-sensor model into a
robust, modular, multi-sensor simulation with file persistence and exception handling.

---

## 3. REAL WORLD TO SYSTEM MAPPING

Each variable in the program represents a real agricultural parameter:

| Variable | Real-World Meaning |
|----------|-------------------|
| `sensor_id` | Unique identifier attached to a physical sensor device |
| `moisture_level` | Volumetric soil water content (0.0 = bone dry, 1.0 = saturated) |
| `temperature` | Air temperature above the field in degrees Celsius |
| `rainfall` | Amount of rainfall recorded in millimeters |
| `ph` | Soil acidity/alkalinity level (0.0 to 14.0 scale) |
| `status` | Operational state of the sensor: ACTIVE, NORMAL, WARNING, ALERT, FAULTY, OFFLINE |

### Moisture Classification Thresholds
Based on field sensor data:

| Range | Classification | Action |
|-------|---------------|--------|
| Below 0.20 | CRITICAL DRY | Irrigate immediately |
| 0.20 – 0.35 | DRY | Schedule irrigation within 24 hours |
| 0.35 – 0.65 | OPTIMAL | No action needed |
| 0.65 – 0.80 | WET | Monitor drainage |
| Above 0.80 | WATERLOGGED | Activate drainage system |

### Temperature Classification
Based on East African highland and lowland crop tolerance data:

| Range | Classification |
|-------|---------------|
| Below 15°C | Cold stress — frost risk |
| 15°C – 20°C | Cool — suboptimal for crops |
| 20°C – 30°C | Optimal — ideal for crop growth |
| 30°C – 35°C | Warm — monitor crop stress |
| Above 35°C | Heat stress — crops at risk |

### pH Classification
Based on Embu County, Kenya smallholder farm sensor study:

| Range | Classification |
|-------|---------------|
| Below 4.5 | Highly Acidic — lime required urgently |
| 4.5 – 5.5 | Acidic — consider lime treatment |
| 5.5 – 6.8 | Optimal — ideal for maize, beans, vegetables |
| 6.8 – 7.5 | Alkaline — nutrient availability reduced |
| Above 7.5 | Highly Alkaline — soil amendment required |

---

## 4. DATA SOURCES

Sensor values used throughout the system are based on real agricultural data:

- **Embu County Smallholder Farm Sensor Study**
  Sensor performance evaluation in Kenyan smallholder farms
  Published in: MDPI Sensors / PMC, 2016

- **TAMSAT Soil Moisture Dataset, Kenya (2024)**
  Root zone moisture availability data, Kenya Meteorological Department

Typical value ranges used:
- Soil Moisture: 0.12 – 0.78 VWC
- Temperature: 18.0 – 39.5 °C
- Rainfall: 0.0 – 45.0 mm/day
- pH: 4.5 – 7.8
- Electrical Conductivity: 0.1 – 3.5 mS/cm

---

## 5. SYSTEM STRUCTURE

The system follows a processing pipeline that grows more sophisticated with each milestone:

```
Input → Validation → Processing → Decision → Output → Logging
```

- **Input**: Sensor readings from the simulated farm network
- **Validation**: Checking readings are within physically acceptable ranges
- **Processing**: Classification and analysis using defined thresholds
- **Decision**: Farm-level recommendations (irrigation, drainage, alerts)
- **Output**: Console display of results and status
- **Logging**: Persistent storage of readings and alerts to files (from Milestone 4)

---

## 6. MILESTONE 1 — Computational Foundations

**Focus**: Weeks 1–2 | Translating real-world sensor behavior into a computational model

### Objective
To establish the core computational logic of the system using basic programming constructs
without any structural abstraction.

### Implementation
The system uses a procedural approach with 10 sensors deployed across different farm zones
from North Field A to South Dryland. It performs the following:

- Initializes all system state variables representing real farm parameters
- Registers 10 sensors across named farm zones
- Computes farm-wide moisture statistics: total, average, highest and lowest
- Computes farm-wide temperature and rainfall statistics
- Classifies each sensor's moisture reading using if/elif/else decision structures
- Runs a multi-cycle simulation across 3 time cycles, generating new readings each cycle
- Recalculates farm averages and issues a farm-level irrigation decision after each cycle
- Prints a final system report summarizing alerts and conditions across all zones

### Key Variables
- `farm_name`, `total_sensors`, `current_cycle`, `total_cycles`
- `moisture_readings`, `temperature_readings`, `rainfall_readings` — lists of 10 values
- `THRESHOLD_DRY`, `THRESHOLD_LOW`, `THRESHOLD_OPTIMAL` — classification constants

### Key Insight
This milestone establishes the foundation. All future development builds directly on
these computations and decision rules.

---

## 7. MILESTONE 2 — Control Logic & Object-Oriented Design

**Focus**: Weeks 3–4 | Restructuring using object-oriented principles

### Objective
To reorganize the Milestone 1 system into a class-based structure for better organization,
scalability and realism. No logic was rewritten — only restructured.

### Implementation
The system is redesigned around a `Sensor` class representing an individual field sensor.
The same 10 sensors from Milestone 1 are now created as objects, each carrying its own
state and behavior.

### Core Features

#### Encapsulation
All sensor attributes — sensor ID, zone, moisture, temperature, rainfall, status and alert
flag — are stored as private attributes (double underscore prefix). They can only be
accessed through getter methods.

#### Validation
Before processing, each reading is checked:
- Moisture must be within 0.0 to 1.0
- Temperature must be within 0°C to 60°C

Invalid readings result in the sensor being flagged as FAULTY and processing stops for
that sensor.

#### Methods
- `validate_reading()` — checks all readings are within valid ranges
- `process_reading()` — classifies moisture and generates recommended action
- `update_reading()` — simulates receiving new data in a new time cycle
- Getter methods for controlled access to private attributes

#### Multi-Sensor Simulation
The simulation engine loops all 10 sensor objects across 3 time cycles. Between cycles,
all sensors are updated with new readings. After each cycle, a farm-wide summary is
printed showing alert counts, warnings and average moisture.

### System Evolution

| Aspect | Milestone 1 | Milestone 2 |
|--------|-------------|-------------|
| Structure | Procedural | Object-Oriented |
| Data Handling | Separate lists | Encapsulated in class |
| Sensors | 10 (via lists) | 10 sensor objects |
| Validation | None | Implemented |
| Logic | Standalone blocks | Organized in methods |
| Simulation | Multi-cycle loop | Multi-cycle with object updates |

---

## 8. MILESTONE 3 — Data Structures & OOP Modeling

**Focus**: Weeks 5–6 | Modeling complex systems using abstraction

### Objective
To introduce a proper inheritance hierarchy, polymorphism and structured datasets,
replacing the single generic Sensor class with specialized sensor types.

### Implementation
The system expands from 10 generic sensors to 21 specialized sensors across three types,
all managed within a structured dataset class.

### Inheritance Hierarchy

```
Sensor (Abstract Base Class)
├── MoistureSensor
├── TemperatureSensor
└── PHSensor
```

The abstract base class `Sensor` uses Python's ABC module and defines two abstract methods
— `get_reading()` and `process_reading()` — that every subclass must implement.

#### MoistureSensor
Measures volumetric soil water content.
10 sensors deployed across all farm zones.

#### TemperatureSensor
Measures air temperature in Celsius. Uses East African crop tolerance ranges.
6 sensors deployed across key farm zones.

#### PHSensor
Measures soil acidity. Uses Embu County Kenya pH research data.
5 sensors deployed across selected zones.

### Polymorphism
Each subclass overrides `process_reading()` with its own classification logic and
thresholds. The same method name produces different behavior depending on which sensor
type calls it.

### SensorDataset Class
Manages the full collection of 21 sensors as a structured dataset:
- Stores sensors in an array
- Maintains a string-based registration log
- Computes moisture statistics: average, highest, lowest, spread
- Generates compact and verbose reports

### Method Overloading (Simulated)
`get_summary(verbose=False)` — returns a one-line summary when verbose is False,
and a full detailed breakdown when verbose is True. This simulates method overloading
using Python's default parameters.

### Recursion
`detect_anomalies_recursive()` scans all 21 sensors using recursion. It processes
one sensor per call and calls itself on the next until all sensors are checked.
In this run it detected 6 anomalies across the network.

### System Evolution

| Aspect | Milestone 2 | Milestone 3 |
|--------|-------------|-------------|
| Sensor types | 1 generic class | 3 specialized subclasses |
| Total sensors | 10 | 21 |
| Hierarchy | Single class | Abstract base + 3 subclasses |
| Data handling | Object list | SensorDataset class |
| Anomaly detection | Manual check | Recursive algorithm |
| Reporting | Basic print | Compact and verbose modes |

---

## 9. MILESTONE 4 — Modular Architecture & System Robustness

**Focus**: Weeks 7–9 | Reliable and modular software design

### Objective
To split the system into dedicated modules, introduce interfaces, implement a full
exception handling framework and add file persistence for all sensor data.

### Interfaces
Two abstract interfaces defined using ABC:

#### IReadable
Enforces that any data-providing component must implement:
- `get_reading()` — returns the sensor's measurement
- `validate()` — checks if the reading is within acceptable range

#### ILoggable
Enforces that any logging component must implement:
- `log_to_file(filepath)` — writes data to a specified file

The `Sensor` class implements both interfaces, making every sensor capable of
validating its own reading and writing itself to disk independently.

### Custom Exception Framework
Instead of simple if/else validation, the system uses a hierarchy of custom exceptions:

| Exception | When Raised |
|-----------|-------------|
| `SensorException` | Base class for all sensor errors |
| `InvalidReadingError` | Reading is outside the valid range |
| `SensorOfflineError` | Sensor sent no reading at all |
| `FileLoggingError` | System could not write to a log file |

A deliberately faulty sensor (SNS-M10, moisture = 1.45) demonstrates the framework.
The system catches the `InvalidReadingError`, flags the sensor as FAULTY and continues
processing all remaining sensors without interruption.

### File Handling — FileLogger Module
A dedicated `FileLogger` class handles all disk operations separately from sensor logic:

| File | Contents |
|------|----------|
| `sensor_readings.txt` | Every sensor's full reading and assessment |
| `alerts.txt` | Only sensors in ALERT or FAULTY state |
| `daily_summary.txt` | Structured end-of-day farm report |

All file operations are wrapped in try-except blocks. A disk error does not crash the
system — it is caught, reported and the system continues.

### Modular Architecture
The system is divided into four dedicated modules:

| Module | Responsibility |
|--------|---------------|
| Custom Exceptions | Define all system-specific error types |
| Interfaces (IReadable, ILoggable) | Enforce consistent contracts across components |
| Sensor | Validate, process and log individual readings |
| FileLogger | Handle all file creation, writing and reading |
| SensorNetwork | Coordinate all sensors, run processing cycle, collect results |

### Results (Milestone 4 Run)
- Total sensors: 21
- Alerts: 6
- Warnings: 6
- Normal: 9
- Faulty sensors caught by exception handler: 1
- Log files generated: 3

### System Evolution

| Aspect | Milestone 3 | Milestone 4 |
|--------|-------------|-------------|
| Validation | if/else checks | Custom exception classes |
| File output | None | 3 persistent log files |
| Architecture | Classes | Dedicated modules |
| Interfaces | None | IReadable, ILoggable |
| Error handling | Basic | Full exception framework |
| Fault tolerance | Limited | Graceful — system never crashes |

---

## 10. DESIGN CONSISTENCY ACROSS LANGUAGES

The system is implemented in Python, Java, C++ and Smalltalk. Despite differences in
syntax, the following remain identical across all versions:
- System logic and decision rules
- Data flow and processing pipeline
- Class structure and method names
- Sensor values and classification thresholds

This ensures the project demonstrates understanding of concepts, not just syntax.

---

## 11. GROUP IMPLEMENTATION APPROACH

The group is organized into pairs, with each pair responsible for one language:

| Members | Language |
|---------|----------|
| Members 1 & 2 | Python |
| Members 3 & 4 | Java |
| Members 5 & 6 | C++ |
| Members 7 & 8 | Smalltalk |

All pairs follow the same system design, maintain consistent logic and contribute to
a unified final system.

---

## 12. FILES

| File | Description |
|------|-------------|
| `python/milestone1.py` | Procedural implementation — 10 sensors, 3 cycles |
| `python/milestone2.py` | OOP implementation — Sensor class, encapsulation |
| `python/milestone3.py` | Inheritance hierarchy — 21 sensors, polymorphism, recursion |
| `python/milestone4.py` | Modular system — interfaces, exceptions, file logging |
| `java/Milestone1.java` | Java version — Milestone 1 |
| `java/Milestone2.java` | Java version — Milestone 2 |
| `cpp/milestone1.cpp` | C++ version — Milestone 1 |
| `cpp/milestone2.cpp` | C++ version — Milestone 2 |
| `smalltalk/milestone1.st` | Smalltalk version — Milestone 1 |
| `smalltalk/milestone2.st` | Smalltalk version — Milestone 2 |
| `documentation/documentation.md` | Unified documentation — all languages, all milestones |
| `sensor_logs/sensor_readings.txt` | Generated log — all sensor readings |
| `sensor_logs/alerts.txt` | Generated log — alerts only |
| `sensor_logs/daily_summary.txt` | Generated log — daily farm summary |

---

## 13. CONCLUSION

The Sensor Data Processing System demonstrates how real-world agricultural monitoring
can be modeled computationally and progressively improved across milestones.

Milestone 1 established the core logic using basic programming constructs across a
network of 10 farm sensors simulated over multiple time cycles.

Milestone 2 introduced structure and scalability through object-oriented design,
replacing standalone logic with a Sensor class built on encapsulation and validation.

Milestone 3 introduced a full inheritance hierarchy with three specialized sensor types,
polymorphism, structured datasets and recursive anomaly detection across 21 sensors
using real Kenyan agricultural data.

Milestone 4 made the system robust and production-ready through interfaces, a custom
exception framework, dedicated modules and persistent file logging across three output files.

The system is now prepared for Milestones 5 and 6, which will introduce concurrent
multi-threaded processing, lambda expressions, enumerations and a fully interactive
graphical user interface.
