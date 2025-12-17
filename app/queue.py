from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from enum import Enum
from typing import Protocol, TYPE_CHECKING

import boto3
from botocore.exceptions import BotoCoreError, ClientError

if TYPE_CHECKING:  # pragma: no cover
    from app.models import JobModel


class Operation(str, Enum):
    CREATE = "Create"
    UPDATE = "Update"
    REPLACE = "Replace"


class QueuePublisher(Protocol):
    def send_job_message(self, job: "JobModel", operation: Operation) -> None: ...


def _get_message_version() -> int:
    try:
        return int(os.getenv("QUEUE_MESSAGE_VERSION", "1"))
    except ValueError:
        return 1


def _get_api_endpoint() -> str | None:
    return os.getenv("QUEUE_API_ENDPOINT")


def build_queue_message(job: "JobModel", operation: Operation) -> dict:
    message = {
        "id": job.id,
        "externalId": job.external_id,
        "version": _get_message_version(),
        "operation": operation.value,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    api_endpoint = _get_api_endpoint()
    if api_endpoint:
        message["apiEndpoint"] = f"{api_endpoint.rstrip('/')}/jobs/{job.external_id}"
    return message


class NoOpQueuePublisher:
    def send_job_message(self, job: "JobModel", operation: Operation) -> None:
        return None


class SqsQueuePublisher:
    def __init__(
        self,
        *,
        queue_url: str | None,
        queue_name: str | None,
        endpoint_url: str | None,
        region_name: str | None,
    ):
        if not queue_url and not queue_name:
            raise ValueError("SQS_QUEUE_URL or SQS_QUEUE_NAME must be provided")
        self.queue_url = queue_url
        self.queue_name = queue_name
        self.client = boto3.client("sqs", endpoint_url=endpoint_url, region_name=region_name or "us-east-1")

    def _ensure_queue_url(self) -> str:
        if self.queue_url:
            return self.queue_url
        response = self.client.create_queue(QueueName=self.queue_name)
        self.queue_url = response["QueueUrl"]
        return self.queue_url

    def send_job_message(self, job: "JobModel", operation: Operation) -> None:
        queue_url = self._ensure_queue_url()
        message = build_queue_message(job, operation)
        try:
            self.client.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message))
        except (BotoCoreError, ClientError) as exc:
            raise RuntimeError(f"Failed to publish queue message: {exc}") from exc


_publisher: QueuePublisher | None = None


def get_queue_publisher() -> QueuePublisher:
    global _publisher
    if _publisher is None:
        queue_url = os.getenv("SQS_QUEUE_URL")
        queue_name = os.getenv("SQS_QUEUE_NAME")
        endpoint_url = os.getenv("SQS_ENDPOINT_URL")
        region_name = os.getenv("AWS_REGION")
        if queue_url or queue_name:
            _publisher = SqsQueuePublisher(
                queue_url=queue_url,
                queue_name=queue_name,
                endpoint_url=endpoint_url,
                region_name=region_name,
            )
        else:
            _publisher = NoOpQueuePublisher()
    return _publisher
