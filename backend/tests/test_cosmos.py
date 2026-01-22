"""Tests for Cosmos DB integration."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.integrations.cosmos import OnboardingCosmosClient, get_cosmos_client
from backend.agents.state import OnboardingState
from datetime import datetime


class TestOnboardingCosmosClient:
    """Tests for Cosmos DB client."""
    
    @patch.dict('os.environ', {
        'COSMOS_ENDPOINT': 'https://test.documents.azure.com:443/',
        'COSMOS_KEY': 'test-key',
        'COSMOS_DATABASE': 'test-db',
        'COSMOS_CONTAINER': 'test-container'
    })
    @patch('backend.integrations.cosmos.CosmosClient')
    def test_initialization(self, mock_cosmos_client):
        """Test client initialization with environment variables."""
        client = OnboardingCosmosClient()
        
        mock_cosmos_client.assert_called_once_with(
            'https://test.documents.azure.com:443/',
            'test-key'
        )
    
    @patch.dict('os.environ', {}, clear=True)
    @patch('backend.integrations.cosmos.CosmosClient')
    def test_raises_without_credentials(self, mock_cosmos_client):
        """Test that missing credentials raises ValueError."""
        with pytest.raises(ValueError, match="COSMOS_ENDPOINT and COSMOS_KEY must be set"):
            OnboardingCosmosClient()
    
    @patch.dict('os.environ', {
        'COSMOS_ENDPOINT': 'https://test.documents.azure.com:443/',
        'COSMOS_KEY': 'test-key'
    })
    @patch('backend.integrations.cosmos.CosmosClient')
    def test_create_state(self, mock_cosmos_client):
        """Test creating state in Cosmos DB."""
        # Setup mocks
        mock_container = MagicMock()
        mock_database = MagicMock()
        mock_database.get_container_client.return_value = mock_container
        mock_client_instance = MagicMock()
        mock_client_instance.get_database_client.return_value = mock_database
        mock_cosmos_client.return_value = mock_client_instance
        
        mock_container.create_item.return_value = {"id": "nh-001"}
        
        # Create client and state
        client = OnboardingCosmosClient()
        
        state: OnboardingState = {
            "new_hire_id": "nh-001",
            "new_hire_name": "Test User",
            "email": "test@example.com",
            "role": "Engineer",
            "department": "IT",
            "start_date": "2026-02-01",
            "manager_id": "mgr-001",
            "current_phase": "pre_onboarding",
            "tasks": [],
            "completed_tasks": [],
            "pending_tasks": [],
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "errors": [],
        }
        
        result = client.create_state(state)
        
        mock_container.create_item.assert_called_once()
        assert result is not None
        assert result.get("id") == "nh-001"
    
    @patch.dict('os.environ', {
        'COSMOS_ENDPOINT': 'https://test.documents.azure.com:443/',
        'COSMOS_KEY': 'test-key'
    })
    @patch('backend.integrations.cosmos.CosmosClient')
    def test_get_state(self, mock_cosmos_client):
        """Test retrieving state from Cosmos DB."""
        # Setup mocks
        mock_container = MagicMock()
        mock_database = MagicMock()
        mock_database.get_container_client.return_value = mock_container
        mock_client_instance = MagicMock()
        mock_client_instance.get_database_client.return_value = mock_database
        mock_cosmos_client.return_value = mock_client_instance
        
        mock_container.read_item.return_value = {
            "id": "nh-001",
            "new_hire_name": "Test User"
        }
        
        # Get state
        client = OnboardingCosmosClient()
        result = client.get_state("nh-001")
        
        mock_container.read_item.assert_called_once_with(
            item="nh-001",
            partition_key="nh-001"
        )
        assert result is not None
        assert result.get("id") == "nh-001"


class TestGetCosmosClient:
    """Tests for get_cosmos_client singleton."""
    
    @patch.dict('os.environ', {
        'COSMOS_ENDPOINT': 'https://test.documents.azure.com:443/',
        'COSMOS_KEY': 'test-key'
    })
    @patch('backend.integrations.cosmos.CosmosClient')
    def test_returns_singleton(self, mock_cosmos_client):
        """Test that get_cosmos_client returns the same instance."""
        # Reset singleton
        import backend.integrations.cosmos as cosmos_module
        cosmos_module._cosmos_client = None
        
        client1 = get_cosmos_client()
        client2 = get_cosmos_client()
        
        assert client1 is client2
