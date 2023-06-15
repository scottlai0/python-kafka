## Start up docker-composer
```
> docker-composer up -d
```
## Show state of composer
```
> docker-compose ps
```
## Turn off docker environment
```
> docker-composer down -v
```

<hr>

# Admin Api:
## Topic Management via CLI within dockerized environment
```
> docker-compose ps
```
There should be a cli-tools container

List Topics inside the Kafka environment
```
> docker exec -it cli-tools kafka-topics --boostrap-server --list broker0:29092,broker1:29093,broker2:29094
```

### Create Topic
Listing the partition and replication number will override the value specified inside the ```docker-composer.yml```
```
> docker exec -it cli-tools kafka-topics --boostrap-server --create broker0:29092 --topic people --partitions 3 --replication-factor 3
```

### Describe Topics
```
> docker exec -it cli-tools kafka-topics --boostrap-server --describe broker0:29092 --topic people
```

### Delete Topics 
```
> docker exec -it cli-tools kafka-topics --boostrap-server --delete broker0:29092 --topic people
```

### Create Topic with different retention
1 hour = 360000ms
```
> docker exec -it cli-tools kafka-topics --boostrap-server broker0:29092 --topic experiments --config rentention.ms=360000
```

### Describe configs
```
> docker exec -it cli-tools kafka-configs --boostrap-server broker0:29092 --describe -- all --topic experiments
```

### Change Retention of a Topic
Default retention periond is 2 weeks.
```
> docker exec -it cli-tools kafka-configs --boostrap-server broker0:29092 --alter --entity-type topics --entity-name experiments --add-config retention.ms=500000
```

### Create compacted Topic 
Topic name = experiments.latest (different name from experiments)
```
> docker exec -it cli-tools kafka-topics --boostrap-server broker0:29092 --create --topic experiments.latest -config cleanup.policy=compact
```

<hr>
# Producer & Consumer
## Start Producer
```
> docker exec -it cli-tools kafka-console-producer --bootstrap-server broker0:29092 --topic people
```
## Start Consumer
```
> docker exec -it cli-tools kafka-console-consumer --bootstrap-server broker0:29092 --topic people --from-beginning
```
Within Producer CLI, try typing the following:
```
> {"name":"Martin Fowler", "title":"Chief Scientist"}
```
```
> {"name":"Zhamak Dehghani", "title":"Direct Tech Innovation"}
```
The consumer CLI should reflect the changes accordingly.
