#!/usr/bin/env python3
"""
Integration tests for Phase 5.3: Backend Agent.
Tests API development, database design, security implementation, and 
architecture design capabilities.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agents.specialized.backend_agent import (
    BackendAgent, APISpecification, DatabaseSchema,
    SecurityConfiguration, ArchitectureDesign
)


class TestBackendAgent:
    """Test suite for Backend Agent."""
    
    @pytest.fixture
    async def backend_agent(self):
        """Create a Backend Agent instance for testing."""
        agent = BackendAgent(agent_id="test_backend_001", name="Test Backend Agent")
        await agent.initialize()
        return agent
    
    @pytest.fixture
    def sample_api_endpoints(self):
        """Sample API endpoints for testing."""
        return [
            {
                "path": "/users",
                "method": "GET",
                "description": "Get all users"
            },
            {
                "path": "/users/{id}",
                "method": "GET",
                "description": "Get user by ID"
            },
            {
                "path": "/users",
                "method": "POST",
                "description": "Create new user"
            }
        ]
    
    @pytest.fixture
    def sample_data_models(self):
        """Sample data models for testing."""
        return [
            {
                "name": "User",
                "fields": [
                    {"name": "id", "type": "int", "required": True},
                    {"name": "username", "type": "str", "required": True},
                    {"name": "email", "type": "str", "required": True},
                    {"name": "created_at", "type": "datetime", "required": False}
                ]
            }
        ]
    
    @pytest.fixture
    def sample_database_entities(self):
        """Sample database entities for testing."""
        return [
            {
                "name": "users",
                "type": "table",
                "fields": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "username", "type": "VARCHAR(255)", "unique": True},
                    {"name": "email", "type": "VARCHAR(255)", "unique": True},
                    {"name": "created_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"}
                ]
            }
        ]
    
    @pytest.fixture
    def sample_security_config(self):
        """Sample security configuration for testing."""
        return {
            "algorithm": "HS256",
            "expiration": 3600,
            "refresh_token": True,
            "secret_key": "your-secret-key-here"
        }
    
    @pytest.fixture
    def sample_architecture_components(self):
        """Sample architecture components for testing."""
        return [
            {
                "name": "API Gateway",
                "type": "service",
                "description": "Entry point for all API requests",
                "technology": "nginx"
            },
            {
                "name": "User Service",
                "type": "microservice",
                "description": "Handles user management",
                "technology": "python/fastapi"
            },
            {
                "name": "Database",
                "type": "storage",
                "description": "PostgreSQL database",
                "technology": "postgresql"
            }
        ]
    
    def test_backend_agent_initialization(self, backend_agent):
        """Test Backend Agent initialization."""
        assert backend_agent.agent_id == "test_backend_001"
        assert backend_agent.name == "Test Backend Agent"
        assert backend_agent.agent_type.value == "backend"
        assert len(backend_agent.capabilities) == 5
        
        # Check capabilities
        capability_names = [cap.name for cap in backend_agent.capabilities]
        expected_capabilities = [
            "api_development", "database_design", "security_implementation",
            "architecture_design", "code_generation"
        ]
        for expected in expected_capabilities:
            assert expected in capability_names
    
    def test_supported_technologies(self, backend_agent):
        """Test supported technologies."""
        # Test supported languages
        languages = backend_agent.get_supported_languages()
        expected_languages = ["python", "nodejs", "java", "go", "rust"]
        assert languages == expected_languages
        
        # Test supported frameworks
        python_frameworks = backend_agent.get_supported_frameworks("python")
        expected_python_frameworks = ["fastapi", "django", "flask", "aiohttp"]
        assert python_frameworks == expected_python_frameworks
        
        # Test supported databases
        sql_databases = backend_agent.get_supported_databases("sql")
        expected_sql_databases = ["postgresql", "mysql", "sqlite", "sqlserver"]
        assert sql_databases == expected_sql_databases
    
    def test_template_system_initialization(self, backend_agent):
        """Test template system initialization."""
        # Check that default templates are created
        assert "rest" in backend_agent.api_templates
        assert "basic" in backend_agent.api_templates["rest"]
        assert "sql" in backend_agent.database_templates
        assert "basic" in backend_agent.database_templates["sql"]
        assert "authentication" in backend_agent.security_templates
        assert "jwt" in backend_agent.security_templates["authentication"]
        assert "docker" in backend_agent.deployment_templates
        assert "basic" in backend_agent.deployment_templates["docker"]
    
    @pytest.mark.asyncio
    async def test_design_api(self, backend_agent, sample_api_endpoints, sample_data_models):
        """Test API design functionality."""
        # Design a REST API
        result = await backend_agent.design_api(
            api_type="rest",
            name="User Management API",
            description="API for managing users",
            endpoints=sample_api_endpoints,
            data_models=sample_data_models,
            authentication={"type": "jwt", "enabled": True}
        )
        
        assert result["success"] is True
        assert "api_specification" in result
        assert result["message"] == "API specification 'User Management API' created successfully"
        
        # Check API specification
        api_spec = result["api_specification"]
        assert api_spec["api_type"] == "rest"
        assert api_spec["name"] == "User Management API"
        assert api_spec["description"] == "API for managing users"
        assert len(api_spec["endpoints"]) == 3
        assert len(api_spec["data_models"]) == 1
        assert api_spec["authentication"]["type"] == "jwt"
        
        # Verify it's stored
        assert len(backend_agent.api_specifications) == 1
        stored_spec = list(backend_agent.api_specifications.values())[0]
        assert stored_spec.name == "User Management API"
    
    @pytest.mark.asyncio
    async def test_create_database_schema(self, backend_agent, sample_database_entities):
        """Test database schema creation."""
        # Create a database schema
        result = await backend_agent.create_database_schema(
            database_type="postgresql",
            name="User Management Database",
            description="Database for user management system",
            entities=sample_database_entities,
            relationships=[
                {"from": "users", "to": "profiles", "type": "one_to_one"}
            ],
            constraints=[
                {"name": "unique_username", "type": "unique", "fields": ["username"]}
            ],
            indexes=[
                {"name": "idx_users_email", "type": "btree", "fields": ["email"]}
            ]
        )
        
        assert result["success"] is True
        assert "database_schema" in result
        assert result["message"] == "Database schema 'User Management Database' created successfully"
        
        # Check database schema
        db_schema = result["database_schema"]
        assert db_schema["database_type"] == "postgresql"
        assert db_schema["name"] == "User Management Database"
        assert db_schema["description"] == "Database for user management system"
        assert len(db_schema["entities"]) == 1
        assert len(db_schema["relationships"]) == 1
        assert len(db_schema["constraints"]) == 1
        assert len(db_schema["indexes"]) == 1
        
        # Verify it's stored
        assert len(backend_agent.database_schemas) == 1
        stored_schema = list(backend_agent.database_schemas.values())[0]
        assert stored_schema.name == "User Management Database"
    
    @pytest.mark.asyncio
    async def test_implement_security(self, backend_agent, sample_security_config):
        """Test security implementation."""
        # Implement JWT authentication
        result = await backend_agent.implement_security(
            security_type="authentication",
            name="JWT Authentication",
            description="JWT-based authentication system",
            method="jwt",
            configuration=sample_security_config
        )
        
        assert result["success"] is True
        assert "security_configuration" in result
        assert result["message"] == "Security configuration 'JWT Authentication' created successfully"
        
        # Check security configuration
        security_config = result["security_configuration"]
        assert security_config["security_type"] == "authentication"
        assert security_config["name"] == "JWT Authentication"
        assert security_config["description"] == "JWT-based authentication system"
        assert security_config["method"] == "jwt"
        assert security_config["enabled"] is True
        assert security_config["configuration"]["algorithm"] == "HS256"
        
        # Verify it's stored
        assert len(backend_agent.security_configurations) == 1
        stored_config = list(backend_agent.security_configurations.values())[0]
        assert stored_config.name == "JWT Authentication"
    
    @pytest.mark.asyncio
    async def test_design_architecture(self, backend_agent, sample_architecture_components):
        """Test architecture design."""
        # Design a microservices architecture
        result = await backend_agent.design_architecture(
            architecture_type="microservices",
            name="User Management System",
            description="Microservices-based user management system",
            components=sample_architecture_components,
            deployment="kubernetes",
            scaling={"auto_scaling": True, "min_replicas": 2, "max_replicas": 10}
        )
        
        assert result["success"] is True
        assert "architecture_design" in result
        assert result["message"] == "Architecture design 'User Management System' created successfully"
        
        # Check architecture design
        arch_design = result["architecture_design"]
        assert arch_design["architecture_type"] == "microservices"
        assert arch_design["name"] == "User Management System"
        assert arch_design["description"] == "Microservices-based user management system"
        assert len(arch_design["components"]) == 3
        assert arch_design["deployment"] == "kubernetes"
        assert arch_design["scaling"]["auto_scaling"] is True
        
        # Verify it's stored
        assert len(backend_agent.architecture_designs) == 1
        stored_design = list(backend_agent.architecture_designs.values())[0]
        assert stored_design.name == "User Management System"
    
    @pytest.mark.asyncio
    async def test_generate_api_code(self, backend_agent, sample_api_endpoints, sample_data_models):
        """Test API code generation."""
        # First design an API
        api_result = await backend_agent.design_api(
            api_type="rest",
            name="Test API",
            description="Test API for code generation",
            endpoints=sample_api_endpoints,
            data_models=sample_data_models
        )
        
        assert api_result["success"] is True
        api_spec_id = api_result["api_specification"]["api_id"]
        
        # Generate Python FastAPI code
        code_result = await backend_agent.generate_api_code(
            language="python",
            framework="fastapi",
            specification_id=api_spec_id
        )
        
        assert code_result["success"] is True
        assert "code" in code_result
        assert code_result["language"] == "python"
        assert code_result["framework"] == "fastapi"
        
        # Check generated code
        code = code_result["code"]
        assert "main.py" in code
        assert "requirements.txt" in code
        assert "README.md" in code
        
        # Check main.py content
        main_code = code["main.py"]
        assert "from fastapi import FastAPI" in main_code
        assert "app = FastAPI" in main_code
        assert "Test API" in main_code
        
        # Check requirements.txt
        requirements = code["requirements.txt"]
        assert "fastapi" in requirements
        assert "uvicorn" in requirements
        assert "pydantic" in requirements
    
    @pytest.mark.asyncio
    async def test_generate_express_code(self, backend_agent, sample_api_endpoints, sample_data_models):
        """Test Express.js code generation."""
        # First design an API
        api_result = await backend_agent.design_api(
            api_type="rest",
            name="Test Express API",
            description="Test API for Express.js code generation",
            endpoints=sample_api_endpoints,
            data_models=sample_data_models
        )
        
        assert api_result["success"] is True
        api_spec_id = api_result["api_specification"]["api_id"]
        
        # Generate Node.js Express code
        code_result = await backend_agent.generate_api_code(
            language="nodejs",
            framework="express",
            specification_id=api_spec_id
        )
        
        assert code_result["success"] is True
        assert "code" in code_result
        assert code_result["language"] == "nodejs"
        assert code_result["framework"] == "express"
        
        # Check generated code
        code = code_result["code"]
        assert "app.js" in code
        assert "package.json" in code
        assert "README.md" in code
        
        # Check app.js content
        app_code = code["app.js"]
        assert "const express = require('express')" in app_code
        assert "app.listen" in app_code
        assert "Test Express API" in app_code
        
        # Check package.json
        package_json = code["package.json"]
        assert "express" in package_json
        assert "cors" in package_json
        assert "helmet" in package_json
    
    def test_get_stored_data(self, backend_agent):
        """Test retrieving stored data."""
        # Check that we can get stored data
        api_specs = backend_agent.get_api_specifications()
        db_schemas = backend_agent.get_database_schemas()
        security_configs = backend_agent.get_security_configurations()
        arch_designs = backend_agent.get_architecture_designs()
        
        # These should be lists (even if empty)
        assert isinstance(api_specs, list)
        assert isinstance(db_schemas, list)
        assert isinstance(security_configs, list)
        assert isinstance(arch_designs, list)
    
    @pytest.mark.asyncio
    async def test_error_handling(self, backend_agent):
        """Test error handling."""
        # Test with invalid API type
        result = await backend_agent.design_api(
            api_type="invalid_type",
            name="Test API",
            description="Test API"
        )
        
        # Should still succeed but with default values
        assert result["success"] is True
        assert result["api_specification"]["api_type"] == "invalid_type"
        
        # Test code generation with non-existent specification
        code_result = await backend_agent.generate_api_code(
            language="python",
            framework="fastapi",
            specification_id="non_existent_id"
        )
        
        assert code_result["success"] is False
        assert "error" in code_result
        assert "not found" in code_result["error"]
    
    @pytest.mark.asyncio
    async def test_task_execution(self, backend_agent):
        """Test task execution through the task system."""
        # Create a mock task
        mock_task = MagicMock()
        mock_task.id = "test_task_001"
        mock_task.type = "design_api"
        mock_task.metadata = {
            "api_type": "rest",
            "name": "Task Test API",
            "description": "API created through task system"
        }
        
        # Execute the task
        result = await backend_agent._execute_task_impl(mock_task)
        
        assert result["success"] is True
        assert "api_specification" in result
        assert result["api_specification"]["name"] == "Task Test API"
        
        # Test unknown task type
        mock_task.type = "unknown_task_type"
        result = await backend_agent._execute_task_impl(mock_task)
        
        assert result["success"] is False
        assert "error" in result
        assert "Unknown task type" in result["error"]


class TestBackendAgentDataStructures:
    """Test the data structures used by Backend Agent."""
    
    def test_api_specification(self):
        """Test APISpecification dataclass."""
        from datetime import datetime
        
        api_spec = APISpecification(
            api_id="test_001",
            api_type="rest",
            name="Test API",
            description="Test API description",
            version="1.0.0",
            base_url="/api/v1",
            endpoints=[],
            data_models=[],
            authentication={},
            rate_limiting={},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert api_spec.api_id == "test_001"
        assert api_spec.api_type == "rest"
        assert api_spec.name == "Test API"
        assert api_spec.version == "1.0.0"
    
    def test_database_schema(self):
        """Test DatabaseSchema dataclass."""
        from datetime import datetime
        
        db_schema = DatabaseSchema(
            schema_id="test_001",
            database_type="postgresql",
            name="Test Database",
            description="Test database description",
            entities=[],
            relationships=[],
            constraints=[],
            indexes=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert db_schema.schema_id == "test_001"
        assert db_schema.database_type == "postgresql"
        assert db_schema.name == "Test Database"
    
    def test_security_configuration(self):
        """Test SecurityConfiguration dataclass."""
        from datetime import datetime
        
        security_config = SecurityConfiguration(
            security_id="test_001",
            security_type="authentication",
            name="Test Security",
            description="Test security description",
            method="jwt",
            configuration={},
            enabled=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert security_config.security_id == "test_001"
        assert security_config.security_type == "authentication"
        assert security_config.method == "jwt"
        assert security_config.enabled is True
    
    def test_architecture_design(self):
        """Test ArchitectureDesign dataclass."""
        from datetime import datetime
        
        arch_design = ArchitectureDesign(
            architecture_id="test_001",
            architecture_type="microservices",
            name="Test Architecture",
            description="Test architecture description",
            components=[],
            deployment="kubernetes",
            scaling={},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert arch_design.architecture_id == "test_001"
        assert arch_design.architecture_type == "microservices"
        assert arch_design.deployment == "kubernetes"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
