import sys
import os
import configparser
import logging

# Logs will not be shown up for this file as it is imported before logging is configured
log = logging.getLogger(__name__)

# Creates new config is the file is not exists
if not os.path.isfile("config/config.ini"):
    log.debug("Creating new config.ini file from the template")
    # Open the template and creating new config.ini file
    with open("config/config_template.ini", 'r', encoding='utf-8') as template_file, \
            open("config/config.ini", 'w', encoding='utf-8') as config_file:
        log.debug("New configuration file was created")
        # Creating new config file from the template
        config_file.write(template_file.read())

# Checking template version
with open("config/config_template.ini", 'r', encoding='utf-8') as template_file:
    config = configparser.ConfigParser()
    config.read_file(template_file)
    template_version = config["Config"]["version"]
    log.debug(f"Template version is {template_version}")


# Checking config version
with open("config/config.ini", 'r', encoding='utf-8') as config_file:
    config = configparser.ConfigParser()
    config.read_file(config_file)
    config_version = config["Config"]["version"]
    log.debug(f"Config version is {config_version}")


# Checking if the config is a template
if config["Config"]["is_template"] == "yes":
    log.debug("Config is a template, aborting...")
    log.fatal("Please configure file config/config.ini\t"
              "Set the value is_template to 'no', then restart the script")
    sys.exit(1)

# Checking if the config older then the template
if template_version > config_version:
    log.debug("Config is older then a template. Creating new config...")
    with open('config/config_template.ini', 'r', encoding='utf-8') as template_file, \
            open("config/config.ini", 'w', encoding='utf-8') as config_file:
        # Creating new config file from the template
        config_file.write(template_file.read())
        log.fatal("Please configure file config/config.ini\t"
                  "Set the value is_template to 'no', then restart the script")
        sys.exit(1)
