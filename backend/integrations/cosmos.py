"""Cosmos DB client for onboarding state persistence."""

import os
from typing import Optional
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError

from agents.state import OnboardingState


class OnboardingCosmosClient:
    """Client for persisting onboarding state to Cosmos DB."""
    
    def __init__(self):
        """Initialize Cosmos DB client."""
        # Get connection details from environment
        endpoint = os.environ.get("COSMOS_ENDPOINT")
        key = os.environ.get("COSMOS_KEY")
        database_name = os.environ.get("COSMOS_DATABASE", "hr-onboarding")
        container_name = os.environ.get("COSMOS_CONTAINER", "onboarding-states")
        
        if not endpoint or not key:
            raise ValueError("COSMOS_ENDPOINT and COSMOS_KEY must be set")
        
        # Initialize client
        self.client = CosmosClient(endpoint, key)
        self.database = self.client.get_database_client(database_name)
        self.container = self.database.get_container_client(container_name)
    
    def create_state(self, state: OnboardingState) -> dict:
        """Create new onboarding state in Cosmos DB."""
        document = {
            "id": state["new_hire_id"],
            "partitionKey": state["new_hire_id"],
            **state
        }
        
        created = self.container.create_item(body=document)
        return created
    
    def get_state(self, onboarding_id: str) -> Optional[OnboardingState]:
        """Retrieve onboarding state by ID."""
        try:
            item = self.container.read_item(
                item=onboarding_id,
                partition_key=onboarding_id
            )
            return item
        except CosmosResourceNotFoundError:
            return None
    
    def update_state(self, state: OnboardingState) -> dict:
        """Update existing onboarding state."""
        document = {
            "id": state["new_hire_id"],
            "partitionKey": state["new_hire_id"],
            **state
        }
        
        updated = self.container.upsert_item(body=document)
        return updated
    
    def delete_state(self, onboarding_id: str) -> None:
        """Delete onboarding state."""
        self.container.delete_item(
            item=onboarding_id,
            partition_key=onboarding_id
        )
    
    def list_states(self, limit: int = 100) -> list[OnboardingState]:
        """List all onboarding states."""
        query = "SELECT * FROM c ORDER BY c.created_at DESC OFFSET 0 LIMIT @limit"
        parameters = [{"name": "@limit", "value": limit}]
        
        items = list(self.container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))
        
        return items


# Singleton instance
_cosmos_client: Optional[OnboardingCosmosClient] = None


def get_cosmos_client() -> OnboardingCosmosClient:
    """Get or create Cosmos DB client singleton."""
    global _cosmos_client
    if _cosmos_client is None:
        _cosmos_client = OnboardingCosmosClient()
    return _cosmos_client