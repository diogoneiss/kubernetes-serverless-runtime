# Custom serverless runtime using K8s

A runtime for arbitrary serverless functions capable of processing resource consumption info.

Requires a Redis server running and a key continously updated. 

## Serverless function
Function capable of taking an input dict and persistent context and outputting processed metrics, which will be persisted on the desired Redis key. 
There is a mock runtime module for reading redis and calling the function, exclusive for debugging.

## Dashboard

Written in plotly, periodically polls the desired redis key for updates.

## Runtime
Requires two configmaps
* outputkey, which defines the redis output key
* pyfile, which contains the function that will be executed by the runtime

K8s deployment takes the configmaps, mounts a file volume for the serverless function and sets outputkey as an env variable. 

The runtime itself calls the mounted function with data read from redis, stores the result back and sleeps for some seconds.

