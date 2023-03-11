#!/usr/bin/env python3
import yaml


def main(filename):
    with open(filename, "rt") as file:
        config = yaml.safe_load(file)
    
    print(config)


if __name__ == "__main__":
    main("dummy-configuration.yaml")