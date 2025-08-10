from HardwareMonitor.Hardware import IVisitor, IComputer, IHardware, IParameter, ISensor, Computer
from HardwareMonitor.Util import OpenComputer
import time 
import pandas as pd
import datetime

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
        row = [elapsedTime/60]  # convert seconds to minutes
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
    
    def initializeLoggingDataFrame(self, computer: Computer) -> pd.DataFrame:
        """Initialize a DataFrame to log hardware usage."""
        columns = ["Time"]
        for hardware in computer.Hardware:
            for sensor in hardware.Sensors:
                columns.append(f"{sensor.Name}")
        self.logs = pd.DataFrame(columns=columns)
        return self.logs

    def logHardwareUsage(self, duration: float = 60) -> pd.DataFrame:
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
            row = [elapsedTime/60]  # convert seconds to minutes
            for hardware in computer.Hardware:
                for sensor in hardware.Sensors:
                    row.append(sensor.Value)
            hardwareUsage.loc[len(hardwareUsage)] = row
            if elapsedTime > duration:  # stop after 10 seconds
                break
            time.sleep(TIME_BETWEEN_UPDATES)  # sleep for 0.25 seconds to give time for the next update
        self.logs = hardwareUsage
        return hardwareUsage
    
    def listMetrics(self) -> list:
        """List all metrics available in the logs."""
        return self.logs.columns.tolist()   
    