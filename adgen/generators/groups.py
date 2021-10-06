import math
import random

from adgen.config import PARTITIONS
from adgen.utils.utils import cn, cs, cws


def create_domain_nodes(session, domain, sid):
    base_statement = "MERGE (n:Base {name: $gname}) SET n:Group, n.objectid=$sid"
    session.run(f"{base_statement},n.highvalue=true", sid=cs(512, sid), gname=cn("DOMAIN ADMINS", domain))
    session.run(base_statement, sid=cs(515, sid), gname=cn("DOMAIN COMPUTERS", domain))
    session.run(base_statement, gname=cn("DOMAIN USERS", domain), sid=cs(513, sid))


def create_domain_controllers(session, domain, sid):
    base_statement = "MERGE (n:Base {name: $gname}) SET n:Group, n.objectid=$sid"
    session.run(f"{base_statement},n.highvalue=true", gname=cn("DOMAIN CONTROLLERS", domain), sid=cs(516, sid))
    session.run(f"{base_statement},n.highvalue=true", gname=cn("ENTERPRISE DOMAIN CONTROLLERS", domain), sid=cws("S-1-5-9", sid))
    session.run(base_statement, gname=cn("ENTERPRISE READ-ONLY DOMAIN CONTROLLERS", domain), sid=cs(498, sid))


def create_administrators(session, domain, sid):
    base_statement = "MERGE (n:Base {name: $gname}) SET n:Group, n.objectid=$sid"
    session.run(f"{base_statement},n.highvalue=true", gname=cn("ADMINISTRATORS", domain), sid=cs(544, sid))
    session.run(f"{base_statement},n.highvalue=true", gname=cn("ENTERPRISE ADMINS", domain), sid=cs(519, sid))


def create_domain(session, domain, sid):
    session.run(
        """
        MERGE (n:Base {name:$domain})
        SET n:Domain, n.highvalue=true, n.objectid=$objectid
        """,
        domain=domain,
        objectid=sid
    )


def data_generation(session, domain, sid, nodes):
    print("Starting data generation with nodes={}".format(nodes))
    create_domain_nodes(session, domain, sid)
    create_domain_controllers(session, domain, sid)
    create_administrators(session, domain, sid)
    create_domain(session, domain, sid)


def create_groups(session, domain, sid, nodes, groups, ridcount):
    print("Generating Group Nodes")
    dept_list = PARTITIONS
    props = []
    group_props_list = []

    for i in range(1, nodes + 1):
        dept = random.choice(dept_list)
        group = "{}{:05d}@{}".format(dept, i, domain)
        groups.append(group)
        sid = cs(ridcount, sid)
        ridcount += 1
        group_props = {
            "name": group,
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


def add_domain_admins(session, domain, nodes, users):
    dapctint = random.randint(3, 5)
    dapct = float(dapctint) / 100
    danum = int(math.ceil(nodes * dapct))
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
            gname=cn("DOMAIN ADMINS", domain))
    return das


def create_nested_groups(session, nodes, groups):
    print("Applying random group nesting")
    max_nest = int(round(math.log10(nodes)))
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


def add_users_to_group(session, nodes, users, groups, das):
    print("Adding users to groups")
    props = []
    a = math.log10(nodes)
    a = math.pow(a, 2)
    a = math.floor(a)
    a = int(a)
    num_groups_base = a
    variance = int(math.ceil(math.log10(nodes)))
    it_users = []

    print("Calculated {} groups per user with a variance of - {}".format(num_groups_base, variance * 2))

    dept_list = PARTITIONS

    for user in users:
        dept = random.choice(dept_list)
        if dept == "IT":
            it_users.append(user)
        possible_groups = [x for x in groups if dept in x]

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
