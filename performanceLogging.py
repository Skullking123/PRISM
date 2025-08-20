from HardwareMonitor.Hardware import IVisitor, IComputer, IHardware, IParameter, ISensor, Computer, HardwareType
from HardwareMonitor.Util import OpenComputer, SensorValueToString
from PySide6.QtCore import QPointF, QDateTime
import time 
import pandas as pd
import json
import datetime
from constants import *
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

def initializeLoggingDataFrame(computer: Computer) -> pd.DataFrame:
    """Initialize a DataFrame to log hardware usage."""
    columns = ["Time"]
    for hardware in computer.Hardware:
        for sensor in hardware.Sensors:
            columns.append(f"{sensor.Name}")
    return pd.DataFrame(columns=columns)

def logHardwareUsage(duration: float = 60) -> pd.DataFrame:
    """Monitor CPU usage and print sensor values."""
    computer = OpenComputer(all=True)
    hardwareUsage = initializeLoggingDataFrame(computer)
    computer.Open()
    visitor = UpdateVisitor()
    computer.Accept(visitor)
    startTime = time.perf_counter()
    while True:
        computer.Accept(visitor)
        elapsedTime = time.perf_counter() - startTime
        row = [elapsedTime]  # convert seconds to minutes
        for hardware in computer.Hardware:
            for sensor in hardware.Sensors:
                row.append(sensor.Value)
        hardwareUsage.loc[len(hardwareUsage)] = row
        if elapsedTime > duration:  # stop after 10 seconds
            break
        time.sleep(TIME_BETWEEN_UPDATES)  # sleep for 0.25 seconds to give time for the next update
    return hardwareUsage
        
class HardwareLogger:
    """Class to manage hardware logs."""

    def __init__(self, hardware: Hardware):
        self.hardware = hardware
        self.computer = Computer()
        self.logs = None
        if hardware == Hardware.CPU:
            self.computer.IsCpuEnabled = True
        elif hardware == Hardware.GPU:
            self.computer.IsGpuEnabled = True
        elif hardware == Hardware.MEMORY:
            self.computer.IsMemoryEnabled = True
        elif hardware == Hardware.COOLING:
            self.computer.IsControllerEnabled = True
        elif hardware == Hardware.STORAGE:
            self.computer.IsStorageEnabled = True
        elif hardware == Hardware.NETWORK:
            self.computer.IsNetworkEnabled = True
        elif hardware == Hardware.MOTHERBOARD:
            self.computer.IsMotherboardEnabled = True
        else:
            self.computer = OpenComputer(all=True)
        self.computer.Open()


    def read(self) -> dict:
        """Gets the current hardware usage values"""
        visitor = UpdateVisitor()
        self.computer.Open()
        self.computer.Accept(visitor)
        
        if self.logs is None:
            self.logs = self.__initializeLoggingDataFrame(self.computer)
            
        data  = {"Time": time.time()}
        row = [time.perf_counter()]
        for hardware in self.computer.Hardware:
            for sensor in hardware.Sensors:
                data[f"{sensor.Name} {sensor.SensorType}"] = sensor.Value
                row.append(sensor.Value)
        self.logs.loc[len(self.logs)] = row
        
        self.computer.Close()
        return data

    def __initializeLoggingDataFrame(self, computer: Computer) -> pd.DataFrame:
        """Initialize a DataFrame to log hardware usage."""
        columns = ["Time"]
        for hardware in computer.Hardware:
            for sensor in hardware.Sensors:
                columns.append(f"{sensor.Name}")
        self.logs = pd.DataFrame(columns=columns)
        return self.logs

    def listMetrics(self) -> list[str]:
        """List all metrics available in the logs."""
        return self.logs.columns.tolist()

    def getSensors(self, hardwareType: HardwareType) -> list[ISensor]:
        """Get all sensors for a specific hardware type."""
        sensors = []
        for hardware in self.computer.Hardware:
            if hardware.HardwareType == hardwareType:
                sensors.append(hardware.Sensors)
        return sensors
    
    def getDataFromSensors(self, sensors: list[ISensor]) -> dict[str, str]:
        """Get data from a list of sensors."""
        data = {}
        for sensor in sensors:
            data[sensor.Name] = SensorValueToString(sensor.Value, sensor.SensorType)
        return data
    
    def isAMDorIntelCPU(self) -> bool:
        """Check if the CPU is AMD or Intel. True if its AMD, false otherwise"""
        for hardware in self.computer.Hardware:
            if hardware.HardwareType == HardwareType.Cpu:
                if hardware.Name.lower().startswith("amd"):
                    return True
                else:
                    return False
        return False

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