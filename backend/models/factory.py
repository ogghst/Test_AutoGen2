import json
from .data_models import Project
from config.settings import get_config_manager

def project_to_json_schema() -> dict:
    """
    Convert the Project class to its JSON schema representation.

    Returns:
        dict: The JSON schema of the Project class.
    """
    return Project.model_json_schema()

    # INSERT_YOUR_CODE
class ProjectFactory:
    """
    Singleton factory class for creating and managing Project instances.
    """
    _instance = None
    
    def __init__(self):
        
        config_manager = get_config_manager("../config/config.json")

        with open(config_manager.system.data_model_file, 'r', encoding='utf-8') as f:
            self._project_schema = f.read()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProjectFactory, cls).__new__(cls)
        return cls._instance

    def create_project(self, **kwargs):
        """
        Create a new Project instance with the provided keyword arguments.

        Returns:
            Project: A new Project instance.
        """
        return Project(**kwargs)

    def get_project_schema(self) -> dict:
        """
        Get the JSON schema of the Project class.

        Returns:
            dict: The JSON schema of the Project class.
        """
        return self._project_schema
    
        # INSERT_YOUR_CODE
def main():
    """
    Main function to test the ProjectFactory and its get_project_schema method.
    """
    factory = ProjectFactory()
    schema = factory.get_project_schema()
    print("Project JSON Schema:")
    print(schema)

if __name__ == "__main__":
    main()
