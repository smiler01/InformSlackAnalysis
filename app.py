# coding: utf-8
import os
import urllib.request as requests
import yaml

CONFIG_PATH = "./config.yaml"


def main():

    with open(CONFIG_PATH) as f:
        config = yaml.load(stream=f, Loader=yaml.SafeLoader)

    request = requests.Request()

    print(config["slack"])


if __name__ == "__main__":
    main()