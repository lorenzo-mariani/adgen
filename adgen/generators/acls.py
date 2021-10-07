import random
import math

from adgen.generators.gpos import link_default_gpos
from adgen.utils.utils import cs


def create_enterprise_admins(session, domain_name):
    group_name = "ENTERPRISE ADMINS@{}".format(domain_name)
    session.run(
        """
        MERGE (n:Domain {name:$domain})
        MERGE (m:Group {name:$gname})
        MERGE (m)-[:GenericAll {isacl:true}]->(n)
        """,
        domain=domain_name,
        gname=group_name
    )


def create_administrators(session, domain_name):
    group_name = "ADMINISTRATORS@{}".format(domain_name)
    session.run(
        """
        MERGE (n:Domain {name:$domain})
        MERGE (m:Group {name:$gname})
        MERGE (m)-[:Owns {isacl:true}]->(n)
        """,
        domain=domain_name,
        gname=group_name
    )

    session.run(
        """
        MERGE (n:Domain {name:$domain})
        WITH n
        MERGE (m:Group {name:$gname})
        WITH n,m
        MERGE (m)-[:WriteOwner {isacl:true}]->(n)
        """,
        domain=domain_name,
        gname=group_name
    )

    session.run(
        """
        MERGE (n:Domain {name:$domain})
        WITH n
        MERGE (m:Group {name:$gname})
        WITH n,m
        MERGE (m)-[:WriteDacl {isacl:true}]->(n)
        """,
        domain=domain_name,
        gname=group_name
    )

    session.run(
        """
        MERGE (n:Domain {name:$domain})
        WITH n
        MERGE (m:Group {name:$gname})
        WITH n,m
        MERGE (m)-[:DCSync {isacl:true}]->(n)
        """,
        domain=domain_name,
        gname=group_name
    )

    session.run(
        """
        MERGE (n:Domain {name:$domain})
        WITH n
        MERGE (m:Group {name:$gname})
        WITH n,m
        MERGE (m)-[:GetChanges {isacl:true}]->(n)
        """,
        domain=domain_name,
        gname=group_name
    )

    session.run(
        """
        MERGE (n:Domain {name:$domain})
        WITH n
        MERGE (m:Group {name:$gname})
        WITH n,m
        MERGE (m)-[:GetChangesAll {isacl:true}]->(n)
        """,
        domain=domain_name,
        gname=group_name
    )


def create_domain_admins(session, domain_name):
    group_name = "DOMAIN ADMINS@{}".format(domain_name)
    session.run(
        """
        MERGE (n:Domain {name:$domain})
        WITH n
        MERGE (m:Group {name:$gname})
        WITH n,m
        MERGE (m)-[:WriteOwner {isacl:true}]->(n)
        """,
        domain=domain_name,
        gname=group_name
    )

    session.run(
        """
        MERGE (n:Domain {name:$domain})
        WITH n
        MERGE (m:Group {name:$gname})
        WITH n,m
        MERGE (m)-[:WriteDacl {isacl:true}]->(n)
        """,
        domain=domain_name,
        gname=group_name
    )

    session.run(
        """
        MERGE (n:Domain {name:$domain})
        WITH n
        MERGE (m:Group {name:$gname})
        WITH n,m
        MERGE (m)-[:DCSync {isacl:true}]->(n)
        """,
        domain=domain_name,
        gname=group_name
    )

    session.run(
        """
        MERGE (n:Domain {name:$domain})
        WITH n
        MERGE (m:Group {name:$gname})
        WITH n,m
        MERGE (m)-[:GetChanges {isacl:true}]->(n)
        """,
        domain=domain_name,
        gname=group_name)

    session.run(
        """
        MERGE (n:Domain {name:$domain})
        WITH n
        MERGE (m:Group {name:$gname})
        WITH n,m
        MERGE (m)-[:GetChangesAll {isacl:true}]->(n)
        """,
        domain=domain_name,
        gname=group_name
    )


def create_enterprise_dcs(session, domain_name):
    group_name = "ENTERPRISE DOMAIN CONTROLLERS@{}".format(domain_name)
    session.run(
        """
        MERGE (n:Domain {name:$domain})
        WITH n
        MERGE (m:Group {name:$gname})
        WITH n,m
        MERGE (m)-[:GetChanges {isacl:true}]->(n)
        """,
        domain=domain_name,
        gname=group_name
    )

    group_name = "ENTERPRISE READ-ONLY DOMAIN CONTROLLERS@{}".format(domain_name)
    session.run(
        """
        MERGE (n:Domain {name:$domain})
        WITH n
        MERGE (m:Group {name:$gname})
        WITH n,m
        MERGE (m)-[:GetChanges {isacl:true}]->(n)
        """,
        domain=domain_name,
        gname=group_name
    )

    group_name = "DOMAIN CONTROLLERS@{}".format(domain_name)
    session.run(
        """
        MERGE (n:Domain {name:$domain})
        WITH n
        MERGE (m:Group {name:$gname})
        WITH n,m
        MERGE (m)-[:GetChangesAll {isacl:true}]->(n)
        """,
        domain=domain_name,
        gname=group_name
    )


def add_standard_edges(session, domain_name, dcou):
    print("Adding Standard Edges")
    link_default_gpos(session, domain_name, dcou)
    create_enterprise_admins(session, domain_name)
    create_administrators(session, domain_name)
    create_domain_admins(session, domain_name)
    create_enterprise_dcs(session, domain_name)


def add_domain_admin_to_local_admin(session, domain_sid):
    print("Adding Domain Admins to Local Admins of Computers")
    session.run(
        """
        MATCH (n:Computer)
        MATCH (m:Group {objectid: $id})
        MERGE (m)-[:AdminTo]->(n)
        """,
        id=cs(512, domain_sid)
    )


def add_local_admin_rights(session, groups, computers):
    print("Adding local admin rights")
    it_groups = [x for x in groups if "IT" in x]
    random.shuffle(it_groups)

    if len(it_groups) < 4:
        max_lim = len(it_groups)
    else:
        max_lim = 4

    super_groups = random.sample(it_groups, max_lim)
    super_group_num = int(math.floor(len(computers) * .85))
    it_groups = [x for x in it_groups if not x in super_groups]
    total_it_groups = len(it_groups)
    dist_a = int(math.ceil(total_it_groups * .6))
    dist_b = int(math.ceil(total_it_groups * .3))
    dist_c = int(math.ceil(total_it_groups * .07))
    dist_d = int(math.ceil(total_it_groups * .03))

    distribution_list = [1] * dist_a + [2] * dist_b + [10] * dist_c + [50] * dist_d

    props = []
    for x in range(0, total_it_groups):
        g = it_groups[x]
        dist = distribution_list[x]

        to_add = random.sample(computers, dist)
        for a in to_add:
            props.append({"a": g, "b": a})

        if len(props) > 500:
            session.run(
                """
                UNWIND $props AS prop
                MERGE (n:Group {name:prop.a})
                WITH n,prop
                MERGE (m:Computer {name:prop.b})
                WITH n,m
                MERGE (n)-[:AdminTo]->(m)
                """,
                props=props
            )
            props = []

    for x in super_groups:
        for a in random.sample(computers, super_group_num):
            props.append({"a": x, "b": a})

        if len(props) > 500:
            session.run(
                """
                UNWIND $props AS prop
                MERGE (n:Group {name:prop.a})
                WITH n,prop
                MERGE (m:Computer {name:prop.b})
                WITH n,m MERGE (n)-[:AdminTo]->(m)
                """,
                props=props
            )
            props = []

    session.run(
        """
        UNWIND $props AS prop
        MERGE (n:Group {name:prop.a})
        WITH n,prop
        MERGE (m:Computer {name:prop.b})
        WITH n,m
        MERGE (n)-[:AdminTo]->(m)
        """,
        props=props
    )
    return it_groups


def add_domain_admin_aces(session, domain_name, computers, users, groups):
    print("Adding Domain Admin ACEs")
    group_name = "DOMAIN ADMINS@{}".format(domain_name)
    props = []
    for x in computers:
        props.append({'name': x})

        if len(props) > 500:
            session.run(
                """
                UNWIND $props as prop
                MATCH (n:Computer {name:prop.name})
                WITH n
                MATCH (m:Group {name:$gname})
                WITH m,n
                MERGE (m)-[r:GenericAll {isacl:true}]->(n)
                """,
                props=props,
                gname=group_name
            )
            props = []

    session.run(
        """
        UNWIND $props as prop
        MATCH (n:Computer {name:prop.name})
        WITH n
        MATCH (m:Group {name:$gname})
        WITH m,n
        MERGE (m)-[r:GenericAll {isacl:true}]->(n)
        """,
        props=props,
        gname=group_name
    )

    for x in users:
        props.append({'name': x})

        if len(props) > 500:
            session.run(
                """
                UNWIND $props as prop
                MATCH (n:User {name:prop.name})
                WITH n
                MATCH (m:Group {name:$gname})
                WITH m,n
                MERGE (m)-[r:GenericAll {isacl:true}]->(n)
                """,
                props=props,
                gname=group_name
            )
            props = []

    session.run(
        """
        UNWIND $props as prop
        MATCH (n:User {name:prop.name})
        WITH n
        MATCH (m:Group {name:$gname})
        WITH m,n
        MERGE (m)-[r:GenericAll {isacl:true}]->(n)
        """,
        props=props,
        gname=group_name
    )

    for x in groups:
        props.append({'name': x})

        if len(props) > 500:
            session.run(
                """
                UNWIND $props as prop
                MATCH (n:Group {name:prop.name})
                WITH n
                MATCH (m:Group {name:$gname})
                WITH m,n
                MERGE (m)-[r:GenericAll {isacl:true}]->(n)
                """,
                props=props,
                gname=group_name
            )
            props = []

    session.run(
        """
        UNWIND $props as prop
        MATCH (n:Group {name:prop.name})
        WITH n
        MATCH (m:Group {name:$gname})
        WITH m,n
        MERGE (m)-[r:GenericAll {isacl:true}]->(n)
        """,
        props=props,
        gname=group_name
    )


def add_outbound_acls(session, it_groups, it_users, gpos, computers, acl_list):
    num_acl_principals = int(round(len(it_groups) * .1))
    print("Adding outbound ACLs to {} objects".format(num_acl_principals))
    acl_groups = random.sample(it_groups, num_acl_principals)
    all_principals = it_users + it_groups

    for i in acl_groups:
        ace = random.choice(acl_list)
        ace_string = '[r:' + ace + '{isacl:true}]'
        if ace == "GenericAll" or ace == "GenericWrite" or ace == "WriteOwner" or ace == "WriteDacl":
            p = random.choice(all_principals)
            p2 = random.choice(gpos)
            session.run(
                """
                MERGE (n:Group {name:$group})
                MERGE (m {name:$principal})
                MERGE (n)-""" + ace_string + "->(m)",
                group=i,
                principal=p
            )
            session.run(
                """
                MERGE (n:Group {name:$group})
                MERGE (m:GPO {name:$principal})
                MERGE (n)-""" + ace_string + "->(m)",
                group=i,
                principal=p2
            )
        elif ace == "AddMember":
            p = random.choice(it_groups)
            session.run(
                """
                MERGE (n:Group {name:$group})
                MERGE (m:Group {name:$principal})
                MERGE (n)-""" + ace_string + "->(m)",
                group=i,
                principal=p
            )
        elif ace == "ReadLAPSPassword":
            p = random.choice(all_principals)
            targ = random.choice(computers)
            session.run(
                """
                MERGE (n {name:$principal})
                MERGE (m:Computer {name:$target})
                MERGE (n)-[r:ReadLAPSPassword]->(m)
                """,
                target=targ,
                principal=p
            )
        else:
            p = random.choice(it_users)
            session.run(
                """
                MERGE (n:Group {name:$group})
                MERGE (m:User {name:$principal})
                MERGE (n)-""" + ace_string + "->(m)",
                group=i,
                principal=p
            )
