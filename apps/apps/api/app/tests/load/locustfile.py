"""Locust load test — 500 VU / 10 min, SLA: P99 < 300 ms."""

import random

from locust import HttpUser, between, task

TOKEN = ""  # set via env or login task


class PlatformUser(HttpUser):
    wait_time = between(0.5, 2)
    token: str = ""
    project_id: str = ""
    org_id: str = ""

    def on_start(self):
        res = self.client.post(
            "/api/v1/auth/login",
            json={"email": "loadtest@example.com", "password": "LoadTest1234!"},
        )
        if res.status_code == 200:
            self.token = res.json()["data"]["access_token"]
        self.client.headers.update({"Authorization": f"Bearer {self.token}"})

    @task(3)
    def list_projects(self):
        self.client.get(
            f"/api/v1/organizations/{self.org_id}/projects", name="/organizations/:id/projects"
        )

    @task(5)
    def get_board(self):
        if self.project_id:
            self.client.get(
                f"/api/v1/projects/{self.project_id}/tasks/board", name="/projects/:id/tasks/board"
            )

    @task(2)
    def list_notifications(self):
        self.client.get("/api/v1/notifications")

    @task(2)
    def search(self):
        self.client.get(f"/api/v1/search?q=task&org_id={self.org_id}", name="/search")

    @task(1)
    def create_task(self):
        if self.project_id:
            self.client.post(
                f"/api/v1/projects/{self.project_id}/tasks",
                json={
                    "title": f"Load test task {random.randint(1, 9999)}",
                    "priority": "medium",
                    "status": "todo",
                },
                name="/projects/:id/tasks [POST]",
            )

    @task(1)
    def health_check(self):
        self.client.get("/health")
