import math
import random

from adgen.utils.support_functions import cn, cs, cws


def create_domain_nodes(session, domain_name, domain_sid):
    """
    Creates the domain nodes.

    Arguments:
        session     -- the current session
        domain_name -- the domain name
        domain_sid  -- the domain sid
    """
    base_statement = "MERGE (n:Base {name: $gname}) SET n:Group, n.objectid=$sid"
    session.run(f"{base_statement},n.highvalue=true", sid=cs(512, domain_sid), gname=cn("DOMAIN ADMINS", domain_name))
    session.run(base_statement, sid=cs(515, domain_sid), gname=cn("DOMAIN COMPUTERS", domain_name))
    session.run(base_statement, gname=cn("DOMAIN USERS", domain_name), sid=cs(513, domain_sid))


def create_domain_controllers(session, domain_name, domain_sid):
    """
    Creates the domain controllers.

    Arguments:
        session     -- the current session
        domain_name -- the domain name
        domain_sid  -- the domain sid
    """
    base_statement = "MERGE (n:Base {name: $gname}) SET n:Group, n.objectid=$sid"
    session.run(f"{base_statement},n.highvalue=true", gname=cn("DOMAIN CONTROLLERS", domain_name), sid=cs(516, domain_sid))
    session.run(f"{base_statement},n.highvalue=true", gname=cn("ENTERPRISE DOMAIN CONTROLLERS", domain_name), sid=cws("S-1-5-9", domain_sid))
    session.run(base_statement, gname=cn("ENTERPRISE READ-ONLY DOMAIN CONTROLLERS", domain_name), sid=cs(498, domain_sid))


def create_administrators(session, domain_name, domain_sid):
    """
    Creates the administrators.

    Arguments:
        session     -- the current session
        domain_name -- the domain name
        domain_sid  -- the domain sid
    """
    base_statement = "MERGE (n:Base {name: $gname}) SET n:Group, n.objectid=$sid"
    session.run(f"{base_statement},n.highvalue=true", gname=cn("ADMINISTRATORS", domain_name), sid=cs(544, domain_sid))
    session.run(f"{base_statement},n.highvalue=true", gname=cn("ENTERPRISE ADMINS", domain_name), sid=cs(519, domain_sid))


def create_domain(session, domain_name, domain_sid):
    """
    Creates the domain.

    Arguments:
        session     -- the current session
        domain_name -- the domain name
        domain_sid  -- the domain sid
    """
    session.run(
        """
        MERGE (n:Base {name:$domain})
        SET n:Domain, n.highvalue=true, n.objectid=$objectid
        """,
        domain=domain_name,
        objectid=domain_sid
    )


def data_generation(session, domain_name, domain_sid):
    create_domain_nodes(session, domain_name, domain_sid)
    create_domain_controllers(session, domain_name, domain_sid)
    create_administrators(session, domain_name, domain_sid)
    create_domain(session, domain_name, domain_sid)


def create_groups(session, domain_name, domain_sid, num_nodes, groups, ridcount, groups_list):
    """
    Creates groups.

    Arguments:
        session     -- the current session
        domain_name -- the domain name
        domain_sid  -- the domain sid
        num_nodes   -- the number of nodes
        groups      -- a list containing the various groups
        ridcount    -- the current rid value

    Returns:
        group_props_list -- a list containing the properties of the various groups
        groups           -- a list containing the various groups
        ridcount         -- th new rid value
    """
    props = []
    group_props_list = []

    for i in range(1, num_nodes + 1):
        group = random.choice(groups_list)
        group_name = "{}{:05d}@{}".format(group, i, domain_name)
        groups.append(group_name)
        sid = cs(ridcount, domain_sid)
        ridcount += 1
        group_props = {
            "name": group_name,
            "id": sid
        }
        props.append(group_props)
        group_props_list.append(group_props)

        if len(props) > 500:
            session.run(
                """
                UNWIND $props as prop
                MERGE (n:Base {objectid:prop.id})
                SET n:Group, n.name=prop.name
                """,
                props=props
            )
            props = []

    session.run(
        """
        UNWIND $props as prop
        MERGE (n:Base {objectid:prop.id})
        SET n:Group, n.name=prop.name
        """,
        props=props
    )
    return group_props_list, groups, ridcount


def add_domain_admins(session, domain_name, num_nodes, users):
    """
    Create domain administrators.

    Arguments:
        session     -- the current session
        domain_name -- the domain name
        num_nodes   -- the number of nodes
        users       -- a list containing the various users

    Returns:
        das -- domain administrators
    """
    dapctint = random.randint(3, 5)
    dapct = float(dapctint) / 100
    danum = int(math.ceil(num_nodes * dapct))
    danum = min([danum, 30])
    print("Creating {} Domain Admins ({}% of users capped at 30)".format(danum, dapctint))
    das = random.sample(users, danum)

    for da in das:
        session.run(
            """
            MERGE (n:User {name:$name})
            WITH n
            MERGE (m:Group {name:$gname})
            WITH n,m
            MERGE (n)-[:MemberOf]->(m)
            """,
            name=da,
            gname=cn("DOMAIN ADMINS", domain_name))
    return das


def create_nested_groups(session, num_nodes, groups):
    """
    Create nested groups.

    Arguments:
        session   -- the current session
        num_nodes -- the number of nodes
        groups    -- a list containing the various groups
    """
    max_nest = int(round(math.log10(num_nodes)))
    props = []

    for group in groups:
        if random.randrange(0, 100) < 10:
            num_nest = random.randrange(1, max_nest)
            dept = group[0:-19]
            dpt_groups = [x for x in groups if dept in x]
            if num_nest > len(dpt_groups):
                num_nest = random.randrange(1, len(dpt_groups))
            to_nest = random.sample(dpt_groups, num_nest)
            for g in to_nest:
                if not g == group:
                    props.append({'a': group, 'b': g})

        if len(props) > 500:
            session.run(
                """
                UNWIND $props AS prop
                MERGE (n:Group {name:prop.a})
                WITH n,prop
                MERGE (m:Group {name:prop.b})
                WITH n,m
                MERGE (n)-[:MemberOf]->(m)
                """,
                props=props
            )
            props = []

    session.run(
        """
        UNWIND $props AS prop
        MERGE (n:Group {name:prop.a})
        WITH n,prop
        MERGE (m:Group {name:prop.b})
        WITH n,m
        MERGE (n)-[:MemberOf]->(m)
        """,
        props=props)


def add_users_to_group(session, num_nodes, users, groups, das, groups_list):
    """
    Adds users to groups.

    Arguments:
        session     -- the current session
        num_nodes   -- the number of nodes
        users       -- a list containing the various users
        groups      -- a list containing the various groups
        das         -- domain administrators
        groups_list -- a list containing the available groups

    Returns:
        it_users -- a list of it users
    """
    props = []
    a = math.log10(num_nodes)
    a = math.pow(a, 2)
    a = math.floor(a)
    a = int(a)
    num_groups_base = a
    variance = int(math.ceil(math.log10(num_nodes)))
    it_users = []

    print("Calculated {} groups per user with a variance of - {}".format(num_groups_base, variance * 2))

    for user in users:
        group = random.choice(groups_list)
        if group == "IT":
            it_users.append(user)
        possible_groups = [x for x in groups if group in x]

        sample = num_groups_base + random.randrange(-(variance * 2), 0)
        if sample > len(possible_groups):
            sample = int(math.floor(float(len(possible_groups)) / 4))

        if sample <= 1:
            continue

        to_add = random.sample(possible_groups, sample)

        for group in to_add:
            props.append({'a': user, 'b': group})

        if len(props) > 500:
            session.run(
                """
                UNWIND $props AS prop
                MERGE (n:User {name:prop.a})
                WITH n,prop
                MERGE (m:Group {name:prop.b})
                WITH n,m
                MERGE (n)-[:MemberOf]->(m)
                """,
                props=props)
            props = []

    session.run(
        """
        UNWIND $props AS prop
        MERGE (n:User {name:prop.a})
        WITH n,prop
        MERGE (m:Group {name:prop.b})
        WITH n,m
        MERGE (n)-[:MemberOf]->(m)
        """,
        props=props)

    it_users = it_users + das
    it_users = list(set(it_users))
    return it_users
