"""Phase 9.4: Predetermined Knowledge Bases for Intelligent Memory Initialization."""

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


class PredeterminedKnowledgeBase:
    """Comprehensive predetermined knowledge base for project initialization."""
    
    def __init__(self):
        self.knowledge_bases = {
            "pdca": self._get_pdca_knowledge(),
            "agile": self._get_agile_knowledge(),
            "code_quality": self._get_code_quality_knowledge(),
            "security": self._get_security_knowledge(),
            "testing": self._get_testing_knowledge(),
            "documentation": self._get_documentation_knowledge()
        }
        
        logger.info("Predetermined knowledge base initialized with 6 knowledge domains")
    
    def get_knowledge_for_domain(self, domain: str) -> List[KnowledgeItem]:
        """Get knowledge items for a specific domain."""
        return self.knowledge_bases.get(domain, [])
    
    def get_all_knowledge(self) -> Dict[str, List[KnowledgeItem]]:
        """Get all knowledge bases."""
        return self.knowledge_bases
    
    def get_available_domains(self) -> List[str]:
        """Get list of available knowledge domains."""
        return list(self.knowledge_bases.keys())
    
    def _get_pdca_knowledge(self) -> List[KnowledgeItem]:
        """PDCA Framework knowledge base."""
        return [
            KnowledgeItem(
                title="PDCA Framework Overview",
                content="""The PDCA (Plan-Do-Check-Act) cycle is a four-step management method used for continuous improvement of processes and products. It's also known as the Deming Cycle or Shewhart Cycle.

**The Four Steps:**
1. **Plan**: Identify the problem, analyze current situation, set objectives, and plan solutions
2. **Do**: Implement the plan on a small scale to test the solution
3. **Check**: Monitor and measure the results against expected outcomes
4. **Act**: Standardize successful solutions or adjust the plan based on results

**Key Principles:**
- Continuous improvement mindset
- Data-driven decision making
- Small-scale testing before full implementation
- Standardization of successful practices
- Learning from failures and successes""",
                category="methodology",
                subcategory="pdca",
                tags=["pdca", "continuous-improvement", "methodology", "quality"],
                priority="high",
                source="Deming/Shewhart",
                version="1.0",
                last_updated=datetime.now().isoformat()
            ),
            KnowledgeItem(
                title="Plan Phase Best Practices",
                content="""**Plan Phase Execution:**

1. **Problem Identification**
   - Use 5W1H (What, Why, When, Where, Who, How)
   - Root cause analysis techniques
   - Stakeholder input gathering

2. **Current State Analysis**
   - Process mapping
   - Data collection and analysis
   - Gap identification

3. **Objective Setting**
   - SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound)
   - Success criteria definition
   - Resource requirements

4. **Solution Planning**
   - Brainstorming sessions
   - Feasibility analysis
   - Risk assessment
   - Implementation timeline

**Tools and Techniques:**
- Fishbone diagrams (Ishikawa)
- 5 Whys analysis
- Process flowcharts
- Gantt charts
- Risk matrices""",
                category="methodology",
                subcategory="pdca_plan",
                tags=["pdca", "planning", "analysis", "tools"],
                priority="high",
                source="Quality Management",
                version="1.0",
                last_updated=datetime.now().isoformat()
            ),
            KnowledgeItem(
                title="Do Phase Implementation",
                content="""**Do Phase Execution:**

1. **Pilot Implementation**
   - Start with small-scale testing
   - Select representative sample
   - Document all changes and observations

2. **Data Collection**
   - Establish measurement systems
   - Record baseline data
   - Monitor key performance indicators

3. **Team Training**
   - Ensure all team members understand the changes
   - Provide necessary training and resources
   - Establish communication channels

4. **Change Management**
   - Address resistance to change
   - Maintain stakeholder engagement
   - Document lessons learned

**Success Factors:**
- Clear communication
- Adequate resources
- Team commitment
- Proper documentation
- Regular monitoring""",
                category="methodology",
                subcategory="pdca_do",
                tags=["pdca", "implementation", "pilot", "change-management"],
                priority="high",
                source="Change Management",
                version="1.0",
                last_updated=datetime.now().isoformat()
            ),
            KnowledgeItem(
                title="Check Phase Analysis",
                content="""**Check Phase Execution:**

1. **Data Analysis**
   - Compare actual results with planned objectives
   - Statistical analysis of performance data
   - Trend analysis and pattern recognition

2. **Performance Evaluation**
   - KPI measurement and analysis
   - Cost-benefit analysis
   - Quality metrics assessment

3. **Root Cause Analysis**
   - Identify factors that influenced results
   - Distinguish between correlation and causation
   - Document findings and insights

4. **Gap Analysis**
   - Compare current state with target state
   - Identify areas for improvement
   - Prioritize next steps

**Analysis Tools:**
- Control charts
- Pareto analysis
- Scatter plots
- Statistical process control
- Benchmarking""",
                category="methodology",
                subcategory="pdca_check",
                tags=["pdca", "analysis", "evaluation", "metrics"],
                priority="high",
                source="Statistical Analysis",
                version="1.0",
                last_updated=datetime.now().isoformat()
            ),
            KnowledgeItem(
                title="Act Phase Standardization",
                content="""**Act Phase Execution:**

1. **Standardization**
   - Document successful practices
   - Create standard operating procedures
   - Establish new processes and guidelines

2. **Full Implementation**
   - Roll out changes across the organization
   - Provide training and support
   - Monitor implementation progress

3. **Continuous Improvement**
   - Plan next improvement cycle
   - Identify new opportunities
   - Share lessons learned

4. **Knowledge Management**
   - Document best practices
   - Create knowledge repositories
   - Share success stories

**Standardization Elements:**
- Process documentation
- Training materials
- Quality standards
- Performance metrics
- Review schedules""",
                category="methodology",
                subcategory="pdca_act",
                tags=["pdca", "standardization", "implementation", "continuous-improvement"],
                priority="high",
                source="Process Management",
                version="1.0",
                last_updated=datetime.now().isoformat()
            )
        ]
    
    def _get_agile_knowledge(self) -> List[KnowledgeItem]:
        """Agile/Scrum knowledge base."""
        return [
            KnowledgeItem(
                title="Agile Manifesto Principles",
                content="""**The Agile Manifesto Values:**
1. Individuals and interactions over processes and tools
2. Working software over comprehensive documentation
3. Customer collaboration over contract negotiation
4. Responding to change over following a plan

**The 12 Agile Principles:**
1. Customer satisfaction through early and continuous delivery
2. Welcome changing requirements, even late in development
3. Deliver working software frequently (weeks, not months)
4. Business people and developers must work together daily
5. Build projects around motivated individuals
6. Face-to-face conversation is most effective
7. Working software is the primary measure of progress
8. Sustainable development pace
9. Continuous attention to technical excellence
10. Simplicity is essential
11. Self-organizing teams produce best results
12. Regular reflection and adaptation""",
                category="methodology",
                subcategory="agile_principles",
                tags=["agile", "manifesto", "principles", "values"],
                priority="high",
                source="Agile Manifesto",
                version="1.0",
                last_updated=datetime.now().isoformat()
            ),
            KnowledgeItem(
                title="Scrum Framework Overview",
                content="""**Scrum Roles:**
- **Product Owner**: Defines requirements, prioritizes backlog, accepts deliverables
- **Scrum Master**: Facilitates process, removes impediments, coaches team
- **Development Team**: Cross-functional team that delivers the product

**Scrum Events:**
1. **Sprint Planning**: Plan work for upcoming sprint (2-4 hours)
2. **Daily Scrum**: 15-minute daily synchronization meeting
3. **Sprint Review**: Demonstrate completed work to stakeholders
4. **Sprint Retrospective**: Reflect on process and improve

**Scrum Artifacts:**
- **Product Backlog**: Prioritized list of features and requirements
- **Sprint Backlog**: Selected items for current sprint
- **Increment**: Working software delivered at sprint end

**Sprint Duration**: Typically 1-4 weeks, most commonly 2 weeks""",
                category="methodology",
                subcategory="scrum_framework",
                tags=["scrum", "framework", "roles", "events", "artifacts"],
                priority="high",
                source="Scrum Guide",
                version="1.0",
                last_updated=datetime.now().isoformat()
            ),
            KnowledgeItem(
                title="User Story Writing",
                content="""**User Story Format:**
"As a [user type], I want [functionality] so that [benefit]"

**Example:**
"As a customer, I want to reset my password so that I can regain access to my account"

**User Story Components:**
- **Card**: Brief description on index card
- **Conversation**: Discussion between team and stakeholders
- **Confirmation**: Acceptance criteria and tests

**INVEST Criteria:**
- **Independent**: Can be developed and tested alone
- **Negotiable**: Details can be discussed and refined
- **Valuable**: Provides value to user or business
- **Estimable**: Team can estimate effort required
- **Small**: Can be completed in one sprint
- **Testable**: Can be verified with acceptance tests

**Acceptance Criteria Examples:**
- Given I am on the login page
- When I click "Forgot Password"
- Then I should receive an email with reset instructions
- And I should be able to set a new password""",
                category="methodology",
                subcategory="user_stories",
                tags=["user-stories", "requirements", "acceptance-criteria", "invest"],
                priority="high",
                source="Agile Development",
                version="1.0",
                last_updated=datetime.now().isoformat()
            ),
            KnowledgeItem(
                title="Sprint Planning Best Practices",
                content="""**Sprint Planning Preparation:**
- Product backlog is refined and prioritized
- Team capacity is known
- Dependencies are identified
- Technical spikes are completed

**Sprint Planning Process:**
1. **Product Owner presents sprint goal**
2. **Team selects items from backlog**
3. **Team breaks down items into tasks**
4. **Team estimates effort for each task**
5. **Team commits to sprint goal**

**Estimation Techniques:**
- **Story Points**: Relative sizing (Fibonacci sequence)
- **Planning Poker**: Team consensus on estimates
- **T-shirt Sizing**: XS, S, M, L, XL
- **Time Boxing**: Time-based estimates

**Sprint Goal Example:**
"Improve user authentication system to support multi-factor authentication and reduce security incidents by 50%"

**Definition of Done:**
- Code is written and reviewed
- Unit tests pass
- Integration tests pass
- Documentation is updated
- Product Owner accepts the feature""",
                category="methodology",
                subcategory="sprint_planning",
                tags=["sprint-planning", "estimation", "planning-poker", "definition-of-done"],
                priority="high",
                source="Scrum Practices",
                version="1.0",
                last_updated=datetime.now().isoformat()
            ),
            KnowledgeItem(
                title="Retrospective Techniques",
                content="""**Retrospective Structure:**
1. **Set the Stage** (5 min): Create safe environment
2. **Gather Data** (10-15 min): Collect facts and observations
3. **Generate Insights** (10-15 min): Identify patterns and root causes
4. **Decide What to Do** (10-15 min): Choose improvements
5. **Close the Retrospective** (5 min): Summarize and commit

**Popular Retrospective Formats:**

**Start-Stop-Continue:**
- What should we start doing?
- What should we stop doing?
- What should we continue doing?

**Mad-Sad-Glad:**
- What made us mad?
- What made us sad?
- What made us glad?

**4Ls (Liked, Learned, Lacked, Longed For):**
- What did we like?
- What did we learn?
- What was lacking?
- What do we long for?

**Sailboat Retrospective:**
- Wind: What pushed us forward?
- Anchor: What held us back?
- Island: What are we trying to reach?
- Rocks: What are the risks?""",
                category="methodology",
                subcategory="retrospectives",
                tags=["retrospectives", "continuous-improvement", "team-reflection", "agile"],
                priority="medium",
                source="Agile Retrospectives",
                version="1.0",
                last_updated=datetime.now().isoformat()
            )
        ]
    
    def _get_code_quality_knowledge(self) -> List[KnowledgeItem]:
        """Code Quality best practices knowledge base."""
        return [
            KnowledgeItem(
                title="Clean Code Principles",
                content="""**Clean Code Fundamentals:**

**Meaningful Names:**
- Use intention-revealing names
- Avoid disinformation and mental mapping
- Make meaningful distinctions
- Use pronounceable and searchable names
- Avoid prefixes and encodings

**Functions:**
- Small and focused (single responsibility)
- Do one thing well
- Use descriptive names
- Minimize parameters (0-3 ideal)
- Avoid side effects

**Comments:**
- Code should be self-documenting
- Comments should explain "why", not "what"
- Avoid redundant, misleading, or commented-out code
- Use comments for complex business logic

**Formatting:**
- Consistent indentation and spacing
- Logical grouping of related code
- Appropriate line length (80-120 characters)
- Consistent naming conventions

**Error Handling:**
- Use exceptions rather than return codes
- Don't ignore exceptions
- Provide meaningful error messages
- Handle errors at appropriate levels""",
                category="development",
                subcategory="clean_code",
                tags=["clean-code", "best-practices", "readability", "maintainability"],
                priority="high",
                source="Clean Code by Robert Martin",
                version="1.0",
                last_updated=datetime.now().isoformat()
            ),
            KnowledgeItem(
                title="SOLID Principles",
                content="""**SOLID Design Principles:**

**S - Single Responsibility Principle (SRP):**
- A class should have only one reason to change
- Each class should have one responsibility
- Separate concerns into different classes

**O - Open/Closed Principle (OCP):**
- Software entities should be open for extension, closed for modification
- Use inheritance and composition
- Design for future changes

**L - Liskov Substitution Principle (LSP):**
- Objects of a superclass should be replaceable with objects of subclasses
- Subclasses should not break parent class contracts
- Maintain behavioral compatibility

**I - Interface Segregation Principle (ISP):**
- Clients should not depend on interfaces they don't use
- Create specific interfaces rather than general ones
- Avoid fat interfaces

**D - Dependency Inversion Principle (DIP):**
- Depend on abstractions, not concretions
- High-level modules should not depend on low-level modules
- Both should depend on abstractions

**Benefits:**
- Maintainable and flexible code
- Easier testing and debugging
- Reduced coupling and increased cohesion
- Better code reusability""",
                category="development",
                subcategory="solid_principles",
                tags=["solid", "design-principles", "architecture", "maintainability"],
                priority="high",
                source="Object-Oriented Design",
                version="1.0",
                last_updated=datetime.now().isoformat()
            ),
            KnowledgeItem(
                title="Code Review Best Practices",
                content="""**Code Review Guidelines:**

**What to Look For:**
- Correctness and functionality
- Code quality and readability
- Performance implications
- Security vulnerabilities
- Test coverage
- Documentation completeness

**Review Process:**
1. **Self-Review First**: Review your own code before submitting
2. **Small, Focused Changes**: Keep PRs small and focused
3. **Clear Description**: Explain what and why
4. **Timely Reviews**: Review within 24 hours
5. **Constructive Feedback**: Be respectful and helpful

**Review Checklist:**
- [ ] Code follows team standards
- [ ] No obvious bugs or logic errors
- [ ] Performance considerations addressed
- [ ] Security best practices followed
- [ ] Tests are included and pass
- [ ] Documentation is updated
- [ ] No commented-out code
- [ ] Error handling is appropriate

**Common Issues to Flag:**
- Magic numbers without explanation
- Duplicate code that could be refactored
- Missing error handling
- Inefficient algorithms
- Security vulnerabilities
- Poor variable/function naming""",
                category="development",
                subcategory="code_review",
                tags=["code-review", "quality-assurance", "best-practices", "collaboration"],
                priority="high",
                source="Code Review Practices",
                version="1.0",
                last_updated=datetime.now().isoformat()
            ),
            KnowledgeItem(
                title="Refactoring Techniques",
                content="""**Common Refactoring Patterns:**

**Extract Method:**
- Break down large methods into smaller ones
- Improve readability and reusability
- Each method should do one thing

**Extract Class:**
- Split classes that have multiple responsibilities
- Follow Single Responsibility Principle
- Create focused, cohesive classes

**Move Method:**
- Move methods to more appropriate classes
- Improve class cohesion
- Reduce coupling between classes

**Replace Conditional with Polymorphism:**
- Use inheritance or composition
- Eliminate complex if-else chains
- Make code more extensible

**Introduce Parameter Object:**
- Group related parameters into objects
- Reduce parameter lists
- Improve method signatures

**Replace Magic Numbers with Named Constants:**
- Use descriptive constant names
- Make code more self-documenting
- Easier to maintain and modify

**Refactoring Safety:**
- Have comprehensive test coverage
- Refactor in small, incremental steps
- Run tests after each change
- Use automated refactoring tools when possible""",
                category="development",
                subcategory="refactoring",
                tags=["refactoring", "code-improvement", "maintainability", "techniques"],
                priority="medium",
                source="Refactoring by Martin Fowler",
                version="1.0",
                last_updated=datetime.now().isoformat()
            )
        ]
    
    def _get_security_knowledge(self) -> List[KnowledgeItem]:
        """Security patterns and practices knowledge base."""
        return [
            KnowledgeItem(
                title="OWASP Top 10 Security Risks",
                content="""**OWASP Top 10 (2021):**

1. **A01:2021 - Broken Access Control**
   - Implement proper access controls
   - Use principle of least privilege
   - Validate permissions on every request

2. **A02:2021 - Cryptographic Failures**
   - Use strong encryption algorithms
   - Protect sensitive data at rest and in transit
   - Implement proper key management

3. **A03:2021 - Injection**
   - Use parameterized queries
   - Validate and sanitize all inputs
   - Implement proper output encoding

4. **A04:2021 - Insecure Design**
   - Follow secure design principles
   - Implement threat modeling
   - Use secure coding practices

5. **A05:2021 - Security Misconfiguration**
   - Secure default configurations
   - Regular security updates
   - Disable unnecessary features

6. **A06:2021 - Vulnerable Components**
   - Keep dependencies updated
   - Monitor for known vulnerabilities
   - Use software composition analysis

7. **A07:2021 - Authentication Failures**
   - Implement strong authentication
   - Use multi-factor authentication
   - Protect against brute force attacks

8. **A08:2021 - Software and Data Integrity**
   - Verify software integrity
   - Use secure update mechanisms
   - Implement code signing

9. **A09:2021 - Logging and Monitoring Failures**
   - Implement comprehensive logging
   - Monitor for security events
   - Set up alerting systems

10. **A10:2021 - Server-Side Request Forgery**
    - Validate and sanitize URLs
    - Use allowlists for external requests
    - Implement network segmentation""",
                category="security",
                subcategory="owasp_top10",
                tags=["owasp", "security-risks", "vulnerabilities", "best-practices"],
                priority="high",
                source="OWASP Foundation",
                version="2021",
                last_updated=datetime.now().isoformat()
            ),
            KnowledgeItem(
                title="Secure Coding Practices",
                content="""**Input Validation:**
- Validate all inputs on the server side
- Use whitelist validation when possible
- Implement proper data sanitization
- Check data types, ranges, and formats

**Authentication and Authorization:**
- Use strong password policies
- Implement multi-factor authentication
- Use secure session management
- Apply principle of least privilege
- Implement proper logout functionality

**Data Protection:**
- Encrypt sensitive data at rest
- Use HTTPS for data in transit
- Implement proper key management
- Use secure random number generators
- Protect against data leakage

**Error Handling:**
- Don't expose sensitive information in errors
- Log security events appropriately
- Use generic error messages for users
- Implement proper exception handling

**Secure Communication:**
- Use TLS/SSL for all communications
- Implement certificate pinning
- Use secure protocols (HTTPS, WSS)
- Validate SSL certificates

**Code Security:**
- Avoid hardcoded secrets
- Use secure coding libraries
- Implement proper input/output encoding
- Regular security code reviews""",
                category="security",
                subcategory="secure_coding",
                tags=["secure-coding", "authentication", "encryption", "validation"],
                priority="high",
                source="Security Best Practices",
                version="1.0",
                last_updated=datetime.now().isoformat()
            ),
            KnowledgeItem(
                title="Common Security Vulnerabilities",
                content="""**SQL Injection Prevention:**
- Use parameterized queries/prepared statements
- Validate and sanitize all inputs
- Use stored procedures
- Implement least privilege database access

**Cross-Site Scripting (XSS) Prevention:**
- Encode all output data
- Use Content Security Policy (CSP)
- Validate and sanitize inputs
- Use appropriate HTTP headers

**Cross-Site Request Forgery (CSRF) Prevention:**
- Use CSRF tokens
- Validate referer headers
- Implement SameSite cookie attributes
- Use double-submit cookie pattern

**Insecure Direct Object References:**
- Implement proper access controls
- Use indirect object references
- Validate user permissions
- Use UUIDs instead of sequential IDs

**Security Misconfiguration:**
- Remove default accounts and passwords
- Disable unnecessary services
- Keep software updated
- Use secure configurations
- Implement proper error handling

**Sensitive Data Exposure:**
- Encrypt sensitive data
- Use secure transmission protocols
- Implement proper data classification
- Regular security assessments""",
                category="security",
                subcategory="vulnerabilities",
                tags=["vulnerabilities", "injection", "xss", "csrf", "prevention"],
                priority="high",
                source="Security Research",
                version="1.0",
                last_updated=datetime.now().isoformat()
            )
        ]
    
    def _get_testing_knowledge(self) -> List[KnowledgeItem]:
        """Testing strategies and automation knowledge base."""
        return [
            KnowledgeItem(
                title="Testing Pyramid Strategy",
                content="""**Testing Pyramid Levels:**

**Unit Tests (70%):**
- Test individual functions and methods
- Fast execution and quick feedback
- High code coverage
- Isolated and independent
- Written by developers

**Integration Tests (20%):**
- Test interactions between components
- Database and API integrations
- Service-to-service communication
- Medium execution time
- Written by developers and QA

**End-to-End Tests (10%):**
- Test complete user workflows
- Full system integration
- Slow execution but high confidence
- Critical user journeys
- Written by QA and developers

**Benefits of Testing Pyramid:**
- Fast feedback on code changes
- Cost-effective testing strategy
- High confidence in code quality
- Easier maintenance and debugging
- Better test coverage

**Test Automation Best Practices:**
- Automate repetitive tests
- Focus on stable, critical functionality
- Maintain test data and environments
- Regular test maintenance
- Monitor test execution and results""",
                category="testing",
                subcategory="testing_pyramid",
                tags=["testing-pyramid", "unit-tests", "integration-tests", "e2e-tests"],
                priority="high",
                source="Testing Strategies",
                version="1.0",
                last_updated=datetime.now().isoformat()
            ),
            KnowledgeItem(
                title="Test-Driven Development (TDD)",
                content="""**TDD Cycle (Red-Green-Refactor):**

**1. Red Phase:**
- Write a failing test
- Test should fail for the right reason
- Define the expected behavior
- Keep tests simple and focused

**2. Green Phase:**
- Write minimal code to make test pass
- Don't worry about code quality yet
- Focus on making the test pass
- Avoid over-engineering

**3. Refactor Phase:**
- Improve code quality without changing behavior
- Ensure all tests still pass
- Apply clean code principles
- Remove duplication

**TDD Benefits:**
- Better code design and architecture
- Comprehensive test coverage
- Faster debugging and maintenance
- Living documentation
- Increased confidence in changes

**TDD Best Practices:**
- Write tests before implementation
- Keep tests simple and readable
- One assertion per test
- Use descriptive test names
- Refactor regularly
- Maintain test independence""",
                category="testing",
                subcategory="tdd",
                tags=["tdd", "test-driven-development", "red-green-refactor", "best-practices"],
                priority="high",
                source="Agile Development",
                version="1.0",
                last_updated=datetime.now().isoformat()
            ),
            KnowledgeItem(
                title="API Testing Strategies",
                content="""**API Testing Types:**

**Functional Testing:**
- Test API endpoints and methods
- Validate request/response formats
- Test error handling and status codes
- Verify business logic implementation

**Performance Testing:**
- Load testing with expected traffic
- Stress testing beyond normal capacity
- Volume testing with large data sets
- Spike testing for traffic bursts

**Security Testing:**
- Authentication and authorization
- Input validation and sanitization
- SQL injection and XSS testing
- Rate limiting and throttling

**API Testing Tools:**
- **Postman**: Manual and automated testing
- **Newman**: Command-line Postman runner
- **REST Assured**: Java-based API testing
- **Insomnia**: API testing and debugging
- **SoapUI**: SOAP and REST API testing

**API Test Automation:**
- Use version control for test cases
- Implement CI/CD integration
- Monitor API performance metrics
- Maintain test data and environments
- Regular regression testing""",
                category="testing",
                subcategory="api_testing",
                tags=["api-testing", "rest", "performance", "security", "automation"],
                priority="medium",
                source="API Testing Practices",
                version="1.0",
                last_updated=datetime.now().isoformat()
            ),
            KnowledgeItem(
                title="Test Automation Best Practices",
                content="""**Test Automation Guidelines:**

**Test Design Principles:**
- **Independent**: Tests should not depend on each other
- **Repeatable**: Tests should produce same results every time
- **Self-Validating**: Tests should clearly pass or fail
- **Timely**: Tests should be written at appropriate time

**Test Data Management:**
- Use test data factories
- Avoid hardcoded test data
- Clean up test data after tests
- Use realistic test scenarios
- Maintain test data consistency

**Test Environment Management:**
- Isolated test environments
- Consistent environment setup
- Automated environment provisioning
- Environment-specific configurations
- Regular environment maintenance

**CI/CD Integration:**
- Run tests on every code change
- Fast feedback on test failures
- Parallel test execution
- Test result reporting and notifications
- Automated deployment on test success

**Test Maintenance:**
- Regular test review and updates
- Remove obsolete tests
- Refactor test code
- Monitor test execution metrics
- Document test scenarios""",
                category="testing",
                subcategory="automation",
                tags=["test-automation", "ci-cd", "maintenance", "best-practices"],
                priority="medium",
                source="Test Automation",
                version="1.0",
                last_updated=datetime.now().isoformat()
            )
        ]
    
    def _get_documentation_knowledge(self) -> List[KnowledgeItem]:
        """Documentation standards and templates knowledge base."""
        return [
            KnowledgeItem(
                title="Technical Documentation Standards",
                content="""**Documentation Types:**

**API Documentation:**
- Endpoint descriptions and parameters
- Request/response examples
- Authentication requirements
- Error codes and messages
- Rate limiting information

**Code Documentation:**
- Function and method descriptions
- Parameter and return value details
- Usage examples and code snippets
- Error handling information
- Performance considerations

**Architecture Documentation:**
- System overview and components
- Data flow diagrams
- Database schema documentation
- Integration points and dependencies
- Deployment and infrastructure details

**User Documentation:**
- Getting started guides
- Feature descriptions and usage
- Troubleshooting guides
- FAQ sections
- Video tutorials and screenshots

**Documentation Best Practices:**
- Keep documentation up-to-date
- Use clear and concise language
- Include examples and code snippets
- Organize content logically
- Use consistent formatting and style
- Make documentation searchable
- Include diagrams and visuals""",
                category="documentation",
                subcategory="standards",
                tags=["documentation", "api-docs", "technical-writing", "standards"],
                priority="high",
                source="Technical Writing",
                version="1.0",
                last_updated=datetime.now().isoformat()
            ),
            KnowledgeItem(
                title="README Template",
                content="""**Project README Structure:**

# Project Name
Brief description of what the project does.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## Installation
```bash
# Prerequisites
- Node.js 16+
- Python 3.8+
- Docker (optional)

# Install dependencies
npm install
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration
```

## Usage
```bash
# Start the application
npm start
python app.py

# Run tests
npm test
pytest
```

## API Reference
### Authentication
All API requests require authentication via Bearer token.

### Endpoints
- `GET /api/users` - Get all users
- `POST /api/users` - Create new user
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License
This project is licensed under the MIT License.""",
                category="documentation",
                subcategory="readme_template",
                tags=["readme", "template", "project-documentation", "markdown"],
                priority="medium",
                source="Open Source Practices",
                version="1.0",
                last_updated=datetime.now().isoformat()
            ),
            KnowledgeItem(
                title="Code Commenting Standards",
                content="""**Comment Types and Guidelines:**

**File Header Comments:**
- Project name and description
- Author and creation date
- License information
- Version history
- Purpose and usage

**Function/Method Comments:**
- Purpose and functionality
- Parameters and their types
- Return values and types
- Side effects and exceptions
- Usage examples

**Inline Comments:**
- Explain complex logic
- Clarify non-obvious code
- Document business rules
- Highlight important considerations
- Avoid stating the obvious

**Comment Best Practices:**
- Write comments in English
- Use proper grammar and spelling
- Keep comments concise but informative
- Update comments when code changes
- Use consistent formatting
- Avoid commented-out code
- Use TODO comments for future work

**Example:**
```python
def calculate_discount(price, customer_type, membership_years):
    \"\"\"
    Calculate discount based on customer type and membership duration.
    
    Args:
        price (float): Original price of the item
        customer_type (str): Type of customer ('regular', 'premium', 'vip')
        membership_years (int): Years of membership
    
    Returns:
        float: Calculated discount amount
    
    Raises:
        ValueError: If customer_type is invalid or price is negative
    \"\"\"
    # Validate inputs
    if price < 0:
        raise ValueError("Price cannot be negative")
    
    # Calculate base discount based on customer type
    if customer_type == 'vip':
        base_discount = 0.15  # 15% for VIP customers
    elif customer_type == 'premium':
        base_discount = 0.10  # 10% for premium customers
    else:
        base_discount = 0.05  # 5% for regular customers
    
    # Apply membership bonus
    membership_bonus = min(membership_years * 0.01, 0.05)  # Max 5% bonus
    
    return price * (base_discount + membership_bonus)
```""",
                category="documentation",
                subcategory="code_comments",
                tags=["code-comments", "documentation", "standards", "best-practices"],
                priority="medium",
                source="Code Documentation",
                version="1.0",
                last_updated=datetime.now().isoformat()
            )
        ]


# Global instance for easy access
_predetermined_knowledge = None

def get_predetermined_knowledge() -> PredeterminedKnowledgeBase:
    """Get the global predetermined knowledge base instance."""
    global _predetermined_knowledge
    if _predetermined_knowledge is None:
        _predetermined_knowledge = PredeterminedKnowledgeBase()
    return _predetermined_knowledge
