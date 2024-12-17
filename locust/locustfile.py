######
# This tool was used to simulate access to the website
# by hundreds of users and check the behavior of the
# server and database. Run the load testing tool with:
#
# locust -f locustfile.py --host=http://localhost:8010
#
######

import random

from locust import HttpUser, TaskSet, between, task

# The urs_list.txt file is just an example and therefore
# contains a small list of URS
with open("urs_list.txt", "r") as f:
    urs = [line.strip() for line in f.readlines()]


class UserBehavior(TaskSet):
    @task
    def fetch_sequence_page(self):
        random_urs = random.choice(urs)
        self.client.get(f"/rna/{random_urs}")


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 3)
