import os

import environ


class CustomEnvironment:
    env = environ.Env()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

    _proxy = env.str("PROXY")
    _input_url = env.str("INPUT_URL")
    _output_file = env.str("OUTPUT_FILE")

    @classmethod
    def get_proxy(cls) -> str:
        if cls._proxy is None:
            raise ValueError("Proxy is not provided.")
        return cls._proxy

    @classmethod
    def get_input_url(cls) -> str:
        if cls._input_url is None:
            raise ValueError("Input url is not provided.")        
        return cls._input_url

    @classmethod
    def get_output_file(cls) -> str:
        if cls._output_file is None:
            raise ValueError("Output file is not provided.")
        return cls._output_file