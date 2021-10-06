import random
import math
import uuid

from adgen.config import STATES
from adgen.utils.utils import cn, split_seq


def create_dcs_ous(session, domain, dcou):
    session.run(
        """
        MERGE (n:Base {name:$ou, objectid:$guid, blocksInheritance: false})
        SET n:OU
        """,
        ou=cn("DOMAIN CONTROLLERS", domain),
        guid=dcou
    )


def create_computers_ous(session, domain, computers, ou_guid_map, ou_props, nodes):
    print("Creating OUs")
    temp_comps = computers
    random.shuffle(temp_comps)
    split_num = int(math.ceil(nodes / 10))
    split_comps = list(split_seq(temp_comps, split_num))
    num_states = len(STATES)
    props = []

    for i in range(0, num_states):
        state = STATES[i]
        ou_comps = split_comps[i]
        ouname = "{}_COMPUTERS@{}".format(state, domain)
        guid = str(uuid.uuid4())
        ou_guid_map[ouname] = guid
        for c in ou_comps:
            ou_properties = {
                'compname': c,
                'ouguid': guid,
                'ouname': ouname
            }
            props.append(ou_properties)
            ou_props.append(ou_properties)
            if len(props) > 500:
                session.run(
                    """
                    UNWIND $props as prop
                    MERGE (n:Computer {name:prop.compname})
                    WITH n,prop MERGE (m:Base {objectid:prop.ouguid, name:prop.ouname, blocksInheritance: false})
                    SET m:OU WITH n,m,prop
                    MERGE (m)-[:Contains]->(n)
                    """,
                    props=props
                )
                props = []
    session.run(
        """
        UNWIND $props as prop
        MERGE (n:Computer {name:prop.compname})
        WITH n,prop
        MERGE (m:Base {objectid:prop.ouguid, name:prop.ouname, blocksInheritance: false})
        SET m:OU WITH n,m,prop
        MERGE (m)-[:Contains]->(n)
        """,
        props=props
    )
    return ou_props, ou_guid_map


def create_users_ous(session, domain, users, ou_guid_map, ou_props, nodes):
    temp_users = users
    random.shuffle(temp_users)
    split_num = int(math.ceil(nodes / 10))
    split_users = list(split_seq(temp_users, split_num))
    props = []
    num_states = len(STATES)

    for i in range(0, num_states):
        state = STATES[i]
        ou_users = split_users[i]
        ouname = "{}_USERS@{}".format(state, domain)
        guid = str(uuid.uuid4())
        ou_guid_map[ouname] = guid
        for c in ou_users:
            ou_properties = {
                'username': c,
                'ouguid': guid,
                'ouname': ouname
            }
            props.append(ou_properties)
            ou_props.append(ou_properties)
            if len(props) > 500:
                session.run(
                    """
                    UNWIND $props as prop
                    MERGE (n:User {name:prop.username})
                    WITH n,prop
                    MERGE (m:Base {objectid:prop.ouguid, name:prop.ouname, blocksInheritance: false})
                    SET m:OU
                    WITH n,m,prop
                    MERGE (m)-[:Contains]->(n)
                    """,
                    props=props
                )
                props = []

    session.run(
        """
        UNWIND $props as prop
        MERGE (n:User {name:prop.username})
        WITH n,prop
        MERGE (m:Base {objectid:prop.ouguid, name:prop.ouname, blocksInheritance: false})
        SET m:OU
        WITH n,m,prop
        MERGE (m)-[:Contains]->(n)
        """,
        props=props
    )
    return ou_props, ou_guid_map


def link_ous_to_domain(session, domain, ou_guid_map):
    props = []
    for x in list(ou_guid_map.keys()):
        guid = ou_guid_map[x]
        props.append({'b': guid})

    session.run(
        """
        UNWIND $props as prop
        MERGE (n:OU {objectid:prop.b})
        WITH n
        MERGE (m:Domain {name:$domain})
        WITH n,m MERGE (m)-[:Contains]->(n)
        """,
        props=props,
        domain=domain
    )
