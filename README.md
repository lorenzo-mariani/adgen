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
- [COPYRIGHT](#COPYRIGHT)

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

The run mode allows you to enter directly from the command line a series of parameters to be passed to adgen. The parameters to be entered are:

    [url]                   Database URL to connect to
    [username]              Database Username
    [password]              Database Password
    [nodes]                 Number of nodes to generate
    [domain]                Name of the domain to generate
    
To use the run mode type:

    adgen run --url <url> --user <username> --passwd <password> --nodes <nodes> --domain <domain>

### Config mode

The config mode allows you to specify directly from the command line the **absolute path of two .ini files**, e.g., _conn_config.ini_ and _param_config.ini_.

_conn_config.ini_ contains the parameters necessary for the connection to the database, i.e., url, username, password, nodes, domain. It must have the following structure:

    [CONNECTION]
    url = <url>
    username = <username>
    password = <password>
    domain = <domain>
    nodes = <nodes>   

_param_config.ini_ contains the list of client/server operating systems (along with their frequencies) that adgen will use when generating client computers and domain controllers, as well as information about acls, groups and ous (along with their frequencies). It must have the following structure:

    [CLIENTS]
    Windows 7 Professional = 10
    Windows 7 Ultimate = 5
    Windows 7 Enterprise = 15
    Windows 10 Pro = 30
    Windows 10 Enterprise = 40

    [SERVERS]
    Windows Server 2012 Standard = 10
    Windows Server 2016 Datacenter = 15
    Windows Server 2016 Standard = 25
    Windows Server 2019 Datacenter = 10
    Windows Server 2019 Standard = 20
    Windows Server 2022 Datacenter = 10
    Windows Server 2022 Standard = 10
    
    [ACLS]
    GenericAll = 10
    GenericWrite = 15
    WriteOwner = 15
    WriteDacl = 15
    AddMember = 30
    ForceChangePassword = 15
    ReadLAPSPassword = 10

    [GROUPS]
    IT = 7
    HR = 13
    MARKETING = 30
    OPERATIONS = 20
    BIDNESS = 30

    [OUS]
    WA = 2
    MD = 2
    AL = 4
    IN = 2
    NV = 2
    VA = 1
    CA = 2
    NY = 3
    TX = 1
    FL = 1

To use config mode type:

    adgen config --conn </path/to/conn_config.ini> --os </path/to/os_config.ini>

## COPYRIGHT

Copyright: © 2021 Lorenzo Mariani.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.
