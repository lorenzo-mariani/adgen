import time
from adgen.utils.data import get_first_names, get_last_names

DEFAULT_CONFIG = {
    'url': 'bolt://localhost:7687',
    'username': 'neo4j',
    'password': 'neo4jj',
    'driver': None,
    'connected': False,
    'nodes': 500,
    'domain': 'TESTLAB.LOCAL',
    'current_time': int(time.time()),
    'sid': 'S-1-5-21-883232822-274137685-4173207997',
    'first_names': get_first_names(),
    'last_names': get_last_names()
}

'''
CLIENTS_OS = {
    'Windows 7 Professional': 7,
    'Windows 7 Ultimate': 5,
    'Windows 7 Enterprise': 15,
    'Windows 10 Pro': 30,
    'Windows 10 Enterprise': 40,
    'Windows XP Professional': 3
}

SERVERS = {
    'Windows Server 2003 Enterprise Edition': 1,
    'Windows Server 2008 Standard': 1,
    'Windows Server 2008 Enterprise': 1,
    'Windows Server 2008 Datacenter': 1,
    'Windows Server 2008 R2 Standard': 2,
    'Windows Server 2008 R2 Enterprise': 2,
    'Windows Server 2008 R2 Datacenter': 3,
    'Windows Server 2012 Standard': 3,
    'Windows Server 2012 Datacenter': 3,
    'Windows Server 2012 R2 Standard': 5,
    'Windows Server 2012 R2 Datacenter': 5,
    'Windows Server 2016 Datacenter': 15,
    'Windows Server 2016 Standard': 25,
    'Windows Server 2019 Datacenter': 10,
    'Windows Server 2019 Standard': 20,
    'Windows Server 2022 Datacenter': 1,
    'Windows Server 2022 Standard': 2
}

ACLS = {
    'GenericAll': 10,
    'GenericWrite': 15,
    'WriteOwner': 15,
    'WriteDacl': 15,
    'AddMember': 30,
    'ForceChangePassword': 15,
    'ReadLAPSPassword': 10
}

GROUPS = {
    'IT': 7,
    'HR': 13,
    'MARKETING': 30,
    'OPERATIONS': 20,
    'BIDNESS': 30
}

OUS = {
    'WA': 1,
    'MD': 1,
    'AL': 1,
    'IN': 1,
    'NV': 1,
    'VA': 1,
    'CA': 1,
    'NY': 1,
    'TX': 1,
    'FL': 1
}
'''

CLIENT_OS_LIST = ["Windows 7 Professional"] * 7 + ["Windows 7 Ultimate"] * 5 + ["Windows 7 Enterprise"] * 15 + \
            ["Windows 10 Pro"] * 30 + ["Windows 10 Enterprise"] * 40 + ["Windows XP Professional"] * 3

SERVER_OS_LIST = ["Windows Server 2003 Enterprise Edition"] * 1 + ["Windows Server 2008 Standard"] * 1 +\
            ["Windows Server 2008 Enterprise"] * 1 + ["Windows Server 2008 Datacenter"] * 1 +\
            ["Windows Server 2008 R2 Standard"] * 2 +\
            ["Windows Server 2008 R2 Enterprise"] * 2 + ["Windows Server 2008 R2 Datacenter"] * 3 +\
            ["Windows Server 2012 Standard"] * 3 + ["Windows Server 2012 Datacenter"] * 3 +\
            ["Windows Server 2012 R2 Standard"] * 5 + ["Windows Server 2012 R2 Datacenter"] * 5 +\
            ["Windows Server 2016 Datacenter"] * 15 + ["Windows Server 2016 Standard"] * 25 +\
            ["Windows Server 2019 Datacenter"] * 10 + ["Windows Server 2019 Standard"] * 20 +\
            ["Windows Server 2022 Datacenter"] * 1 + ["Windows Server 2022 Standard"] * 2

ACLS_LIST = ["GenericAll"] * 10 + ["GenericWrite"] * 15 + ["WriteOwner"] * 15 + ["WriteDacl"] * \
            15 + ["AddMember"] * 30 + ["ForceChangePassword"] * \
            15 + ["ReadLAPSPassword"] * 10

PARTITIONS = ["IT"] * 7 + ["HR"] * 13 + ["MARKETING"] * 30 + ["OPERATIONS"] * 20 + ["BIDNESS"] * 30

STATES = ["WA", "MD", "AL", "IN", "NV", "VA", "CA", "NY", "TX", "FL"]
