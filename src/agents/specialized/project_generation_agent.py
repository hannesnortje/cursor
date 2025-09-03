#!/usr/bin/env python3
"""
Project Generation Agent for multi-language project generation.
This agent can create project structures, build configurations, and development workflows
for Python, C++, Java, Go, Rust, TypeScript, and other programming languages.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from ..base.base_agent import BaseAgent, AgentType, AgentCapability

logger = logging.getLogger(__name__)


@dataclass
class ProjectTemplate:
    """Project template configuration."""
    template_id: str
    name: str
    description: str
    language: str
    framework: Optional[str] = None
    category: str = "general"  # web, api, library, cli, data-science, etc.
    tags: List[str] = field(default_factory=list)
    files: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    build_system: Optional[str] = None
    testing_framework: Optional[str] = None
    ci_cd_template: Optional[str] = None


@dataclass
class ProjectStructure:
    """Generated project structure."""
    project_id: str
    project_name: str
    language: str
    framework: Optional[str]
    base_path: str
    files_created: List[str] = field(default_factory=list)
    directories_created: List[str] = field(default_factory=list)
    build_files: List[str] = field(default_factory=list)
    test_files: List[str] = field(default_factory=list)
    config_files: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProjectGenerationAgent(BaseAgent):
    """Project Generation Agent for multi-language project creation."""
    
    def __init__(self, agent_id: str = None, name: str = "Project Generation Agent"):
        super().__init__(
            agent_id=agent_id or f"project_gen_{uuid.uuid4().hex[:8]}",
            name=name,
            agent_type=AgentType.SPECIALIZED,
            capabilities=[
                AgentCapability(
                    name="project_generation",
                    description="Generate project structures for multiple programming languages"
                ),
                AgentCapability(
                    name="build_system_setup",
                    description="Create build configurations and dependency management"
                ),
                AgentCapability(
                    name="development_workflow",
                    description="Set up testing, CI/CD, and code quality tools"
                ),
                AgentCapability(
                    name="template_management",
                    description="Manage and customize project templates"
                )
            ]
        )
        
        # Project generation specific attributes
        self.project_templates: Dict[str, ProjectTemplate] = {}
        self.generated_projects: Dict[str, ProjectStructure] = {}
        self.template_categories = {
            "python": ["web", "api", "data-science", "cli", "library"],
            "cpp": ["library", "application", "game", "embedded"],
            "java": ["web", "api", "android", "desktop", "library"],
            "go": ["web", "api", "cli", "library", "microservice"],
            "rust": ["web", "api", "cli", "library", "systems"],
            "typescript": ["web", "api", "cli", "library", "fullstack"],
            "javascript": ["web", "api", "cli", "library", "fullstack"]
        }
        
        # Initialize default templates
        self._initialize_default_templates()
        
        logger.info(f"Project Generation Agent {self.agent_id} initialized with capabilities: {[cap.name for cap in self.capabilities]}")
    
    def _initialize_default_templates(self):
        """Initialize default project templates for various languages."""
        # Python templates
        self._add_python_templates()
        
        # C++ templates
        self._add_cpp_templates()
        
        # Java templates
        self._add_java_templates()
        
        # Go templates
        self._add_go_templates()
        
        # Rust templates
        self._add_rust_templates()
        
        # TypeScript templates
        self._add_typescript_templates()
        
        logger.info(f"Initialized {len(self.project_templates)} project templates")
    
    def _add_python_templates(self):
        """Add Python project templates."""
        # Flask API template
        flask_template = ProjectTemplate(
            template_id="python_flask_api",
            name="Flask API",
            description="Python Flask REST API with testing and documentation",
            language="python",
            framework="flask",
            category="api",
            tags=["python", "flask", "api", "rest", "web"],
            dependencies=["flask", "flask-cors", "pytest", "black", "flake8"],
            build_system="pip",
            testing_framework="pytest",
            ci_cd_template="github_actions_python",
            files=[
                {"path": "requirements.txt", "type": "dependencies"},
                {"path": "app.py", "type": "main"},
                {"path": "tests/", "type": "directory"},
                {"path": "README.md", "type": "documentation"}
            ]
        )
        self.project_templates["python_flask_api"] = flask_template
        
        # Django web template
        django_template = ProjectTemplate(
            template_id="python_django_web",
            name="Django Web",
            description="Python Django web application with admin interface",
            language="python",
            framework="django",
            category="web",
            tags=["python", "django", "web", "admin", "database"],
            dependencies=["django", "djangorestframework", "pytest-django"],
            build_system="pip",
            testing_framework="pytest",
            ci_cd_template="github_actions_python",
            files=[
                {"path": "requirements.txt", "type": "dependencies"},
                {"path": "manage.py", "type": "main"},
                {"path": "tests/", "type": "directory"},
                {"path": "README.md", "type": "documentation"}
            ]
        )
        self.project_templates["python_django_web"] = django_template
        
        # Data Science template
        data_science_template = ProjectTemplate(
            template_id="python_data_science",
            name="Data Science",
            description="Python data science project with Jupyter notebooks",
            language="python",
            framework="jupyter",
            category="data-science",
            tags=["python", "jupyter", "data-science", "pandas", "numpy"],
            dependencies=["jupyter", "pandas", "numpy", "matplotlib", "seaborn"],
            build_system="pip",
            testing_framework="pytest",
            ci_cd_template="github_actions_python",
            files=[
                {"path": "requirements.txt", "type": "dependencies"},
                {"path": "notebooks/", "type": "directory"},
                {"path": "src/", "type": "directory"},
                {"path": "README.md", "type": "documentation"}
            ]
        )
        self.project_templates["python_data_science"] = data_science_template
    
    def _add_cpp_templates(self):
        """Add C++ project templates."""
        # CMake library template
        cmake_library_template = ProjectTemplate(
            template_id="cpp_cmake_library",
            name="CMake Library",
            description="C++ library project using CMake build system",
            language="cpp",
            framework="cmake",
            category="library",
            tags=["cpp", "cmake", "library", "modern-cpp"],
            dependencies=[],
            build_system="cmake",
            testing_framework="google_test",
            ci_cd_template="github_actions_cpp",
            files=[
                {"path": "CMakeLists.txt", "type": "build"},
                {"path": "src/", "type": "directory"},
                {"path": "include/", "type": "directory"},
                {"path": "tests/", "type": "directory"},
                {"path": "README.md", "type": "documentation"}
            ]
        )
        self.project_templates["cpp_cmake_library"] = cmake_library_template
        
        # Makefile application template
        makefile_app_template = ProjectTemplate(
            template_id="cpp_makefile_app",
            name="Makefile Application",
            description="C++ application using traditional Makefile",
            language="cpp",
            framework="make",
            category="application",
            tags=["cpp", "make", "application", "traditional"],
            dependencies=[],
            build_system="make",
            testing_framework="custom",
            ci_cd_template="github_actions_cpp",
            files=[
                {"path": "Makefile", "type": "build"},
                {"path": "src/", "type": "directory"},
                {"path": "tests/", "type": "directory"},
                {"path": "README.md", "type": "documentation"}
            ]
        )
        self.project_templates["cpp_makefile_app"] = makefile_app_template
    
    def _add_java_templates(self):
        """Add Java project templates."""
        # Spring Boot API template
        spring_api_template = ProjectTemplate(
            template_id="java_spring_api",
            name="Spring Boot API",
            description="Java Spring Boot REST API with Maven",
            language="java",
            framework="spring-boot",
            category="api",
            tags=["java", "spring", "api", "rest", "maven"],
            dependencies=["spring-boot-starter-web", "spring-boot-starter-test"],
            build_system="maven",
            testing_framework="junit",
            ci_cd_template="github_actions_java",
            files=[
                {"path": "pom.xml", "type": "build"},
                {"path": "src/main/java/", "type": "directory"},
                {"path": "src/test/java/", "type": "directory"},
                {"path": "README.md", "type": "documentation"}
            ]
        )
        self.project_templates["java_spring_api"] = spring_api_template
        
        # Gradle library template
        gradle_library_template = ProjectTemplate(
            template_id="java_gradle_library",
            name="Gradle Library",
            description="Java library project using Gradle build system",
            language="java",
            framework="gradle",
            category="library",
            tags=["java", "gradle", "library"],
            dependencies=[],
            build_system="gradle",
            testing_framework="junit",
            ci_cd_template="github_actions_java",
            files=[
                {"path": "build.gradle", "type": "build"},
                {"path": "src/main/java/", "type": "directory"},
                {"path": "src/test/java/", "type": "directory"},
                {"path": "README.md", "type": "documentation"}
            ]
        )
        self.project_templates["java_gradle_library"] = gradle_library_template
    
    def _add_go_templates(self):
        """Add Go project templates."""
        # Go web service template
        go_web_template = ProjectTemplate(
            template_id="go_web_service",
            name="Go Web Service",
            description="Go web service with modules and testing",
            language="go",
            framework="gin",
            category="web",
            tags=["go", "gin", "web", "api", "modules"],
            dependencies=["github.com/gin-gonic/gin", "github.com/stretchr/testify"],
            build_system="go_modules",
            testing_framework="testing",
            ci_cd_template="github_actions_go",
            files=[
                {"path": "go.mod", "type": "build"},
                {"path": "go.sum", "type": "build"},
                {"path": "main.go", "type": "main"},
                {"path": "cmd/", "type": "directory"},
                {"path": "internal/", "type": "directory"},
                {"path": "README.md", "type": "documentation"}
            ]
        )
        self.project_templates["go_web_service"] = go_web_template
        
        # Go CLI tool template
        go_cli_template = ProjectTemplate(
            template_id="go_cli_tool",
            name="Go CLI Tool",
            description="Go command-line interface tool",
            language="go",
            framework="cobra",
            category="cli",
            tags=["go", "cobra", "cli", "command-line"],
            dependencies=["github.com/spf13/cobra", "github.com/stretchr/testify"],
            build_system="go_modules",
            testing_framework="testing",
            ci_cd_template="github_actions_go",
            files=[
                {"path": "go.mod", "type": "build"},
                {"path": "main.go", "type": "main"},
                {"path": "cmd/", "type": "directory"},
                {"path": "internal/", "type": "directory"},
                {"path": "README.md", "type": "documentation"}
            ]
        )
        self.project_templates["go_cli_tool"] = go_cli_template
    
    def _add_rust_templates(self):
        """Add Rust project templates."""
        # Rust library template
        rust_library_template = ProjectTemplate(
            template_id="rust_library",
            name="Rust Library",
            description="Rust library crate with Cargo",
            language="rust",
            framework="cargo",
            category="library",
            tags=["rust", "cargo", "library", "systems"],
            dependencies=[],
            build_system="cargo",
            testing_framework="builtin",
            ci_cd_template="github_actions_rust",
            files=[
                {"path": "Cargo.toml", "type": "build"},
                {"path": "src/lib.rs", "type": "main"},
                {"path": "tests/", "type": "directory"},
                {"path": "README.md", "type": "documentation"}
            ]
        )
        self.project_templates["rust_library"] = rust_library_template
        
        # Rust web service template
        rust_web_template = ProjectTemplate(
            template_id="rust_web_service",
            name="Rust Web Service",
            description="Rust web service using Actix-web",
            language="rust",
            framework="actix-web",
            category="web",
            tags=["rust", "actix-web", "web", "api", "async"],
            dependencies=["actix-web", "tokio", "serde"],
            build_system="cargo",
            testing_framework="builtin",
            ci_cd_template="github_actions_rust",
            files=[
                {"path": "Cargo.toml", "type": "build"},
                {"path": "src/main.rs", "type": "main"},
                {"path": "tests/", "type": "directory"},
                {"path": "README.md", "type": "documentation"}
            ]
        )
        self.project_templates["rust_web_service"] = rust_web_template
    
    def _add_typescript_templates(self):
        """Add TypeScript project templates."""
        # Node.js API template
        node_api_template = ProjectTemplate(
            template_id="typescript_node_api",
            name="Node.js TypeScript API",
            description="TypeScript Node.js REST API with Express",
            language="typescript",
            framework="express",
            category="api",
            tags=["typescript", "node", "express", "api", "rest"],
            dependencies=["express", "typescript", "ts-node", "jest", "@types/express"],
            build_system="npm",
            testing_framework="jest",
            ci_cd_template="github_actions_typescript",
            files=[
                {"path": "package.json", "type": "build"},
                {"path": "tsconfig.json", "type": "config"},
                {"path": "src/", "type": "directory"},
                {"path": "tests/", "type": "directory"},
                {"path": "README.md", "type": "documentation"}
            ]
        )
        self.project_templates["typescript_node_api"] = node_api_template
        
        # React TypeScript template
        react_ts_template = ProjectTemplate(
            template_id="typescript_react_app",
            name="React TypeScript App",
            description="React application with TypeScript",
            language="typescript",
            framework="react",
            category="web",
            tags=["typescript", "react", "web", "frontend"],
            dependencies=["react", "typescript", "@types/react", "jest"],
            build_system="npm",
            testing_framework="jest",
            ci_cd_template="github_actions_typescript",
            files=[
                {"path": "package.json", "type": "build"},
                {"path": "tsconfig.json", "type": "config"},
                {"path": "src/", "type": "directory"},
                {"path": "public/", "type": "directory"},
                {"path": "README.md", "type": "documentation"}
            ]
        )
        self.project_templates["typescript_react_app"] = react_ts_template
    
    async def _execute_task_impl(self, task) -> Dict[str, Any]:
        """Execute task implementation - required by BaseAgent."""
        try:
            logger.info(f"Executing task {task.id} in Project Generation Agent")
            
            # Handle different task types
            if task.type == "generate_project":
                return await self._handle_generate_project_task(task)
            elif task.type == "list_templates":
                return await self._handle_list_templates_task(task)
            elif task.type == "customize_template":
                return await self._handle_customize_template_task(task)
            else:
                return {
                    "success": False,
                    "error": f"Unknown task type: {task.type}"
                }
                
        except Exception as e:
            logger.error(f"Error executing task {task.id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_generate_project_task(self, task) -> Dict[str, Any]:
        """Handle project generation task."""
        template_id = task.metadata.get("template_id")
        project_name = task.metadata.get("project_name")
        target_path = task.metadata.get("target_path", ".")
        customizations = task.metadata.get("customizations", {})
        
        return self.generate_project(template_id, project_name, target_path, customizations)
    
    async def _handle_list_templates_task(self, task) -> Dict[str, Any]:
        """Handle list templates task."""
        language_filter = task.metadata.get("language")
        category_filter = task.metadata.get("category")
        
        return self.list_project_templates(language_filter, category_filter)
    
    async def _handle_customize_template_task(self, task) -> Dict[str, Any]:
        """Handle template customization task."""
        template_id = task.metadata.get("template_id")
        customizations = task.metadata.get("customizations", {})
        
        return self.customize_project_template(template_id, customizations)
    
    def list_project_templates(self, language: Optional[str] = None, 
                             category: Optional[str] = None) -> Dict[str, Any]:
        """List available project templates with optional filtering."""
        try:
            templates = list(self.project_templates.values())
            
            # Apply language filter
            if language:
                templates = [t for t in templates if t.language.lower() == language.lower()]
            
            # Apply category filter
            if category:
                templates = [t for t in templates if t.category.lower() == category.lower()]
            
            # Convert to serializable format
            template_list = []
            for template in templates:
                template_list.append({
                    "template_id": template.template_id,
                    "name": template.name,
                    "description": template.description,
                    "language": template.language,
                    "framework": template.framework,
                    "category": template.category,
                    "tags": template.tags,
                    "build_system": template.build_system,
                    "testing_framework": template.testing_framework
                })
            
            logger.info(f"Listed {len(template_list)} project templates")
            
            return {
                "success": True,
                "message": f"Found {len(template_list)} project templates",
                "templates": template_list,
                "total_count": len(template_list),
                "filters_applied": {
                    "language": language,
                    "category": category
                }
            }
            
        except Exception as e:
            logger.error(f"Error listing project templates: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_project(self, template_id: str, project_name: str, 
                        target_path: str = ".", 
                        customizations: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a new project from a template."""
        try:
            if template_id not in self.project_templates:
                return {
                    "success": False,
                    "error": f"Template {template_id} not found"
                }
            
            template = self.project_templates[template_id]
            customizations = customizations or {}
            
            # Create project ID
            project_id = f"{template.language}_{project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create project structure
            project_structure = ProjectStructure(
                project_id=project_id,
                project_name=project_name,
                language=template.language,
                framework=template.framework,
                base_path=target_path,
                metadata={
                    "template_id": template_id,
                    "customizations": customizations,
                    "generated_by": self.agent_id
                }
            )
            
            # Store project structure
            self.generated_projects[project_id] = project_structure
            
            logger.info(f"Generated project {project_name} using template {template_id}")
            
            return {
                "success": True,
                "message": f"Project '{project_name}' generated successfully using {template.name} template",
                "project_id": project_id,
                "project_name": project_name,
                "template": template.name,
                "language": template.language,
                "framework": template.framework,
                "build_system": template.build_system,
                "testing_framework": template.testing_framework,
                "project_structure": {
                    "base_path": target_path,
                    "files_to_create": template.files,
                    "dependencies": template.dependencies
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating project: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def customize_project_template(self, template_id: str, 
                                 customizations: Dict[str, Any]) -> Dict[str, Any]:
        """Customize an existing project template."""
        try:
            if template_id not in self.project_templates:
                return {
                    "success": False,
                    "error": f"Template {template_id} not found"
                }
            
            template = self.project_templates[template_id]
            
            # Create customized template
            customized_template = ProjectTemplate(
                template_id=f"{template_id}_custom_{uuid.uuid4().hex[:8]}",
                name=f"{template.name} (Customized)",
                description=template.description,
                language=template.language,
                framework=template.framework,
                category=template.category,
                tags=template.tags + ["customized"],
                files=template.files,
                dependencies=template.dependencies + customizations.get("additional_dependencies", []),
                build_system=template.build_system,
                testing_framework=template.testing_framework,
                ci_cd_template=template.ci_cd_template
            )
            
            # Store customized template
            self.project_templates[customized_template.template_id] = customized_template
            
            logger.info(f"Customized template {template_id} with {len(customizations)} customizations")
            
            return {
                "success": True,
                "message": f"Template {template.name} customized successfully",
                "customized_template_id": customized_template.template_id,
                "customizations_applied": customizations,
                "new_template": {
                    "name": customized_template.name,
                    "description": customized_template.description,
                    "dependencies": customized_template.dependencies
                }
            }
            
        except Exception as e:
            logger.error(f"Error customizing template: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get status of a generated project."""
        try:
            if project_id not in self.generated_projects:
                return {
                    "success": False,
                    "error": f"Project {project_id} not found"
                }
            
            project = self.generated_projects[project_id]
            
            return {
                "success": True,
                "message": f"Project status retrieved successfully for {project.project_name}",
                "project": {
                    "project_id": project.project_id,
                    "project_name": project.project_name,
                    "language": project.language,
                    "framework": project.framework,
                    "base_path": project.base_path,
                    "files_created": project.files_created,
                    "directories_created": project.directories_created,
                    "build_files": project.build_files,
                    "test_files": project.test_files,
                    "config_files": project.config_files,
                    "created_at": project.created_at.isoformat(),
                    "metadata": project.metadata
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting project status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_generated_projects(self) -> Dict[str, Any]:
        """List all generated projects."""
        try:
            projects = []
            for project in self.generated_projects.values():
                projects.append({
                    "project_id": project.project_id,
                    "project_name": project.project_name,
                    "language": project.language,
                    "framework": project.framework,
                    "base_path": project.base_path,
                    "created_at": project.created_at.isoformat()
                })
            
            logger.info(f"Listed {len(projects)} generated projects")
            
            return {
                "success": True,
                "message": f"Found {len(projects)} generated projects",
                "projects": projects,
                "total_count": len(projects)
            }
            
        except Exception as e:
            logger.error(f"Error listing generated projects: {e}")
            return {
                "success": False,
                "error": str(e)
            }
