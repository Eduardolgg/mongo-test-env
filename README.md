# mongo-test-env
Create MongoDB shards on the local machine for development and / or testing purposes.

## Usage
> $ mongo-test-env.py options

## Examples

### The easy way

> $ ./mongo-test-env.py --tReplicaSetNumber 6 

Or if you just want the commands to execute

> $ ./mongo-test-env.py --tReplicaSetNumber 6 --debug

### The complex way

Get commands
> $ ./mongo-test-env.py --tConfigServers 3 --tDBRootPath ./data --tLogPath ./logs --tLogFilesPrefix "log_" --tReplSet "rpl_" --tReplicaSetNumber 6 --tReplicaSetSize 2 --tArviters 1 --tRouters 2 --oplogSize 5 --debug

Start servers
> $ ./mongo-test-env.py --tConfigServers 3 --tDBRootPath ./data --tLogPath ./logs --tLogFilesPrefix "log_" --tReplSet "rpl_" --tReplicaSetNumber 6 --tReplicaSetSize 2 --tArviters 1 --tRouters 2 --oplogSize 5


# TODO: Auto config servers... Coming soon :)

