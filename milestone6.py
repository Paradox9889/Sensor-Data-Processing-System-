import tkinter as tk
from tkinter import ttk
import threading
import time
from enum import Enum


class SensorState(Enum):
    ACTIVE  = 1
    NORMAL  = 2
    WARNING = 3
    ALERT   = 4
    FAULTY  = 5


class SensorType(Enum):
    MOISTURE    = "MOISTURE"
    TEMPERATURE = "TEMPERATURE"
    PH          = "PH"


class Sensor:
    """Represents one agricultural field sensor."""

    def __init__(self, sensor_id, zone, sensor_type, reading, unit):
        self.__sensor_id   = sensor_id
        self.__zone        = zone
        self.__sensor_type = sensor_type
        self.__reading     = reading
        self.__unit        = unit
        self.__state       = SensorState.ACTIVE
        self.__assessment  = ""

    def process(self):
        """Validates then classifies the sensor reading."""
        self.__validate()
        if self.__state not in (SensorState.FAULTY,):
            self.__classify()

    def __validate(self):
        if self.__sensor_type == SensorType.MOISTURE:
            if not (0.0 <= self.__reading <= 1.0):
                self.__state      = SensorState.FAULTY
                self.__assessment = f"Moisture {self.__reading} out of range (0.0-1.0)"

        elif self.__sensor_type == SensorType.TEMPERATURE:
            if not (0.0 <= self.__reading <= 60.0):
                self.__state      = SensorState.FAULTY
                self.__assessment = f"Temperature {self.__reading}C out of range (0-60)"

        elif self.__sensor_type == SensorType.PH:
            if not (0.0 <= self.__reading <= 14.0):
                self.__state      = SensorState.FAULTY
                self.__assessment = f"pH {self.__reading} out of range (0-14)"

    def __classify(self):
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
                self.__assessment = "OPTIMAL — soil conditions are good"
            elif m < 0.80:
                self.__state      = SensorState.WARNING
                self.__assessment = "WET — monitor drainage"
            else:
                self.__state      = SensorState.ALERT
                self.__assessment = "WATERLOGGED — activate drainage system"

        elif self.__sensor_type == SensorType.TEMPERATURE:
            t = self.__reading
            if t < 15.0:
                self.__state      = SensorState.ALERT
                self.__assessment = "COLD STRESS — frost damage risk"
            elif t < 20.0:
                self.__state      = SensorState.WARNING
                self.__assessment = "COOL — suboptimal for most Kenyan crops"
            elif t <= 30.0:
                self.__state      = SensorState.NORMAL
                self.__assessment = "OPTIMAL — ideal temperature for crops"
            elif t <= 35.0:
                self.__state      = SensorState.WARNING
                self.__assessment = "WARM — monitor for crop stress"
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
                self.__assessment = "OPTIMAL — ideal pH for Kenyan crops"
            elif ph <= 7.5:
                self.__state      = SensorState.WARNING
                self.__assessment = "ALKALINE — nutrient availability reduced"
            else:
                self.__state      = SensorState.ALERT
                self.__assessment = "HIGHLY ALKALINE — soil amendment required"

    def get_sensor_id(self):  return self.__sensor_id
    def get_zone(self):       return self.__zone
    def get_type(self):       return self.__sensor_type.value
    def get_reading(self):    return self.__reading
    def get_unit(self):       return self.__unit
    def get_state(self):      return self.__state
    def get_state_name(self): return self.__state.name
    def get_assessment(self): return self.__assessment


def create_sensors():
    """Creates all 21 sensors with real Kenyan farm values."""
    return [
        Sensor("SNS-M01", "North Field A",   SensorType.MOISTURE,    0.32, "VWC"),
        Sensor("SNS-M02", "North Field B",   SensorType.MOISTURE,    0.15, "VWC"),
        Sensor("SNS-M03", "East Greenhouse", SensorType.MOISTURE,    0.61, "VWC"),
        Sensor("SNS-M04", "East Orchard",    SensorType.MOISTURE,    0.44, "VWC"),
        Sensor("SNS-M05", "Central Paddock", SensorType.MOISTURE,    0.72, "VWC"),
        Sensor("SNS-M06", "Central Nursery", SensorType.MOISTURE,    0.28, "VWC"),
        Sensor("SNS-M07", "West Cropland",   SensorType.MOISTURE,    0.53, "VWC"),
        Sensor("SNS-M08", "West Pasture",    SensorType.MOISTURE,    0.81, "VWC"),
        Sensor("SNS-M09", "South Wetland",   SensorType.MOISTURE,    0.13, "VWC"),
        Sensor("SNS-M10", "South Dryland",   SensorType.MOISTURE,    1.45, "VWC"),
        Sensor("SNS-T01", "North Field A",   SensorType.TEMPERATURE, 24.3, "C"),
        Sensor("SNS-T02", "East Greenhouse", SensorType.TEMPERATURE, 22.1, "C"),
        Sensor("SNS-T03", "Central Paddock", SensorType.TEMPERATURE, 31.7, "C"),
        Sensor("SNS-T04", "West Cropland",   SensorType.TEMPERATURE, 36.8, "C"),
        Sensor("SNS-T05", "South Wetland",   SensorType.TEMPERATURE, 28.4, "C"),
        Sensor("SNS-T06", "South Dryland",   SensorType.TEMPERATURE, 38.5, "C"),
        Sensor("SNS-P01", "North Field A",   SensorType.PH,          6.2,  "pH"),
        Sensor("SNS-P02", "East Orchard",    SensorType.PH,          4.8,  "pH"),
        Sensor("SNS-P03", "Central Nursery", SensorType.PH,          7.1,  "pH"),
        Sensor("SNS-P04", "West Cropland",   SensorType.PH,          5.9,  "pH"),
        Sensor("SNS-P05", "South Dryland",   SensorType.PH,          8.1,  "pH"),
    ]


# >>> GUI APPLICATION: Tkinter-based dashboard
# >>> Event-driven programming with color-coded table display
class FarmDashboard:
    """GUI dashboard for JKUAT Research Farm sensor network."""
    # >>> EVENT-DRIVEN PROGRAMMING: Wait for user interactions
    # >>> Nothing happens until user clicks a button

    ROW_COLORS = {
        "NORMAL" : "#d4edda",
        "WARNING": "#fff3cd",
        "ALERT"  : "#f8d7da",
        "FAULTY" : "#e2e3e5",
        "ACTIVE" : "#ffffff",
    }

    def __init__(self, root):
        self.root    = root
        self.running = False

        self.root.title("Sensor Data Processing System — JKUAT Research Farm")
        self.root.geometry("950x620")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(True, True)

        self.__build_header()
        self.__build_buttons()
        self.__build_table()
        self.__build_summary()

    def __build_header(self):
        frame = tk.Frame(self.root, bg="#2c3e50", pady=10)
        frame.pack(fill="x")
        # >>> GUI SECTION 1: Header with farm name and university info

        tk.Label(
            frame,
            text="SENSOR DATA PROCESSING SYSTEM",
            font=("Helvetica", 16, "bold"),
            fg="white", bg="#2c3e50"
        ).pack()

        tk.Label(
            frame,
            text="JKUAT Research Farm  |  Juja, Kiambu County, Kenya",
            font=("Helvetica", 10),
            fg="#bdc3c7", bg="#2c3e50"
        ).pack()

        tk.Label(
            frame,
            text="ICS 2276 Computer Programming II  |  Group 3  |  BSc. Agricultural & Biosystems Engineering",
            font=("Helvetica", 9),
            fg="#95a5a6", bg="#2c3e50"
        ).pack()

    def __build_buttons(self):
        frame = tk.Frame(self.root, bg="#f0f0f0", pady=8)
        frame.pack(fill="x", padx=15)
        # >>> GUI SECTION 2: Event handlers for user button clicks

        # >>> EVENT-DRIVEN: Button click calls __on_run_clicked handler
        self.run_btn = tk.Button(
            frame,
            text="Run Simulation",
            font=("Helvetica", 11, "bold"),
            bg="#27ae60", fg="white",
            activebackground="#1e8449",
            relief="flat", padx=20, pady=6,
            cursor="hand2",
            command=self.__on_run_clicked
        )
        self.run_btn.pack(side="left", padx=(0, 8))

        # >>> EVENT-DRIVEN: Button click calls __on_clear_clicked handler
        tk.Button(
            frame,
            text="Clear",
            font=("Helvetica", 11),
            bg="#c0392b", fg="white",
            activebackground="#a93226",
            relief="flat", padx=20, pady=6,
            cursor="hand2",
            command=self.__on_clear_clicked
        ).pack(side="left")

        self.status_lbl = tk.Label(
            frame,
            text="Ready. Press Run Simulation to start.",
            font=("Helvetica", 10),
            fg="#7f8c8d", bg="#f0f0f0"
        )
        self.status_lbl.pack(side="left", padx=16)

    def __build_table(self):
        """Color-coded table displays all 21 sensor results."""
        # >>> GUI SECTION 3: Treeview table with color-coded rows
        # >>> Green=NORMAL, Yellow=WARNING, Red=ALERT, Grey=FAULTY
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill="both", expand=True, padx=15, pady=(0, 8))

        scrollbar = ttk.Scrollbar(frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        # >>> TREEVIEW: Tkinter table widget for displaying sensor data
        columns = ("id", "zone", "type", "reading", "state", "assessment")
        self.table = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            height=18
        )
        scrollbar.config(command=self.table.yview)

        self.table.heading("id",         text="Sensor ID")
        self.table.heading("zone",       text="Farm Zone")
        self.table.heading("type",       text="Type")
        self.table.heading("reading",    text="Reading")
        self.table.heading("state",      text="State")
        self.table.heading("assessment", text="Assessment")

        self.table.column("id",         width=90,  anchor="w")
        self.table.column("zone",       width=145, anchor="w")
        self.table.column("type",       width=95,  anchor="w")
        self.table.column("reading",    width=80,  anchor="w")
        self.table.column("state",      width=80,  anchor="w")
        self.table.column("assessment", width=350, anchor="w")

        # >>> COLOR-CODED ROWS: Each state gets a background color
        for state, color in self.ROW_COLORS.items():
            self.table.tag_configure(state, background=color)

        self.table.pack(fill="both", expand=True)

    def __build_summary(self):
        frame = tk.Frame(self.root, bg="#2c3e50", pady=8)
        frame.pack(fill="x")
        # >>> GUI SECTION 4: Summary bar shows counts after simulation

        self.lbl_total    = self.__summary_label(frame, "Total Sensors : —")
        self.lbl_alerts   = self.__summary_label(frame, "Alerts : —")
        self.lbl_warnings = self.__summary_label(frame, "Warnings : —")
        self.lbl_normal   = self.__summary_label(frame, "Normal : —")
        self.lbl_faulty   = self.__summary_label(frame, "Faulty : —")
        self.lbl_moisture = self.__summary_label(frame, "Avg Moisture : —")

    def __summary_label(self, parent, text):
        lbl = tk.Label(
            parent,
            text=text,
            font=("Helvetica", 10, "bold"),
            fg="white", bg="#2c3e50",
            padx=14
        )
        lbl.pack(side="left")
        return lbl

    def __on_run_clicked(self):
        """EVENT HANDLER: Run Simulation button."""
        # >>> EVENT HANDLER: User clicks Run Simulation
        # >>> Triggers concurrent processing of all 21 sensors
        if self.running:
            return

        self.running = True
        self.__clear_table()
        self.run_btn.config(state="disabled", text="Processing...")
        self.status_lbl.config(text="Running simulation — processing 21 sensors concurrently...")

        # >>> BACKGROUND THREAD: Keeps GUI responsive during processing
        # >>> Without background thread, window would freeze
        t = threading.Thread(target=self.__run_simulation)
        t.daemon = True
        t.start()

    def __on_clear_clicked(self):
        """EVENT HANDLER: Clear button."""
        self.__clear_table()
        self.__reset_summary()
        self.status_lbl.config(text="Cleared. Press Run Simulation to start again.")

    def __run_simulation(self):
        """Runs in background thread: process all 21 sensors concurrently."""
        # >>> CONCURRENT PROCESSING: Same multithreading as Milestone 5
        # >>> One thread per sensor, all run in parallel
        sensors = create_sensors()
        results = []
        lock    = threading.Lock()

        def process_one(sensor):
            time.sleep(0.02)
            sensor.process()
            with lock:
                results.append(sensor)

        # >>> MULTITHREADING: One thread per sensor, all run concurrently
        threads = []
        for sensor in sensors:
            t = threading.Thread(target=process_one, args=(sensor,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # >>> THREAD-SAFE GUI UPDATE: root.after() schedules on main thread
        # >>> Cannot update GUI directly from background thread
        self.root.after(0, lambda: self.__update_display(results))

    def __update_display(self, results):
        """Updates table and summary with simulation results."""
        for sensor in results:
            self.table.insert(
                "", "end",
                values=(
                    sensor.get_sensor_id(),
                    sensor.get_zone(),
                    sensor.get_type(),
                    f"{sensor.get_reading()} {sensor.get_unit()}",
                    sensor.get_state_name(),
                    sensor.get_assessment()
                ),
                tags=(sensor.get_state_name(),)
            )

        alerts   = [s for s in results if s.get_state() == SensorState.ALERT]
        warnings = [s for s in results if s.get_state() == SensorState.WARNING]
        normal   = [s for s in results if s.get_state() == SensorState.NORMAL]
        faulty   = [s for s in results if s.get_state() == SensorState.FAULTY]

        moist = [
            s for s in results
            if s.get_type() == "MOISTURE" and s.get_state() != SensorState.FAULTY
        ]
        avg_m = sum(s.get_reading() for s in moist) / len(moist) if moist else 0

        self.lbl_total.config(   text=f"Total Sensors : {len(results)}")
        self.lbl_alerts.config(  text=f"Alerts : {len(alerts)}")
        self.lbl_warnings.config(text=f"Warnings : {len(warnings)}")
        self.lbl_normal.config(  text=f"Normal : {len(normal)}")
        self.lbl_faulty.config(  text=f"Faulty : {len(faulty)}")
        self.lbl_moisture.config(text=f"Avg Moisture : {avg_m:.3f} VWC")

        self.status_lbl.config(
            text=f"Simulation complete — {len(results)} sensors processed."
        )

        self.run_btn.config(state="normal", text="Run Simulation")
        self.running = False

    def __clear_table(self):
        for row in self.table.get_children():
            self.table.delete(row)

    def __reset_summary(self):
        self.lbl_total.config(   text="Total Sensors : —")
        self.lbl_alerts.config(  text="Alerts : —")
        self.lbl_warnings.config(text="Warnings : —")
        self.lbl_normal.config(  text="Normal : —")
        self.lbl_faulty.config(  text="Faulty : —")
        self.lbl_moisture.config(text="Avg Moisture : —")


if __name__ == "__main__":
    # >>> APPLICATION ENTRY: Creates GUI and starts event loop
    root = tk.Tk()
    app  = FarmDashboard(root)
    root.mainloop()
