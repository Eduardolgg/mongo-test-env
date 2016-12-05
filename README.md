# mongo-test-env
Create MongoDB shards on the local machine for development and / or testing purposes.

## Usage
> $ mongo-test-env.py options

## Examples

### The easy way

> $ ./mongo-test-env.py --replicaSetNumber 6 

Or if you just want the commands to execute

> $ ./mongo-test-env.py --replicaSetNumber 6 --debug

### The hard way

Get commands
> $ ./mongo-test-env.py --configServers 3 --dbRootPath ./data --logPath ./logs --logFilesPrefix "log_" --replSet "rpl_" --replicaSetNumber 6 --replicaSetSize 2 --arviters 1 --routers 2 --rs-options "--oplogSize 5" --debug

Start servers
> $ ./mongo-test-env.py --configServers 3 --dbRootPath ./data --logPath ./logs --logFilesPrefix "log_" --replSet "rpl_" --replicaSetNumber 6 --replicaSetSize 2 --arviters 1 --routers 2 --rs-options "--oplogSize 5"

