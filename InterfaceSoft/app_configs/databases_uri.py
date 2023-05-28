import psycopg2
from InterfaceSoft.local_configs import DATABASE_PASSWORD, get_nodes_list

NODES_LIST = get_nodes_list()
db_uris = []

for node in NODES_LIST:
    if "Data-Server" in node["hostname"]:
        # Append the node to the corresponding list based on its hostname
        db_uris.append(f"postgresql://postgres:{DATABASE_PASSWORD}@{node['ip']}:{node['port']}/pipelinetempdb")


# define a function to check the state of the main database
def check_main_db():
    # loop through the database URIs
    for db_uri in db_uris:
        # try to connect to the current node
        try:
            conn = psycopg2.connect(db_uri)
            # check if the current node is the primary node
            cur = conn.cursor()
            cur.execute("SELECT pg_is_in_recovery()")
            result = cur.fetchone()[0]
            cur.close()
            conn.close()
            # if the current node is not in recovery mode, store its URI and break the loop
            if not result:
                primary_uri = db_uri
                break
        # if connection to the current node fails, catch the exception
        except psycopg2.Error as e:
            print(e)

    # return the primary node URI or None if none was found
    return primary_uri
