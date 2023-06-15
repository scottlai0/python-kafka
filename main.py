import os
import uuid
import logging

from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI

from kafka import KafkaAdminClient, KafkaProducer, KafkaConsumer
from kafka.admin import NewTopic, ConfigResource, ConfigResourceType
from kafka.errors import TopicAlreadyExistsError

# Used to create sample data
from faker import Faker

from commands import CreatePeopleCommand
from entities import Person

logger = logging.getLogger()
load_dotenv(verbose=True)

app = FastAPI()

# Using Kafka's Admin API using Python and FastAPI to manipulate topics
@app.on_event('startup')
async def startup_event():
    client = KafkaAdminClient(bootstrap_servers = os.environ['BOOTSTRAP_SERVERS'])

    topics = [
        NewTopic(
            name = os.environ['TOPICS_PEOPLE_BASIC_NAME'],
            num_partitions = int(os.environ['TOPICS_PEOPLE_BASIC_PARTITIONS']),
            replication_factor = int(os.environ['TOPICS_PEOPLE_BASIC_REPLICAS'])
        ),
        NewTopic(
            name = f"{os.environ['TOPICS_PEOPLE_BASIC_NAME']}-short",       # Create topic with same parameters, but with different name and shorter retention
            num_partitions = int(os.environ['TOPICS_PEOPLE_BASIC_PARTITIONS']),
            replication_factor = int(os.environ['TOPICS_PEOPLE_BASIC_REPLICAS']),
            topic_configs = {
                'retention.ms': '360000'
            }
        ),
    ]

    # Create new topic
    for topic in topics:
        try:
            client.create_topics([topics])

        except TopicAlreadyExistsError as e:
            logger.warning("Topic already exists")

    # To edit configs of existing topic
    cfg_resource_update = ConfigResource(
        ConfigResource.TOPIC,
        os.environ['TOPICS_PEOPLE_BASIC_NAME'],
        configs = {'retention.ms': '360000'}
    )
    client.alter_configs([cfg_resource_update])


    client.close()

# Producer
def make_producer():
    return KafkaProducer(bootstrap_servers = os.environ['BOOTSTRAP_SERVERS'])

@app.post('/api/people', status_code=201, response_moedl=List[Person])
async def create_people(cmd: CreatePeopleCommand):
    people: List[Person] = []

    faker = Faker()
    producer = make_producer()

    for _ in range(cmd.count):
        person = Person(id = int(uuid.uuid4()), name = faker.name(), title = faker.job().title())
        people.append(person)
        
        # Kafka keys and values are encoded to bytes (utf-8)
        producer.send(
            topic = os.environ['TOPICS_PEOPLE_BASIC_NAME'],
            key = people.title.lower().replace(r's+','-').encode('utf-8'),
            value = person.json().encode('utf-8')
        )

    # This blocks and waits for all data to be written into Kafka (including any retries in the background if a write attempt fails)
    producer.flush()

    return people


@app.get('/hello-world')
async def hello_world():
    return {"message": "Hello World"}