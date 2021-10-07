# adgen. An Active Directory generator

Author: Lorenzo Mariani <lmariani0698@gmail.com>

Copyright: © 2021, Lorenzo Mariani

Date: 2021-10-07

Version: 0.1.0

## Table of contents

- [Purpose](#Purpose)
- [Installation](#Installation)
- [Usage](#Usage)
    - [Interactive mode](#Interactive-mode)
    - [Run mode](#Run-mode)
    - [Config mode](#Config-mode)

## Purpose

adgen is a generator of Active Directory data that is stored into a Neo4j graph database. adgen was born from the ashes of [DBCreator](https://github.com/BloodHoundAD/BloodHound-Tools) with the aim of improving the program and above all to add new features.

## Installation

**You should have Python 3.x installed.**

To install adgen follow the steps below:

    git clone https://github.com/lorenzo-mariani/adgen
    cd adgen
    pip install -r requirements.txt
    python setup.py install

## Usage

Once installed, adgen can be used in three different modes, i.e., interactive mode, run mode and config mode.

### Interactive mode

To use adgen in interactive mode, type:

    adgen interactive

At this point you can enter your parameters directly from the command line by using the commands that this mode makes available:

    [clear_and_generate]    Connect to the database, clear the db, set the schema, and generate random data
    [cleardb]               Clear the database and set constraints
    [connect]               Test connection to the database and verify credentials
    [dbconfig]              Configure database connection parameters
    [exit]                  Exits the database creator
    [generate]              Generate random data
    [help]                  Shows a brief description of the various commands (type help <topic>)
    [setdomain]             Set domain name (default 'TESTLAB.LOCAL')
    [setnodes]              Set base number of nodes to generate (default 500)

### Run mode
### Config mode
