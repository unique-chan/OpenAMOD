import configparser


class IniReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.config = configparser.ConfigParser()
        self.config.read(file_path)

    def get_value(self, section, key):
        """
        Get the value of the specified key under the given section.

        Parameters:
        - section (str): The section name in the ini file.
        - key (str): The key name under the section.

        Returns:
        - value (str): The value associated with the key.
        """
        try:
            value = self.config.get(section, key)
            return self._strip_quotes(value)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return None

    def get_all_sections(self):
        """
        Get all section names in the ini file.

        Returns:
        - sections (list): A list of section names.
        """
        return self.config.sections()

    def get_all_keys(self, section):
        """
        Get all keys under the specified section.

        Parameters:
        - section (str): The section name in the ini file.

        Returns:
        - keys (list): A list of key names under the section.
        """
        try:
            return self.config.options(section)
        except configparser.NoSectionError:
            return []

    def get_all_items(self, section):
        """
        Get all key-value pairs under the specified section.

        Parameters:
        - section (str): The section name in the ini file.

        Returns:
        - items (dict): A dictionary of key-value pairs under the section.
        """
        try:
            items = self.config.items(section)
            return {key: self._strip_quotes(value) for key, value in items}
        except configparser.NoSectionError:
            return {}

    def _strip_quotes(self, value):
        """
        Strip surrounding quotes from a string value if they exist.

        Parameters:
        - value (str): The string value to strip quotes from.

        Returns:
        - value (str): The value without surrounding quotes.
        """
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        return value


# Example usage
if __name__ == "__main__":
    ini_reader = IniReader("example.ini")
    print(ini_reader.get_value("section", "key"))
    print(ini_reader.get_all_sections())
    print(ini_reader.get_all_keys("section"))
    print(ini_reader.get_all_items("section"))
