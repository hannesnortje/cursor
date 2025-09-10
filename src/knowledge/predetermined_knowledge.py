"""Phase 9.4: Predetermined Knowledge Bases with optional loading and fallback support."""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeItem:
    """Structure for predetermined knowledge items."""

    title: str
    content: str
    category: str
    subcategory: str
    tags: List[str]
    priority: str  # "high", "medium", "low"
    source: str
    version: str
    last_updated: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert knowledge item to dictionary."""
        return {
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "subcategory": self.subcategory,
            "tags": self.tags,
            "priority": self.priority,
            "source": self.source,
            "version": self.version,
            "last_updated": self.last_updated,
        }


class PredeterminedKnowledgeBase:
    """Comprehensive predetermined knowledge base for project initialization."""

    def __init__(self):
        self.knowledge_bases = {}
        self.loading_enabled = True
        self.fallback_mode = False
        self.initialization_status = "not_initialized"

        try:
            self._initialize_knowledge_bases()
            self.initialization_status = "initialized"
            logger.info("Predetermined knowledge base initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize knowledge bases: {e}")
            self.fallback_mode = True
            self.initialization_status = "fallback_mode"
            logger.info("Using fallback knowledge base")

    def _initialize_knowledge_bases(self):
        """Initialize all knowledge bases."""
        if not self.loading_enabled:
            logger.info("Knowledge loading disabled - using fallback mode")
            self.fallback_mode = True
            return

        self.knowledge_bases = {
            "pdca": self._get_pdca_knowledge(),
            "agile": self._get_agile_knowledge(),
            "code_quality": self._get_code_quality_knowledge(),
            "security": self._get_security_knowledge(),
            "testing": self._get_testing_knowledge(),
            "documentation": self._get_documentation_knowledge(),
        }

        total_items = sum(len(items) for items in self.knowledge_bases.values())
        logger.info(
            f"Initialized {len(self.knowledge_bases)} knowledge domains with {total_items} total items"
        )

    def _get_pdca_knowledge(self) -> List[KnowledgeItem]:
        """Get PDCA Framework knowledge."""
        return [
            KnowledgeItem(
                title="PDCA Framework Overview",
                content="Plan-Do-Check-Act (PDCA) is a four-step management method for continuous improvement. Plan: Define objectives and plan solutions. Do: Implement the plan. Check: Monitor results and measure effectiveness. Act: Standardize successful approaches and improve processes.",
                category="methodology",
                subcategory="pdca",
                tags=["pdca", "continuous_improvement", "management"],
                priority="high",
                source="ISO 9001",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
            KnowledgeItem(
                title="PDCA Planning Phase",
                content="The Plan phase involves: 1) Define objectives and goals, 2) Analyze current state, 3) Identify root causes, 4) Develop solutions, 5) Create implementation plan, 6) Set success criteria and metrics.",
                category="methodology",
                subcategory="pdca_planning",
                tags=["pdca", "planning", "objectives"],
                priority="high",
                source="Quality Management",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
            KnowledgeItem(
                title="PDCA Implementation Phase",
                content="The Do phase involves: 1) Execute the plan, 2) Implement solutions, 3) Monitor progress, 4) Document changes, 5) Collect data, 6) Maintain communication with stakeholders.",
                category="methodology",
                subcategory="pdca_implementation",
                tags=["pdca", "implementation", "execution"],
                priority="high",
                source="Quality Management",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
            KnowledgeItem(
                title="PDCA Check Phase",
                content="The Check phase involves: 1) Measure results against objectives, 2) Analyze data collected, 3) Compare actual vs planned outcomes, 4) Identify gaps and issues, 5) Document lessons learned.",
                category="methodology",
                subcategory="pdca_checking",
                tags=["pdca", "monitoring", "analysis"],
                priority="high",
                source="Quality Management",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
            KnowledgeItem(
                title="PDCA Act Phase",
                content="The Act phase involves: 1) Standardize successful approaches, 2) Implement improvements, 3) Update processes and procedures, 4) Share knowledge, 5) Plan next cycle, 6) Document best practices.",
                category="methodology",
                subcategory="pdca_acting",
                tags=["pdca", "standardization", "improvement"],
                priority="high",
                source="Quality Management",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
        ]

    def _get_agile_knowledge(self) -> List[KnowledgeItem]:
        """Get Agile/Scrum knowledge."""
        return [
            KnowledgeItem(
                title="Agile Manifesto Principles",
                content="The Agile Manifesto values: 1) Individuals and interactions over processes and tools, 2) Working software over comprehensive documentation, 3) Customer collaboration over contract negotiation, 4) Responding to change over following a plan.",
                category="methodology",
                subcategory="agile_principles",
                tags=["agile", "manifesto", "principles"],
                priority="high",
                source="Agile Manifesto",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
            KnowledgeItem(
                title="Scrum Framework",
                content="Scrum consists of: 1) Roles (Product Owner, Scrum Master, Development Team), 2) Events (Sprint Planning, Daily Scrum, Sprint Review, Sprint Retrospective), 3) Artifacts (Product Backlog, Sprint Backlog, Increment).",
                category="methodology",
                subcategory="scrum_framework",
                tags=["scrum", "framework", "roles"],
                priority="high",
                source="Scrum Guide",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
            KnowledgeItem(
                title="User Story Writing",
                content="User stories follow the format: 'As a [user type], I want [functionality] so that [benefit]'. They should be INVEST: Independent, Negotiable, Valuable, Estimable, Small, Testable.",
                category="methodology",
                subcategory="user_stories",
                tags=["user_stories", "requirements", "invest"],
                priority="high",
                source="Agile Best Practices",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
            KnowledgeItem(
                title="Sprint Planning",
                content="Sprint Planning involves: 1) Review product backlog, 2) Select items for sprint, 3) Break down tasks, 4) Estimate effort, 5) Create sprint goal, 6) Commit to sprint backlog.",
                category="methodology",
                subcategory="sprint_planning",
                tags=["sprint_planning", "backlog", "estimation"],
                priority="high",
                source="Scrum Guide",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
            KnowledgeItem(
                title="Sprint Retrospective",
                content="Sprint Retrospective focuses on: 1) What went well, 2) What could be improved, 3) Action items for next sprint, 4) Team dynamics, 5) Process improvements, 6) Celebration of achievements.",
                category="methodology",
                subcategory="retrospective",
                tags=["retrospective", "improvement", "team"],
                priority="medium",
                source="Scrum Guide",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
        ]

    def _get_code_quality_knowledge(self) -> List[KnowledgeItem]:
        """Get Code Quality knowledge."""
        return [
            KnowledgeItem(
                title="SOLID Principles",
                content="SOLID principles: 1) Single Responsibility - one reason to change, 2) Open/Closed - open for extension, closed for modification, 3) Liskov Substitution - derived classes must be substitutable, 4) Interface Segregation - many specific interfaces, 5) Dependency Inversion - depend on abstractions.",
                category="code_quality",
                subcategory="solid_principles",
                tags=["solid", "principles", "design"],
                priority="high",
                source="Clean Code",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
            KnowledgeItem(
                title="Clean Code Practices",
                content="Clean code practices: 1) Meaningful names, 2) Small functions, 3) Single responsibility, 4) No side effects, 5) Error handling, 6) Comments for why, not what, 7) Consistent formatting, 8) DRY principle.",
                category="code_quality",
                subcategory="clean_code",
                tags=["clean_code", "best_practices", "readability"],
                priority="high",
                source="Clean Code",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
            KnowledgeItem(
                title="Code Review Guidelines",
                content="Code review should check: 1) Functionality correctness, 2) Code readability, 3) Performance implications, 4) Security considerations, 5) Test coverage, 6) Documentation, 7) Adherence to standards, 8) Maintainability.",
                category="code_quality",
                subcategory="code_review",
                tags=["code_review", "quality", "standards"],
                priority="high",
                source="Best Practices",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
            KnowledgeItem(
                title="Refactoring Techniques",
                content="Common refactoring techniques: 1) Extract Method, 2) Extract Variable, 3) Rename Variable, 4) Move Method, 5) Replace Conditional with Polymorphism, 6) Introduce Parameter Object, 7) Replace Magic Numbers with Constants.",
                category="code_quality",
                subcategory="refactoring",
                tags=["refactoring", "techniques", "improvement"],
                priority="medium",
                source="Refactoring",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
        ]

    def _get_security_knowledge(self) -> List[KnowledgeItem]:
        """Get Security knowledge."""
        return [
            KnowledgeItem(
                title="OWASP Top 10",
                content="OWASP Top 10 vulnerabilities: 1) Injection, 2) Broken Authentication, 3) Sensitive Data Exposure, 4) XML External Entities, 5) Broken Access Control, 6) Security Misconfiguration, 7) Cross-Site Scripting, 8) Insecure Deserialization, 9) Known Vulnerabilities, 10) Insufficient Logging.",
                category="security",
                subcategory="owasp",
                tags=["owasp", "vulnerabilities", "security"],
                priority="high",
                source="OWASP",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
            KnowledgeItem(
                title="Secure Coding Practices",
                content="Secure coding practices: 1) Input validation, 2) Output encoding, 3) Authentication and authorization, 4) Session management, 5) Error handling, 6) Logging and monitoring, 7) Cryptographic practices, 8) Data protection.",
                category="security",
                subcategory="secure_coding",
                tags=["secure_coding", "practices", "security"],
                priority="high",
                source="Security Best Practices",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
            KnowledgeItem(
                title="Security Testing",
                content="Security testing includes: 1) Static Application Security Testing (SAST), 2) Dynamic Application Security Testing (DAST), 3) Interactive Application Security Testing (IAST), 4) Software Composition Analysis (SCA), 5) Penetration testing, 6) Vulnerability scanning.",
                category="security",
                subcategory="security_testing",
                tags=["security_testing", "sast", "dast"],
                priority="medium",
                source="Security Testing",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
        ]

    def _get_testing_knowledge(self) -> List[KnowledgeItem]:
        """Get Testing knowledge."""
        return [
            KnowledgeItem(
                title="Testing Pyramid",
                content="Testing Pyramid: 1) Unit Tests (70%) - Fast, isolated, test individual components, 2) Integration Tests (20%) - Test component interactions, 3) End-to-End Tests (10%) - Test complete user workflows. Focus on speed and reliability.",
                category="testing",
                subcategory="testing_pyramid",
                tags=["testing", "pyramid", "strategy"],
                priority="high",
                source="Testing Best Practices",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
            KnowledgeItem(
                title="Test-Driven Development",
                content="TDD Cycle: 1) Red - Write failing test, 2) Green - Write minimal code to pass, 3) Refactor - Improve code while keeping tests green. Benefits: Better design, comprehensive test coverage, documentation, confidence in changes.",
                category="testing",
                subcategory="tdd",
                tags=["tdd", "test_driven", "development"],
                priority="high",
                source="TDD Best Practices",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
            KnowledgeItem(
                title="Test Coverage Metrics",
                content="Test coverage metrics: 1) Line Coverage - percentage of code lines executed, 2) Branch Coverage - percentage of branches tested, 3) Function Coverage - percentage of functions called, 4) Statement Coverage - percentage of statements executed. Aim for 80%+ coverage.",
                category="testing",
                subcategory="coverage",
                tags=["coverage", "metrics", "testing"],
                priority="medium",
                source="Testing Metrics",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
            KnowledgeItem(
                title="Automated Testing",
                content="Automated testing benefits: 1) Faster feedback, 2) Consistent execution, 3) Reduced human error, 4) Continuous integration, 5) Regression prevention, 6) Cost reduction. Types: Unit, Integration, API, UI, Performance, Security tests.",
                category="testing",
                subcategory="automation",
                tags=["automation", "testing", "ci_cd"],
                priority="high",
                source="Testing Automation",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
        ]

    def _get_documentation_knowledge(self) -> List[KnowledgeItem]:
        """Get Documentation knowledge."""
        return [
            KnowledgeItem(
                title="Documentation Standards",
                content="Documentation standards: 1) Clear and concise language, 2) Consistent formatting, 3) Up-to-date information, 4) User-focused content, 5) Searchable and navigable, 6) Version control, 7) Review process, 8) Accessibility compliance.",
                category="documentation",
                subcategory="standards",
                tags=["documentation", "standards", "quality"],
                priority="high",
                source="Documentation Best Practices",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
            KnowledgeItem(
                title="API Documentation",
                content="API documentation should include: 1) Endpoint descriptions, 2) Request/response examples, 3) Authentication methods, 4) Error codes and handling, 5) Rate limiting, 6) SDKs and libraries, 7) Interactive examples, 8) Versioning information.",
                category="documentation",
                subcategory="api_docs",
                tags=["api", "documentation", "endpoints"],
                priority="high",
                source="API Documentation",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
            KnowledgeItem(
                title="Code Documentation",
                content="Code documentation includes: 1) Inline comments for complex logic, 2) Function/method documentation, 3) Class documentation, 4) README files, 5) Architecture diagrams, 6) Setup instructions, 7) Contributing guidelines, 8) Change logs.",
                category="documentation",
                subcategory="code_docs",
                tags=["code", "documentation", "comments"],
                priority="medium",
                source="Code Documentation",
                version="1.0",
                last_updated=datetime.now().isoformat(),
            ),
        ]

    def get_knowledge_for_domain(self, domain: str) -> List[KnowledgeItem]:
        """Get knowledge items for a specific domain."""
        if self.fallback_mode:
            return self._get_fallback_knowledge(domain)
        return self.knowledge_bases.get(domain, [])

    def get_all_knowledge(self) -> Dict[str, List[KnowledgeItem]]:
        """Get all knowledge bases."""
        if self.fallback_mode:
            return self._get_fallback_all_knowledge()
        return self.knowledge_bases

    def get_available_domains(self) -> List[str]:
        """Get list of available knowledge domains."""
        if self.fallback_mode:
            return [
                "pdca",
                "agile",
                "code_quality",
                "security",
                "testing",
                "documentation",
            ]
        return list(self.knowledge_bases.keys())

    def search_knowledge(
        self, query: str, domain: Optional[str] = None
    ) -> List[KnowledgeItem]:
        """Search knowledge items by content."""
        try:
            results = []
            query_lower = query.lower()

            if domain:
                knowledge_items = self.get_knowledge_for_domain(domain)
            else:
                all_knowledge = self.get_all_knowledge()
                knowledge_items = []
                for items in all_knowledge.values():
                    knowledge_items.extend(items)

            for item in knowledge_items:
                if (
                    query_lower in item.title.lower()
                    or query_lower in item.content.lower()
                    or any(query_lower in tag.lower() for tag in item.tags)
                ):
                    results.append(item)

            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        try:
            if self.fallback_mode:
                return {
                    "total_domains": 6,
                    "total_items": 24,
                    "fallback_mode": True,
                    "initialization_status": self.initialization_status,
                }

            total_items = sum(len(items) for items in self.knowledge_bases.values())
            domain_counts = {
                domain: len(items) for domain, items in self.knowledge_bases.items()
            }

            return {
                "total_domains": len(self.knowledge_bases),
                "total_items": total_items,
                "domain_counts": domain_counts,
                "fallback_mode": False,
                "initialization_status": self.initialization_status,
            }

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {
                "total_domains": 0,
                "total_items": 0,
                "fallback_mode": True,
                "initialization_status": "error",
                "error": str(e),
            }

    def initialize_project(
        self, project_id: str, domains: List[str] = None
    ) -> Dict[str, Any]:
        """Initialize project with predetermined knowledge."""
        try:
            if domains is None:
                domains = self.get_available_domains()

            project_knowledge = {}
            for domain in domains:
                domain_knowledge = self.get_knowledge_for_domain(domain)
                project_knowledge[domain] = [
                    item.to_dict() for item in domain_knowledge
                ]

            logger.info(
                f"Initialized project {project_id} with {len(domains)} knowledge domains"
            )

            return {
                "success": True,
                "project_id": project_id,
                "domains_initialized": domains,
                "knowledge_items": project_knowledge,
                "total_items": sum(len(items) for items in project_knowledge.values()),
            }

        except Exception as e:
            logger.error(f"Failed to initialize project: {e}")
            return {"success": False, "error": str(e)}

    def get_by_category(self, category: str) -> List[KnowledgeItem]:
        """Get knowledge items by category."""
        try:
            results = []
            all_knowledge = self.get_all_knowledge()

            for items in all_knowledge.values():
                for item in items:
                    if item.category == category:
                        results.append(item)

            return results

        except Exception as e:
            logger.error(f"Failed to get by category: {e}")
            return []

    def get_by_priority(self, priority: str) -> List[KnowledgeItem]:
        """Get knowledge items by priority."""
        try:
            results = []
            all_knowledge = self.get_all_knowledge()

            for items in all_knowledge.values():
                for item in items:
                    if item.priority == priority:
                        results.append(item)

            return results

        except Exception as e:
            logger.error(f"Failed to get by priority: {e}")
            return []

    def _get_fallback_knowledge(self, domain: str) -> List[KnowledgeItem]:
        """Get fallback knowledge for a domain."""
        fallback_items = {
            "pdca": [
                KnowledgeItem(
                    title="PDCA Framework (Fallback)",
                    content="Plan-Do-Check-Act is a continuous improvement methodology.",
                    category="methodology",
                    subcategory="pdca",
                    tags=["pdca", "fallback"],
                    priority="high",
                    source="Fallback",
                    version="1.0",
                    last_updated=datetime.now().isoformat(),
                )
            ],
            "agile": [
                KnowledgeItem(
                    title="Agile Principles (Fallback)",
                    content="Agile focuses on iterative development and customer collaboration.",
                    category="methodology",
                    subcategory="agile",
                    tags=["agile", "fallback"],
                    priority="high",
                    source="Fallback",
                    version="1.0",
                    last_updated=datetime.now().isoformat(),
                )
            ],
        }
        return fallback_items.get(domain, [])

    def _get_fallback_all_knowledge(self) -> Dict[str, List[KnowledgeItem]]:
        """Get all fallback knowledge."""
        return {
            domain: self._get_fallback_knowledge(domain)
            for domain in self.get_available_domains()
        }

    def enable_loading(self):
        """Enable knowledge loading."""
        self.loading_enabled = True
        logger.info("Knowledge loading enabled")

    def disable_loading(self):
        """Disable knowledge loading."""
        self.loading_enabled = False
        self.fallback_mode = True
        logger.info("Knowledge loading disabled - using fallback mode")


# Global instance
_predetermined_knowledge = None


def get_predetermined_knowledge() -> PredeterminedKnowledgeBase:
    """Get the global predetermined knowledge instance."""
    global _predetermined_knowledge
    if _predetermined_knowledge is None:
        _predetermined_knowledge = PredeterminedKnowledgeBase()
    return _predetermined_knowledge
