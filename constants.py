from enum import Enum

class MenuButtonNames(Enum):
    OVERVIEW = "overviewButton"
    CPU = "cpuButton"
    GPU = "gpuButton"
    RAM = "ramButton"
    COOLING = "coolingButton"
    STORAGE = "storageButton"
    NETWORK = "networkButton"
    SPECIFICATIONS = "specButton"
    EXIT = "exitButton"
    
class HardwareParts(Enum):
    CPU = "CPU"
    GPU = "GPU"
    MEMORY = "Memory"
    COOLING = "Cooling"
    STORAGE = "Storage"
    NETWORK = "Network"
    MOTHERBOARD = "Motherboard"
    CONTROLLER = "EmbeddedController"
    BATTERY = "Battery"
    PSU = "PSU"
    SUPERIO = "SuperIO"
