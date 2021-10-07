import random
import uuid

from adgen.utils.utils import cn


def create_default_gpos(session, domain_name, ddp, ddcp):
    base_statement = "MERGE (n:Base {name:$gpo, objectid:$guid}) SET n:GPO"
    session.run(base_statement, gpo=cn("DEFAULT DOMAIN POLICY", domain_name), guid=ddp)
    session.run(base_statement, gpo=cn("DEFAULT DOMAIN CONTROLLERS POLICY", domain_name), guid=ddcp)


def link_default_gpos(session, domain_name, dcou):
    gpo_name = "DEFAULT DOMAIN POLICY@{}".format(domain_name)
    session.run(
        """
        MERGE (n:GPO {name:$gpo})
        MERGE (m:Domain {name:$domain})
        MERGE (n)-[:GpLink {isacl:false, enforced:toBoolean(false)}]->(m)
        """,
        gpo=gpo_name,
        domain=domain_name
    )

    session.run(
        """
        MERGE (n:Domain {name:$domain})
        MERGE (m:OU {objectid:$guid})
        MERGE (n)-[:Contains {isacl:false}]->(m)
        """,
        domain=domain_name,
        guid=dcou
    )

    gpo_name = "DEFAULT DOMAIN CONTROLLERS POLICY@{}".format(domain_name)
    session.run(
        """
        MERGE (n:GPO {name:$gpo})
        MERGE (m:OU {objectid:$guid})
        MERGE (n)-[:GpLink {isacl:false, enforced:toBoolean(false)}]->(m)
        """,
        gpo=gpo_name,
        guid=dcou
    )


def create_gpos(session, domain_name, gpos):
    print("Creating GPOs")
    for i in range(1, 20):
        gpo_name = "GPO_{}@{}".format(i, domain_name)
        guid = str(uuid.uuid4()).upper()
        session.run(
            """
            MERGE (n:Base {name:$gponame})
            SET n:GPO, n.objectid=$guid
            """,
            gponame=gpo_name,
            guid=guid
        )
        gpos.append(gpo_name)
    return gpos


def link_gpos_to_ous(session, gpos, ou_names, ou_guid_map):
    for g in gpos:
        num_links = random.randint(1, 3)
        linked_ous = random.sample(ou_names, num_links)
        for link in linked_ous:
            guid = ou_guid_map[link]
            session.run(
                """
                MERGE (n:GPO {name:$gponame})
                WITH n
                MERGE (m:OU {objectid:$guid})
                WITH n,m
                MERGE (n)-[r:GpLink]->(m)
                """,
                gponame=g,
                guid=guid
            )


def link_domain_to_ous(session, domain_name, ou_names, ou_guid_map):
    num_links = random.randint(1, 3)
    linked_ous = random.sample(ou_names, num_links)
    for link in linked_ous:
        guid = ou_guid_map[link]
        session.run(
            """
            MERGE (n:Domain {name:$gponame})
            WITH n
            MERGE (m:OU {objectid:$guid})
            WITH n,m
            MERGE (n)-[r:GpLink]->(m)
            """,
            gponame=domain_name,
            guid=guid
        )


def link_to_ous(session, gpos, domain_name, ou_guid_map):
    ou_names = list(ou_guid_map.keys())
    link_domain_to_ous(session, domain_name, ou_names, ou_guid_map)
    link_gpos_to_ous(session, gpos, ou_names, ou_guid_map)
    gpos.append("DEFAULT DOMAIN POLICY@{}".format(domain_name))
    gpos.append("DEFAULT DOMAIN CONTROLLER POLICY@{}".format(domain_name))
