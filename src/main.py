import  argparse
import os
import json
import requests
from rich.console import Console
from rich.table import Table

PROG_DIR=os.path.join(os.path.expanduser("~"), ".local/share/ssv-man")
CLUSTER_LIST=os.path.join(PROG_DIR, "cluster-list.json")
URL="https://ssvscan.io/subgraph/graphql"
#URL="https://gateway.thegraph.com/api/[api-key]/subgraphs/id/9JdixzA6Ey391oiC4PwuDFyAiCxCw9xzR3gWYJSQW6yn"

def init():
    try:
        if os.path.isfile(CLUSTER_LIST):
            pass
        else:
            if not os.path.isdir(PROG_DIR):
                os.makedirs(PROG_DIR)
            write_json(CLUSTER_LIST, {"clusters":{}})
    except Exception as e:
        print("Error during init: ", e)
        exit()

def read_json(f):
    try:
        with open(f) as f:
            data = json.load(f)
            return data
    except Exception as e:
        print("Error while reading ~/.local/ssv-man/cluster-list.json", e)
        exit()

def write_json(f, data):
    try:
        with open(f, "w") as f:
            data = json.dump(data, f, indent=2)
    except Exception as e:
        print("Error while writing ~/.local/share/ssv-man/cluster-list.json", e)
        exit()

def get_networkFee():
    query = f'''
    {{
      networkFeeUpdateds(first: 1) {{
        newFee
        oldFee
      }}
    }}
    '''
    headers = { "Content-Type": "application/json" }
    data = {"query": query, "operationName": "Subgraphs", "variables": {"id": "1"}}
    response = post_request(data, headers)
    if response.status_code == 200:
       #print(response.json())
       return response.json()["data"]["networkFeeUpdateds"][0]["newFee"]
    else:
        print(f"Query failed with status code {response.status_code}")
        print(response.text)
        exit()


def get_cluster_info(cluster_id):
    query = f'''
    {{
      cluster( id: "{cluster_id}" ){{
        id
        operatorIds
        owner
        cluster_active
        cluster_balance
        cluster_validatorCount
      }}
    }}
    '''
    headers = { "Content-Type": "application/json" }
    data = {"query": query, "operationName": "Subgraphs", "variables": {"id": "1"}}
    response = post_request(data, headers)
    # Check the response
    if response.status_code == 200:
       #print(response.json())
       cluster_info = response.json()["data"]["cluster"]
       cluster_info["networkFee"] = get_networkFee()
       return cluster_info
    else:
        print(f"Query failed with status code {response.status_code}")
        print(response.text)
        exit()

def post_request(data, headers):
    response = requests.post(
        URL,
        json=data,
        headers=headers
    )
    return response

def get_status(validators):
    data = { "ids": validators }
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    url = "https://ethereum-beacon-api.publicnode.com/eth/v1/beacon/states/head/validators"
    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()
    return response_data["data"]

def get_validators(cluster_id):
    query=f'''
    {{
     validators (first: 1000, where: {{clusterId: "{cluster_id}"}}) {{
       publicKey
     }}
    }}
    '''
    headers = { "Content-Type": "application/json" }
    data = {"query": query, "operationName": "Subgraphs", "variables": {"id": "1"}}
    response = post_request(data, headers)
    # Check the response
    if response.status_code == 200:
        # return response.json()["data"]["validators"]
        validators = []
        for val in response.json()["data"]["validators"]:
           validators.append(val["publicKey"])
        return validators
    else:
        print(f"Query failed with status code {response.status_code}")
        print(response.text)
        exit()

def print_cluster(alias, cluster_info):
    table = Table(title=alias)
    table.add_column("Parameters", style="cyan")
    table.add_column("Values", style="magenta")
    table.add_row("Cluster ID", cluster_info["id"])
    table.add_row("Status", str(cluster_info["cluster_active"]))
    operators = ""
    for op in cluster_info["operatorIds"]:
        operators += ", " + op
    table.add_row("Operators", operators[2:])
    table.add_row("Owner", cluster_info["owner"])
    table.add_row("Network Fee Index", cluster_info["networkFee"])
    table.add_row("Cluster Balance", cluster_info["cluster_balance"])
    table.add_row("Validator Count", cluster_info["cluster_validatorCount"])
    console = Console()
    console.print(table)

def print_validators(alias, validators, active):
    table = Table(title=alias)
    table.add_column("Public Key", style="magenta")
    if active:
        status_color = "green"
    else:
        status_color = "red"
    table.add_column("Status", style=status_color)
    l = []
    for val in validators:
        #print(val["publicKey"])
        table.add_row(val["publicKey"], val["status"])
        l.append(val["publicKey"])
    #print(l)
    console = Console()
    console.print(table)

def add_cluster(args):
    cluster_data = read_json(f"{CLUSTER_LIST}")
    # check if cluster exists
    cluster_info = get_cluster_info(args.id)
    if cluster_info == None:
        print("Cluster Doesn't exit")
        exit()
    cluster_data["clusters"][args.alias] = cluster_info
    write_json(CLUSTER_LIST, cluster_data)
    print_cluster(args.alias, cluster_info)

def show_cluster(args):
    cluster_data = read_json(f"{CLUSTER_LIST}")
    cluster_info = cluster_data["clusters"][args.alias]
    if cluster_info == None:
        print("Cluster Doesn't exit")
        exit()
    cluster_data["clusters"][args.alias] = cluster_info
    write_json(CLUSTER_LIST, cluster_data)
    print_cluster(args.alias, cluster_info)

def show_validators(args):
    cluster_data = read_json(CLUSTER_LIST)
    cluster_id = cluster_data["clusters"][args.alias]["id"]
    validators = get_validators(cluster_id)
    validator_status = get_status(validators)
    active_validators = []
    inactive_validators = []
    print("No of validators in this CLUSTER: ",len(validator_status))
    for validator in validator_status:
        print(validator["validator"]["pubkey"])
        if validator["status"] == "active_ongoing":
            active_validators.append({"publicKey": validator["validator"]["pubkey"], "status": "active"})
        else:
            inactive_validators.append({"publicKey": validator["validator"]["pubkey"], "status": "inactive"})
    if not args.inactive:
        print_validators(args.alias, inactive_validators, args.inactive)
    else:
        print_validators(args.alias, active_validators, args.inactive)



    # print_validators(args.alias, validators, args.inactive)

def parse_args():
    # parse args
    parser = argparse.ArgumentParser(prog="ssv-man")
    subparsers = parser.add_subparsers()
    add_cluster_parser = subparsers.add_parser("add-cluster", help="Add a new cluster")
    add_cluster_parser.add_argument("--id", type=str, required=True, help="Enter cluster id to add")
    add_cluster_parser.add_argument("--alias", type=str, required=True, help="Enter an alias to refer this cluster")
    add_cluster_parser.set_defaults(func=add_cluster)
    # add cluster
        # cluster id
    # show
        # cluster info
        # active validators in cluster
        # inactive validators in cluster
        # show runway info
    show_parser = subparsers.add_parser("show", help="Show details regarding saved clusters")
    show_subparser = show_parser.add_subparsers()
    show_cluster_parser=show_subparser.add_parser("cluster", help="Show saved clusters")
    show_cluster_parser.add_argument("--alias", type=str, required=True, help="Cluster alias to show info")
    show_val_parser = show_subparser.add_parser("validators", help="Enter the cluster id to show active validators for")
    show_val_parser.add_argument("--alias", type=str, required=True, help="Cluster alias to show validators for")
    show_val_parser.add_argument("--inactive", action="store_false", help="To show inactive validators")
    show_runway_parser = show_subparser.add_parser("runway", help="Enter the cluster id to show runway")

    show_cluster_parser.set_defaults(func=show_cluster)
    show_val_parser.set_defaults(func=show_validators)


    # add cluster
    # validator
        # info
    validator_parser = subparsers.add_parser("validator", help="Show validator info")
    validator_parser.add_argument("--address", type=str, help="Enter address of validator")
    return parser.parse_args()

def main():
    init()
    args = parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
