import random
import math
import uuid

from adgen.utils.support_functions import cn, split_seq


def create_dcs_ous(session, domain_name, dcou):
    """
    Create OUs for domain controllers.

    Arguments:
        session     -- the current session
        domain_name -- the domain name
        dcou        -- the OU of domain controller
    """
    session.run(
        """
        MERGE (n:Base {name:$ou, objectid:$guid, blocksInheritance: false})
        SET n:OU
        """,
        ou=cn("DOMAIN CONTROLLERS", domain_name),
        guid=dcou
    )


def create_computers_ous(session, domain_name, computers, ou_guid_map, ou_props, num_nodes, ous_list):
    """
    Create OUs for computers.

    Arguments:
        session     -- the current session
        domain_name -- the domain name
        computers   -- a list containing the various computers
        ou_guid_map -- a map of OUs guid
        ou_props    -- a list containing the properties of the various OUs
        num_nodes   -- the number of nodes
        ous_list    -- a list containing the names of the various OUs

    Returns:
        ou_props    -- a list containing the properties of the various OUs
        ou_guid_map -- a map of OUs guid
    """
    temp_comps = computers
    random.shuffle(temp_comps)
    num_ous = len(ous_list)
    split_num = int(math.ceil(num_nodes / num_ous))
    split_comps = list(split_seq(temp_comps, split_num))
    props = []

    for i in range(0, num_ous):
        ou = ous_list[i]

        try:
            ou_comps = split_comps[i]
            ouname = "{}_COMPUTERS@{}".format(ou, domain_name)
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
        except IndexError:
            ouname = "{}_COMPUTERS@{}".format(ou, domain_name)
            guid = str(uuid.uuid4())
            ou_guid_map[ouname] = guid
            ou_properties = {
                'ouguid': guid,
                'ouname': ouname
            }
            ou_props.append(ou_properties)
            session.run(
                """
                CREATE (n:Base {objectid:$sid})
                SET n:OU,n.name=$name, n.blocksInheritance=false, n.highvalue=false
                """,
                sid=ou_properties["ouguid"],
                name=ou_properties["ouname"]
                )

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


def create_users_ous(session, domain_name, users, ou_guid_map, ou_props, num_nodes, ous_list):
    """
    Create OUs for users.

    Arguments:
        session     -- the current session
        domain_name -- the domain name
        users       -- a list containing the various users
        ou_guid_map -- a map of OUs guid
        ou_props    -- a list containing the properties of the various OUs
        num_nodes   -- the number of nodes
        ous_list    -- a list containing the names of the various OUs

    Returns:
        ou_props    -- a list containing the properties of the various OUs
        ou_guid_map -- a map of OUs guid
    """
    temp_users = users
    random.shuffle(temp_users)
    num_ous = len(ous_list)
    split_num = int(math.ceil(num_nodes / num_ous))
    split_users = list(split_seq(temp_users, split_num))
    props = []

    for i in range(0, num_ous):
        ou = ous_list[i]

        try:
            ou_users = split_users[i]
            ouname = "{}_USERS@{}".format(ou, domain_name)
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
        except IndexError:
            ouname = "{}_USERS@{}".format(ou, domain_name)
            guid = str(uuid.uuid4())
            ou_guid_map[ouname] = guid
            ou_properties = {
                'ouguid': guid,
                'ouname': ouname
            }
            ou_props.append(ou_properties)
            session.run(
                """
                CREATE (n:Base {objectid:$sid})
                SET n:OU,n.name=$name, n.blocksInheritance=false, n.highvalue=false
                """,
                sid=ou_properties["ouguid"],
                name=ou_properties["ouname"]
                )

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


def link_ous_to_domain(session, domain_name, ou_guid_map):
    """
    Links the OUs to the domain

    Arguments:
        session     -- the current session
        domain_name -- the domain name
        ou_guid_map -- a map of OUs guid
    """
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
        domain=domain_name
    )
