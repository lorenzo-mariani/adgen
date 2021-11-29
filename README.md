# _adgen_. An Active Directory generator

Author: Lorenzo Mariani

Copyright: © 2021, Lorenzo Mariani

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

_adgen_ is a generator of Active Directory data that is stored into a Neo4j graph database. _adgen_ was born from the ashes of [DBCreator](https://github.com/BloodHoundAD/BloodHound-Tools) with the aim of improving the program and adding new features.

## Installation

**You should have Python 3.x installed.**

To install _adgen_ follow the steps below:

    git clone https://github.com/lorenzo-mariani/adgen
    cd adgen
    pip install -r requirements.txt
    python setup.py install

## Usage

Once installed, _adgen_ can be used in three different modes, i.e., interactive mode, run mode and config mode.

### Interactive mode

To use _adgen_ in interactive mode, type:

    adgen interactive

At this point you can enter your parameters directly from the command line by using the commands that this mode makes available:

    [clear_and_generate]    Connect to the database with the given credentials, clear the database,
                            set the schema, and generate data.
    
    [cleardb]               Clear the database to which you are connected  and set constraints.
    
    [connect]               Test connection to the database and verify credentials. If everything is
                            correct, it connects to the database.
    
    [dbconfig]              Configure database connection parameters, i.e., database URL to connect
                            to, username and password.
    
    [exit]                  Exits adgen.
    
    [generate]              Generate data.
    
    [help]                  Shows a brief description of the available commands (type help <topic>).
    
    [setdomain]             Set domain name (default 'TESTLAB.LOCAL').
    
    [setnodes]              Set base number of nodes to generate (default 600).
    
    [setnodes_distr]        Set base distribution of nodes to generate. If not used, the number of
                            nodes to be generated is equal to the last value entered by [setnodes].
                            There are four available distributions, i.e.:
                              - uniform(a,b)
                              - triangular(low,high)
                              - gauss(mu,sigma)
                              - gamma(alpha,beta)

**_Note!_** In order for data generation to occur correctly, either using the [setnodes] command or using [setnodes_distr], the entered value must be greater than zero. Therefore, if the entered value is less or equal to zero, the latter is automatically restored to the default value (600) or to the last value entered using the [setnodes] command.

### Run mode

The run mode allows you to enter directly from the command line a series of parameters to be passed to _adgen_. The parameters to be entered are:

    [url]                   Database URL to connect to (mandatory)

    [username]              Database Username (mandatory)

    [password]              Database Password (mandatory)

    [nodes_val]             Number of nodes to generate (mandatory if you do not use [nodes_distr])
    
    [nodes_distr]           Distribution of the nodes to generate (mandatory if you do not use [nodes_val]).
                            There are four available distributions, i.e.:
                              - uniform(a,b)
                              - triangular(low,high)
                              - gauss(mu,sigma)
                              - gamma(alpha,beta)
    
    [domain]                Name of the domain to generate (mandatory)
    
To use the run mode type:

    adgen run --url <url> --user <username> --passwd <password> --nodes-val <nodes_val> --domain <domain>

or

    adgen run --url <url> --user <username> --passwd <password> --nodes-distr <nodes_distr> --domain <domain>
  
**_Note!_** In order for data generation to occur correctly, the number of nodes must be greater than zero. Therefore, if the entered value is less or equal to zero, the latter is automatically restored to the default value (600).

### Config mode

The config mode allows you to specify directly from the command line the **absolute path of two .ini files** (which are mandatory), e.g., _conn_config.ini_ and _param_config.ini_ and the **absolute path of one .yaml file** (which is optional), e.g., _config_nodes_distr.yaml_.

_conn_config.ini_ contains the parameters necessary for the connection to the database, i.e., URL, username, password, nodes, domain, e.g.:

    [CONNECTION]
    url = bolt://localhost:7687
    username = neo4j
    password = neo4jpassword
    domain = contoso.local
    nodes = 500   

_param_config.ini_ contains the list of client/server operating systems (along with their frequencies) that _adgen_ will use when generating client computers and domain controllers, as well as information about acls, groups and ous (along with their frequencies), e.g.:

    [CLIENTS]
    Windows 10 Pro = 30
    Windows 10 Enterprise = 40
    ...

    [SERVERS]
    Windows Server 2016 Datacenter = 15
    Windows Server 2019 Standard = 20
    ...
    
    [ACLS]
    GenericAll = 10
    AddMember = 30
    ...

    [GROUPS]
    IT = 7
    MARKETING = 30
    ...

    [OUS]
    WA = 2
    AL = 4
    ...

**_Note!_** Except for OUs, for all other sections, the frequency of each option represents the probability of having that option. So, pay attention to the fact that the sum of all frequencies of a section must be equal to 100.

_config_nodes_distr.yaml_ contains the information about the distributions of the nodes to generate, e.g.:

    # COMMENT: uniform(a,b), where x=a, y=b-
    - distribution: "uniform"
    x: 100
    y: 300

    # COMMENT: triangular(low,high), where x=low, y=high
    - distribution: "gauss"
    x: 200
    y: 50

    # COMMENT: ...
    - ...

**_Note!_** There are four available distributions, i.e.:
- uniform(a,b)
- triangular(low,high)
- gauss(mu,sigma)
- gamma(alpha,beta)

To use config mode type:

    adgen config --conn </path/to/conn_config.ini> --param </path/to/param_config.ini>

or

    adgen config --conn </path/to/conn_config.ini> --param </path/to/param_config.ini> --nodes-distr </path/to/config_nodes_distr.yaml>

**_Note!_** In order for data generation to occur correctly, the number of nodes must be greater than zero. Therefore, if the entered value is less or equal to zero, the latter is automatically restored to the default value (600).

## COPYRIGHT

Copyright: © 2021 Lorenzo Mariani.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.
