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
    
class Hardware(Enum):
    CPU = "cpu"
    GPU = "gpu"
    MEMORY = "memory"
    COOLING = "cooling"
    STORAGE = "storage"
    NETWORK = "network"
