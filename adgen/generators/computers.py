import math
import random

from adgen.config import STATES, SERVER_OS_LIST, CLIENT_OS_LIST
from adgen.utils.utils import cn, cs


def create_computers(session, domain, sid, nodes, computers):
    print("Generating Computer Nodes")
    computer_props_list = []
    group = "DOMAIN COMPUTERS@{}".format(domain)
    props = []
    ridcount = 1000
    client_os_list = CLIENT_OS_LIST

    for i in range(1, nodes + 1):
        comp_name = "COMP{:05d}.{}".format(i, domain)
        computers.append(comp_name)
        os = random.choice(client_os_list)
        enabled = True
        computer_props = {
            "id": cs(ridcount, sid),
            "props": {
                "name": comp_name,
                "operatingsystem": os,
                "enabled": enabled
            }
        }
        props.append(computer_props)
        computer_props_list.append(computer_props)
        ridcount += 1

        if len(props) > 500:
            session.run(
                """
                UNWIND $props as prop
                MERGE (n:Base {objectid: prop.id})
                SET n:Computer, n += prop.props
                WITH n
                MERGE (m:Group {name:$gname})
                WITH n,m
                MERGE (n)-[:MemberOf]->(m)
                """,
                props=props,
                gname=group
            )
            props = []
    session.run(
        """
        UNWIND $props as prop
        MERGE (n:Base {objectid:prop.id})
        SET n:Computer, n += prop.props
        WITH n
        MERGE (m:Group {name:$gname})
        WITH n,m
        MERGE (n)-[:MemberOf]->(m)
        """,
        props=props,
        gname=group
    )
    return computer_props_list, computers, ridcount


def create_dcs(session, domain, sid, dcou, ridcount):
    print("Creating Domain Controllers")
    dc_props_list = []
    os_list = SERVER_OS_LIST
    states = STATES

    for state in states:
        comp_name = cn(f"{state}LABDC", domain)
        group_name = cn("DOMAIN CONTROLLERS", domain)
        sid = cs(ridcount, sid)
        os = random.choice(os_list)
        enabled = True

        dc_props = {
            "name": comp_name,
            "id": sid,
            "operatingsystem": os,
            "enabled": enabled,
        }
        ridcount += 1
        dc_props_list.append(dc_props)

        session.run(
            """
            MERGE (n:Base {objectid:$sid})
            SET n:Computer,n.name=$name, n.operatingsystem=$os, n.enabled=$enabled
            WITH n
            MATCH (m:Group {name:$gname})
            WITH n,m
            MERGE (n)-[:MemberOf]->(m)
            """,
            sid=sid,
            name=comp_name,
            gname=group_name,
            os=dc_props["operatingsystem"],
            enabled=dc_props["enabled"]
        )

        session.run(
            """
            MATCH (n:Computer {objectid:$sid})
            WITH n 
            MATCH (m:OU {objectid:$dcou})
            WITH n,m
            MERGE (m)-[:Contains]->(n)
            """,
            sid=sid,
            dcou=dcou
        )

        session.run(
            """
            MATCH (n:Computer {objectid:$sid})
            WITH n
            MATCH (m:Group {name:$gname})
            WITH n,m
            MERGE (n)-[:MemberOf]->(m)
            """,
            sid=sid,
            gname=cn("ENTERPRISE DOMAIN CONTROLLERS", domain)
        )

        session.run(
            """
            MERGE (n:Computer {objectid:$sid})
            WITH n
            MERGE (m:Group {name:$gname})
            WITH n,m
            MERGE (m)-[:AdminTo]->(n)
            """,
            sid=sid,
            gname=cn("DOMAIN ADMINS", domain)
        )
    return dc_props_list, ridcount


def add_rdp_users(session, computers, it_users, count):
    props = []
    for i in range(0, count):
        comp = random.choice(computers)
        user = random.choice(it_users)
        props.append({'a': user, 'b': comp})

    session.run(
        """
        UNWIND $props AS prop
        MERGE (n:User {name: prop.a})
        MERGE (m:Computer {name: prop.b})
        MERGE (n)-[r:CanRDP]->(m)
        """,
        props=props
    )


def add_rdp_groups(session, computers, it_groups, count):
    props = []
    for i in range(0, count):
        comp = random.choice(computers)
        user = random.choice(it_groups)
        props.append({'a': user, 'b': comp})

    session.run(
        """
        UNWIND $props AS prop
        MERGE (n:Group {name: prop.a})
        MERGE (m:Computer {name: prop.b})
        MERGE (n)-[r:CanRDP]->(m)
        """,
        props=props
    )


def add_execute_dcom_users(session, computers, it_users, count):
    props = []
    for i in range(0, count):
        comp = random.choice(computers)
        user = random.choice(it_users)
        props.append({'a': user, 'b': comp})

    session.run(
        """
        UNWIND $props AS prop
        MERGE (n:User {name: prop.a})
        MERGE (m:Computer {name: prop.b})
        MERGE (n)-[r:ExecuteDCOM]->(m)
        """,
        props=props
    )


def add_execute_dcom_groups(session, computers, it_groups, count):
    props = []
    for i in range(0, count):
        comp = random.choice(computers)
        user = random.choice(it_groups)
        props.append({'a': user, 'b': comp})

    session.run(
        """
        UNWIND $props AS prop
        MERGE (n:Group {name: prop.a})
        MERGE (m:Computer {name: prop.b})
        MERGE (n)-[r:ExecuteDCOM]->(m)
        """,
        props=props
    )


def add_allowed_to_delegate_to_users(session, computers, it_users, count):
    props = []
    for i in range(0, count):
        comp = random.choice(computers)
        user = random.choice(it_users)
        props.append({'a': user, 'b': comp})

    session.run(
        """
        UNWIND $props AS prop
        MERGE (n:User {name: prop.a})
        MERGE (m:Computer {name: prop.b})
        MERGE (n)-[r:AllowedToDelegate]->(m)
        """,
        props=props
    )


def add_allowed_to_delegate_to_computers(session, computers, count):
    props = []
    for i in range(0, count):
        comp = random.choice(computers)
        user = random.choice(computers)
        if comp == user:
            continue
        props.append({'a': user, 'b': comp})

    session.run(
        """
        UNWIND $props AS prop
        MERGE (n:Computer {name: prop.a})
        MERGE (m:Computer {name: prop.b})
        MERGE (n)-[r:AllowedToDelegate]->(m)
        """,
        props=props
    )


def add_rdp_dcom_delegate(session, computers, it_users, it_groups):
    print("Adding RDP/ExecuteDCOM/AllowedToDelegateTo")
    count = int(math.floor(len(computers) * .1))
    add_rdp_users(session, computers, it_users, count)
    add_execute_dcom_users(session, computers, it_users, count)
    add_rdp_groups(session, computers, it_groups, count)
    add_execute_dcom_groups(session, computers, it_groups, count)
    add_allowed_to_delegate_to_users(session, computers, it_users, count)
    add_allowed_to_delegate_to_computers(session, computers, count)


def add_sessions(session, nodes, computers, users, das):
    print("Adding sessions")
    max_sessions_per_user = int(math.ceil(math.log10(nodes)))
    props = []
    for user in users:
        num_sessions = random.randrange(0, max_sessions_per_user)
        if user in das:
            num_sessions = max(num_sessions, 1)

        if num_sessions == 0:
            continue

        for c in random.sample(computers, num_sessions):
            props.append({'a': user, 'b': c})

        if len(props) > 500:
            session.run(
                """
                UNWIND $props AS prop
                MERGE (n:User {name:prop.a})
                WITH n,prop
                MERGE (m:Computer {name:prop.b})
                WITH n,m
                MERGE (m)-[:HasSession]->(n)
                """,
                props=props
            )
            props = []

    session.run(
        """
        UNWIND $props AS prop
        MERGE (n:User {name:prop.a})
        WITH n,prop
        MERGE (m:Computer {name:prop.b})
        WITH n,m
        MERGE (m)-[:HasSession]->(n)
        """,
        props=props
    )


def add_unconstrained_delegation(session, computers):
    print("Adding unconstrained delegation to a few computers")
    i = random.randint(10, 20)
    i = min(i, len(computers))
    for computer in random.sample(computers, i):
        session.run(
            """
            MATCH (n:Computer {name:$computer})
            SET n.unconstrainteddelegation=true
            """,
            computer=computer
        )
