from HardwareMonitor.Hardware import IVisitor, IComputer, IHardware, IParameter, ISensor, Computer, HardwareType
from HardwareMonitor.Util import OpenComputer, SensorType, SensorValueToString
from PySide6.QtCore import QPointF, QDateTime
import time 
import pandas as pd
import json
import datetime
from constants import *
import psutil
import threading
from constants import HardwareParts
# from psutil import disk_usage, virtual_memory, cpu_percent, net_io_counters

TIME_BETWEEN_UPDATES = 1  # seconds

class UpdateVisitor(IVisitor):
    __namespace__ = "TestHardwareMonitor"  # must be unique among implementations of the IVisitor interface
    def VisitComputer(self, computer: IComputer):
        computer.Traverse(self)

    def VisitHardware(self, hardware: IHardware):
        hardware.Update()
        for subHardware in hardware.SubHardware:
            subHardware.Update()

    def VisitParameter(self, parameter: IParameter): pass

    def VisitSensor(self, sensor: ISensor): pass
    
    
class Hardware():
    
    def __init__(self):
        self.computer = OpenComputer(all=True)
        self.hardware = self.getAllHardware()
    
    def getAllHardware(self) -> dict[str, list[IHardware]]:
        """Get all hardware organized by type"""
        allHardware = {}
        
        # Define mapping from HardwareType to HardwareParts enum
        hardware_type_mapping = {
            HardwareType.Cpu: HardwareParts.CPU,
            HardwareType.Battery: HardwareParts.BATTERY,
            HardwareType.GpuNvidia: HardwareParts.GPU,
            HardwareType.GpuAmd: HardwareParts.GPU,
            HardwareType.GpuIntel: HardwareParts.GPU,
            HardwareType.Memory: HardwareParts.MEMORY,
            HardwareType.Motherboard: HardwareParts.MOTHERBOARD,
            HardwareType.Storage: HardwareParts.STORAGE,
            HardwareType.Network: HardwareParts.NETWORK,
            HardwareType.Cooler: HardwareParts.COOLING,
            HardwareType.EmbeddedController: HardwareParts.CONTROLLER,
            HardwareType.Psu: HardwareParts.PSU,
            HardwareType.SuperIO: HardwareParts.SUPERIO,
        }
        
        for hardware in self.computer.Hardware:
            # Get the corresponding enum value for this hardware type
            hardware_part = hardware_type_mapping.get(hardware.HardwareType)
            
            if hardware_part:
                key = hardware_part.value
                if key not in allHardware:
                    allHardware[key] = []
                allHardware[key].append(hardware)
        
        return allHardware
    
    
    
def readSensorOutput(hardware: IHardware) -> dict[(str, SensorType), float]:
    output = {}
    hardware.Update()
    for sensor in hardware.Sensors:
        
        output[(sensor.Name, sensor.SensorType)] = sensor.Value
    return output

def printSensorOutput(data: dict[(str, SensorType), float]):
    print("Data:")
    for name, type in data.keys():
        print(f"({name}, {type}: {data[(name, type)]})")
    
def SensorTypeToString(type: SensorType):
    if type == SensorType.Voltage:
        return "Voltage"
    elif type == SensorType.Current:
        return "Current"
    elif type == SensorType.Power:
        return "Power"
    elif type == SensorType.Clock:
        return "Clock"
    elif type == SensorType.Temperature:
        return "Temperature"
    elif type == SensorType.Load:
        return "Load"
    elif type == SensorType.Frequency:
        return "Frequency"
    elif type == SensorType.Fan:
        return "Fan"
    elif type == SensorType.Flow:
        return "Flow"
    elif type == SensorType.Control:
        return "Control"
    elif type == SensorType.Level:
        return "Level"
    elif type == SensorType.Factor:
        return "Factor"
    elif type == SensorType.Data:
        return "Data"
    elif type == SensorType.SmallData:
        return "SmallData"
    elif type == SensorType.Throughput:
        return "Throughput"
    elif type == SensorType.TimeSpan:
        return "TimeSpan"
    elif type == SensorType.Energy:
        return "Energy"
    elif type == SensorType.Noise:
        return "Noise"
    else:
        return ""
        
HARDWARE = Hardware()
            

# def initializeLoggingDataFrame(computer: Computer) -> pd.DataFrame:
#     """Initialize a DataFrame to log hardware usage."""
#     columns = ["Time"]
#     for hardware in computer.Hardware:
#         for sensor in hardware.Sensors:
#             columns.append(f"{sensor.Name}")
#     return pd.DataFrame(columns=columns)

# def logHardwareUsage(duration: float = 60) -> pd.DataFrame:
#     """Monitor CPU usage and print sensor values."""
#     computer = OpenComputer(all=True)
#     hardwareUsage = initializeLoggingDataFrame(computer)
#     computer.Open()
#     visitor = UpdateVisitor()
#     computer.Accept(visitor)
#     startTime = time.perf_counter()
#     while True:
#         computer.Accept(visitor)
#         elapsedTime = time.perf_counter() - startTime
#         row = [elapsedTime]  # convert seconds to minutes
#         for hardware in computer.Hardware:
#             for sensor in hardware.Sensors:
#                 row.append(sensor.Value)
#         hardwareUsage.loc[len(hardwareUsage)] = row
#         if elapsedTime > duration:  # stop after 10 seconds
#             break
#         time.sleep(TIME_BETWEEN_UPDATES)  # sleep for 0.25 seconds to give time for the next update
#     return hardwareUsage
        
# class HardwareLogger:
#     """Class to manage hardware logs."""

#     def __init__(self, hardware: Hardware):
#         self.hardware = hardware
#         self.computer = Computer()
#         self.logs = None
#         if hardware == Hardware.CPU:
#             self.computer.IsCpuEnabled = True
#         elif hardware == Hardware.GPU:
#             self.computer.IsGpuEnabled = True
#         elif hardware == Hardware.MEMORY:
#             self.computer.IsMemoryEnabled = True
#         elif hardware == Hardware.COOLING:
#             self.computer.IsControllerEnabled = True
#         elif hardware == Hardware.STORAGE:
#             self.computer.IsStorageEnabled = True
#         elif hardware == Hardware.NETWORK:
#             self.computer.IsNetworkEnabled = True
#         elif hardware == Hardware.MOTHERBOARD:
#             self.computer.IsMotherboardEnabled = True
#         else:
#             self.computer = OpenComputer(all=True)
#         self.computer.Open()
        
#         self.stop = False
#         visitor = UpdateVisitor()
#         self.computer.Accept(visitor)
#         self.updateThread = threading.Thread(target=self.log)
#         self.updateThread.start()


#     def read(self) -> dict:
#         """Gets the latest hardware usage values from logs"""
#         if self.logs is None:
#             return {}
#         row = self.logs.tail(1)
#         row.to_csv("example.csv")
#         return row.to_dict()
    
#     def log(self):
#         "Logs the current readings from sensors"
#         print("Comes here")
#         while not self.stop:
#             if self.logs is None:
#                 self.logs = self.__initializeLoggingDataFrame(self.computer)
#             data  = {"Time": time.time()}
#             row = [time.perf_counter()]
#             for hardware in self.computer.Hardware:
#                 for subhardware  in hardware.SubHardware:
#                     for sensor in subhardware.Sensors:
#                         data[f"{sensor.Name} {sensor.SensorType}"] = sensor.Value
#                         row.append(sensor.Value)
#                 for sensor in hardware.Sensors:
#                     data[f"{sensor.Name} {sensor.SensorType}"] = sensor.Value
#                     row.append(sensor.Value)
#             row.append(psutil.cpu_freq()[0])
#             self.logs.loc[len(self.logs)] = row
#             time.sleep(1)
        
#     def stopUpdating(self):
#         self.stop = True

#     def __initializeLoggingDataFrame(self, computer: Computer) -> pd.DataFrame:
#         """Initialize a DataFrame to log hardware usage."""
#         columns = ["Time"]
#         for hardware in computer.Hardware:
#             for subhardware  in hardware.SubHardware:
#                 for sensor in subhardware.Sensors:
#                     columns.append(f"{sensor.Name} {sensor.SensorType}")
#             for sensor in hardware.Sensors:
#                 columns.append(f"{sensor.Name} {sensor.SensorType}")
#         columns.append("CPU Frequency")
#         self.logs = pd.DataFrame(columns=columns)
#         return self.logs

#     def listMetrics(self) -> list[str]:
#         """List all metrics available in the logs."""
#         return self.logs.columns.tolist()

#     def getSensors(self, hardwareType: HardwareType) -> list[ISensor]:
#         """Get all sensors for a specific hardware type."""
#         sensors = []
#         for hardware in self.computer.Hardware:
#             if hardware.HardwareType == hardwareType:
#                 sensors.append(hardware.Sensors)
#         return sensors
    
#     def getDataFromSensors(self, sensors: list[ISensor]) -> dict[str, str]:
#         """Get data from a list of sensors."""
#         data = {}
#         for sensor in sensors:
#             data[sensor.Name] = SensorValueToString(sensor.Value, sensor.SensorType)
#         return data
    
#     def isAMDorIntelCPU(self) -> bool:
#         """Check if the CPU is AMD or Intel. True if its AMD, false otherwise"""
#         for hardware in self.computer.Hardware:
#             if hardware.HardwareType == HardwareType.Cpu:
#                 if hardware.Name.lower().startswith("amd"):
#                     return True
#                 else:
#                     return False
#         return False
        
# LOGGER_INSTANCE = HardwareLogger(None)





if __name__ == "__main__":
    # data = logHardwareUsage()
    # data.to_csv("hardware_usage_log.csv", index=False)
    # logger = HardwareLogger(None)
    # print(json.dumps(logger.read(), indent=4))
    
    computer = Computer()  # settings can not be passed as constructor argument (following below)
    computer.IsMotherboardEnabled = True
    computer.IsControllerEnabled = True
    computer.IsCpuEnabled = True
    computer.IsGpuEnabled = True
    computer.IsBatteryEnabled = True
    computer.IsMemoryEnabled = True
    computer.IsNetworkEnabled = True
    computer.IsStorageEnabled = True
    computer.Open()
    computer.Accept(UpdateVisitor())
    for hardware in computer.Hardware:
        print(f"Hardware: {hardware.Name}")
        for subhardware  in hardware.SubHardware:
            print(f"\tSubhardware: {subhardware.Name}")
            for sensor in subhardware.Sensors:
                print(f"\t\tSensor: {sensor.Name} : {sensor.SensorType}, value: {SensorValueToString(sensor.Value, sensor.SensorType)}")
        for sensor in hardware.Sensors:
            print(f"\tSensor: {sensor.Name} : {sensor.SensorType}, value: {SensorValueToString(sensor.Value, sensor.SensorType)}")
    computer.Close()