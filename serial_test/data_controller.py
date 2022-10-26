
class DataController:
    """
    Generic data controller class for reading/writing to a port/connection.
    """
    def __init__(self) -> None:
        pass
    
    # Raise when we can't open().
    class DataControllerException(Exception):
        """
        Generic exception for DataController so people using it know what to catch.

        This is usually raised when DataController.open() fails.
        """
        pass

    # Returns a dictionary with different config options.
    def get_config(self) -> dict[str]:
        return {}
    
    # Sets config options from the dictionary passed in.
    def set_config(self, config: dict[str]) -> None:
        pass
    
    def open(self) -> None:
        raise DataController.DataControllerException('Generic data controller cannot be opened.')
    
    def is_open(self) -> bool:
        return False
    
    def close(self) -> None:
        pass

    def update(self) -> None:
        pass
