Server Inventory Generator
Overview
This Python script generates a realistic server inventory in JSON format with configurable parameters, including server configurations, application information, and booking dates. The script can also introduce controlled errors into the inventory for testing purposes.

Features
Generates server entries with:

Unique server names following a specific pattern

Configuration details (model, OS, version)

Package lists specific to RHEL versions

Filesystem free space information

Associated application information

Optional booking dates with rate limiting

Configurable error injection:

Low disk space scenarios

Flagged problematic packages

Uses Faker library to generate realistic:

Application names

Manager names

Email addresses

Requirements
Python 3.6+

Faker library (pip install faker)

Usage
Clone the repository or download the script

Install dependencies: pip install faker

Run the script: python gen_inventory.py

