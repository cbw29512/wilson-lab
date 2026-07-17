from datetime import datetime, timezone
from typing import Protocol

import docker
from docker.errors import APIError, NotFound

from .config import Settings
from .models import ActionName
from .schemas import Resource, ResourceStatus


class RuntimeError(Exception):
    pass


class RuntimeClient(Protocol):
    def list_resources(self) -> list[Resource]: ...
    def get_resource(self, resource_id: str) -> Resource: ...
    def apply(self, resource_id: str, action: ActionName) -> Resource: ...


def allowed_actions(status: ResourceStatus) -> list[ActionName]:
    if status == ResourceStatus.RUNNING:
        return [ActionName.STOP, ActionName.RESTART]
    if status == ResourceStatus.STOPPED:
        return [ActionName.START]
    return []


class MockRuntime:
    def __init__(self) -> None:
        now = datetime.now(timezone.utc)
        self._resources = {
            "demo-grafana": Resource(
                id="demo-grafana",
                name="Grafana",
                status=ResourceStatus.RUNNING,
                description="Sandbox dashboards for security and traffic telemetry.",
                tags=["observability", "dashboard", "managed"],
                image_name="grafana/grafana:latest",
                health_status="healthy",
                allowed_actions=allowed_actions(ResourceStatus.RUNNING),
                created_utc=now,
                updated_utc=now,
            ),
            "demo-juice-shop": Resource(
                id="demo-juice-shop",
                name="OWASP Juice Shop",
                status=ResourceStatus.STOPPED,
                description="Deliberately vulnerable training application in an isolated sandbox.",
                tags=["training", "owasp", "managed"],
                image_name="bkimminich/juice-shop:latest",
                allowed_actions=allowed_actions(ResourceStatus.STOPPED),
                created_utc=now,
                updated_utc=now,
            ),
        }

    def list_resources(self) -> list[Resource]:
        return list(self._resources.values())

    def get_resource(self, resource_id: str) -> Resource:
        resource = self._resources.get(resource_id)
        if not resource:
            raise RuntimeError("Managed resource not found")
        return resource

    def apply(self, resource_id: str, action: ActionName) -> Resource:
        resource = self.get_resource(resource_id)
        if action not in resource.allowed_actions:
            raise RuntimeError(f"Action '{action}' is not allowed for status '{resource.status}'")
        next_status = ResourceStatus.STOPPED if action == ActionName.STOP else ResourceStatus.RUNNING
        updated = resource.model_copy(
            update={
                "status": next_status,
                "allowed_actions": allowed_actions(next_status),
                "updated_utc": datetime.now(timezone.utc),
            }
        )
        self._resources[resource_id] = updated
        return updated


class DockerRuntime:
    def __init__(self, settings: Settings) -> None:
        self.client = docker.from_env()
        self.settings = settings
        self.label_key, _, self.label_value = settings.managed_label.partition("=")

    def list_resources(self) -> list[Resource]:
        try:
            containers = self.client.containers.list(
                all=True,
                filters={"label": self.settings.managed_label},
            )
            return [self._to_resource(container) for container in containers]
        except APIError as error:
            raise RuntimeError("Docker inventory is unavailable") from error

    def get_resource(self, resource_id: str) -> Resource:
        return self._to_resource(self._managed_container(resource_id))

    def apply(self, resource_id: str, action: ActionName) -> Resource:
        container = self._managed_container(resource_id)
        resource = self._to_resource(container)
        if action not in resource.allowed_actions:
            raise RuntimeError(f"Action '{action}' is not allowed for status '{resource.status}'")
        try:
            if action == ActionName.START:
                container.start()
            elif action == ActionName.STOP:
                container.stop(timeout=10)
            elif action == ActionName.RESTART:
                container.restart(timeout=10)
            container.reload()
            return self._to_resource(container)
        except APIError as error:
            raise RuntimeError(f"Docker action '{action}' failed") from error

    def _managed_container(self, resource_id: str):
        try:
            container = self.client.containers.get(resource_id)
        except (NotFound, APIError) as error:
            raise RuntimeError("Managed resource not found") from error
        if container.labels.get(self.label_key) != self.label_value:
            raise RuntimeError("Resource is outside the Wilson Lab allowlist")
        return container

    def _to_resource(self, container) -> Resource:
        container.reload()
        status = ResourceStatus.RUNNING if container.status == "running" else ResourceStatus.STOPPED
        state = container.attrs.get("State", {})
        health = state.get("Health", {}).get("Status")
        labels = container.labels or {}
        tags = [tag.strip() for tag in labels.get("wilson-lab.tags", "managed").split(",") if tag.strip()]
        created = datetime.fromisoformat(container.attrs["Created"].replace("Z", "+00:00"))
        return Resource(
            id=container.id,
            name=container.name,
            status=status,
            description=labels.get("wilson-lab.description", "Managed Wilson Lab container."),
            tags=tags,
            environment=labels.get("wilson-lab.environment", "sandbox"),
            host_name=labels.get("wilson-lab.host", "wilson-lab-cloud"),
            image_name=container.image.tags[0] if container.image.tags else container.image.short_id,
            health_status=health,
            allowed_actions=allowed_actions(status),
            created_utc=created,
            updated_utc=datetime.now(timezone.utc),
        )


def build_runtime(settings: Settings) -> RuntimeClient:
    if settings.runtime_mode == "docker":
        return DockerRuntime(settings)
    return MockRuntime()
