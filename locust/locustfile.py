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
    urs_taxid = [line.strip() for line in f.readlines()]


class UserBehavior(TaskSet):
    @task
    def fetch_sequence_page(self):
        random_urs = random.choice(urs_taxid)
        self.client.get(f"/rna/{random_urs}")

    @task
    def fetch_api_data(self):
        random_urs = random.choice(urs_taxid).split("_")
        urs = random_urs[0]
        taxid = random_urs[1]
        self.client.get(f"/api/v1/rna/{urs}/publications")
        self.client.get(f"/api/v1/rna/{urs}/xrefs/{taxid}")


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(0.5, 2)
