import oyaml as oyaml


class YAML:
    @classmethod
    def read(cls, file):
        """
        Convert yaml file to dictionary
        :param file:
        :return dictionary:
        """
        with open(file, "r") as f:
            content = oyaml.load(f, oyaml.SafeLoader)
        return content

    @classmethod
    def write(cls, file, config):
        """
        Write dictionary to YAML file
        :param file: path for yaml to be written to
        :param config: dictionary to be written
        :return bool:
        """
        with open(file, "w") as outfile:
            return oyaml.dump(config, outfile, default_flow_style=False)
