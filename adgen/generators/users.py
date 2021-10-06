import random

from adgen.utils.utils import cs, generate_timestamp


def create_users(session, domain, sid, nodes, current_time, first_names, last_names, users, ridcount):
    print("Generating User Nodes")
    user_props = []
    group = "DOMAIN USERS@{}".format(domain)
    props = []

    for i in range(1, nodes + 1):
        first = random.choice(first_names)
        last = random.choice(last_names)
        user_name = "{}{}{:05d}@{}".format(first[0], last, i, domain).upper()
        user_name = user_name.format(first[0], last, i).upper()
        users.append(user_name)
        dispname = "{} {}".format(first, last)
        enabled = True
        pwdlastset = generate_timestamp(current_time)
        lastlogon = generate_timestamp(current_time)
        ridcount += 1
        objectsid = cs(ridcount, sid)

        user_properties = {
            'id': objectsid,
            'props': {
                'displayname': dispname,
                'name': user_name,
                'enabled': enabled,
                'pwdlastset': pwdlastset,
                'lastlogon': lastlogon
            }
        }

        props.append(user_properties)
        user_props.append(user_properties)

        if len(props) > 500:
            session.run(
                """
                UNWIND $props as prop
                MERGE (n:Base {objectid:prop.id})
                SET n:User, n += prop.props
                WITH n
                MATCH (m:Group {name:$gname})
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
        SET n:User, n += prop.props
        WITH n
        MATCH (m:Group {name:$gname})
        WITH n,m
        MERGE (n)-[:MemberOf]->(m)
        """,
        props=props,
        gname=group
    )

    return user_props, users, ridcount


def add_kerberoastable_users(session, it_users):
    print("Marking some users as Kerberoastable")
    i = random.randint(10, 20)
    i = min(i, len(it_users))
    for user in random.sample(it_users, i):
        session.run(
            """
            MATCH (n:User {name:$user})
            SET n.hasspn=true
            """,
            user=user
        )
