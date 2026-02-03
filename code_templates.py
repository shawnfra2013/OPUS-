`#!/usr/bin/env python3
"""
Agent Template System
Provides templates for common code generation tasks with built-in testing

Templates include:
- What to generate
- How to test it
- Verification commands
- Risk assessment
"""

import json
from typing import Dict, List

class CodeTemplate:
    """Base template for code generation with testing"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def get_prompt(self) -> str:
        """Return the prompt to send to the agent"""
        raise NotImplementedError
    
    def get_test_commands(self) -> List[Dict]:
        """Return commands to test the generated code"""
        raise NotImplementedError
    
    def get_verification_steps(self) -> List[str]:
        """Return steps user can run to verify"""
        raise NotImplementedError
    
    def get_files_to_create(self) -> Dict[str, str]:
        """Return expected files with descriptions"""
        raise NotImplementedError
    
    def get_risk_level(self) -> str:
        """Return risk level: low, medium, high"""
        return "medium"


class PythonWebScraperTemplate(CodeTemplate):
    """Web scraper with logging, retry logic, and error handling"""
    
    def __init__(self):
        super().__init__(
            "Python Web Scraper",
            "Production-grade web scraper with error handling and logging"
        )
    
    def get_prompt(self) -> str:
        return """Create a production-grade web scraper at /tmp/web_scraper.py with:

1. LOGGING SYSTEM:
   - Python logging module (not prints)
   - File logging to /tmp/scraper.log
   - Different log levels (DEBUG, INFO, WARNING, ERROR)
   - Limit log file size to 10MB with rotation

2. ROBUST ERROR HANDLING:
   - Network timeouts (retry up to 3 times)
   - Invalid URL validation
   - HTML parsing failures
   - File I/O errors
   - Rate limiting detection

3. ADVANCED FEATURES:
   - Request headers (User-Agent, Accept-Language)
   - Session management (connection pooling)
   - Response time tracking
   - URL normalization and deduplication
   - Metadata extraction

4. DATA QUALITY:
   - Validate extracted links
   - Filter out empty URLs
   - Remove duplicates
   - Sort by relevance

5. STATISTICS & REPORTING:
   - Count total links
   - Categorize links (internal/external)
   - Generate summary report in JSON
   - Track performance metrics

6. COMMAND LINE OPTIONS:
   - --url (required)
   - --output (default: /tmp/scraped_links.json)
   - --log-level (DEBUG, INFO, WARNING, ERROR)
   - --timeout (seconds)
   - --max-retries (default 3)

Make it enterprise-ready with comprehensive error messages."""
    
    def get_test_commands(self) -> List[Dict]:
        return [
            {
                "description": "Verify syntax",
                "cmd": "python3 -m py_compile /tmp/web_scraper.py",
                "test": True
            },
            {
                "description": "Test with example.com",
                "cmd": "python3 /tmp/web_scraper.py --url https://example.com --log-level INFO --timeout 10",
                "test": True
            },
            {
                "description": "Check output format",
                "cmd": "python3 -m json.tool /tmp/scraped_links.json | head -20",
                "test": True
            },
            {
                "description": "Check log file",
                "cmd": "tail -20 /tmp/scraper.log",
                "test": True
            }
        ]
    
    def get_verification_steps(self) -> List[str]:
        return [
            "python3 /tmp/web_scraper.py --url https://example.com",
            "cat /tmp/scraped_links.json | python3 -m json.tool",
            "tail -50 /tmp/scraper.log | grep -i 'error\\|warning'",
            "python3 /tmp/web_scraper.py --help"
        ]
    
    def get_files_to_create(self) -> Dict[str, str]:
        return {
            "/tmp/web_scraper.py": "Web scraper script (100-150 lines expected)"
        }
    
    def get_risk_level(self) -> str:
        return "low"


class SwiftNetworkManagerTemplate(CodeTemplate):
    """Production-grade Swift networking library"""
    
    def __init__(self):
        super().__init__(
            "Swift NetworkManager",
            "Enterprise iOS networking with logging, retry, and error handling"
        )
    
    def get_prompt(self) -> str:
        return """Create an ENTERPRISE-GRADE Swift NetworkManager at /tmp/NetworkManager.swift:

1. REQUEST BODY HANDLING:
   - JSON serialization for POST/PUT/PATCH
   - Content-Type headers
   - Different content types (JSON, form-data)
   - Parameter validation

2. COMPREHENSIVE LOGGING:
   - Log requests: method, URL, headers, body
   - Log responses: status, headers, body preview
   - Timestamps
   - OSLog framework
   - Request IDs for tracing

3. STATUS CODE HANDLING:
   - Accept 200, 201, 204 (success)
   - Handle 204 No Content
   - Proper 4xx (client) errors
   - Proper 5xx (server) errors
   - Follow redirects (3xx)

4. ROBUST ERROR HANDLING:
   - Network timeouts with retry (exponential backoff)
   - Transient errors retry (timeout, 5xx)
   - Permanent errors fail immediately (404, 401)
   - Custom error types
   - Network vs parsing errors

5. COMPLETE HTTP METHODS:
   - GET, POST, PUT, PATCH, DELETE, HEAD
   - Proper error handling each

6. ADVANCED FEATURES:
   - Request cancellation
   - Interceptors
   - Custom headers
   - SSL pinning option
   - Rate limiting (max 5 concurrent)

7. ASYNC/AWAIT:
   - Modern async/await support
   - Also callback version
   - Proper memory management
   - URLSession best practices

Include detailed comments explaining retry logic and error categorization."""
    
    def get_test_commands(self) -> List[Dict]:
        return [
            {
                "description": "Verify Swift syntax",
                "cmd": "swiftc -typecheck /tmp/NetworkManager.swift 2>&1 | head -10",
                "test": True
            },
            {
                "description": "Check file size",
                "cmd": "wc -l /tmp/NetworkManager.swift",
                "test": True
            },
            {
                "description": "Verify key patterns",
                "cmd": "grep -c 'async' /tmp/NetworkManager.swift && grep -c 'retry' /tmp/NetworkManager.swift",
                "test": True
            },
            {
                "description": "Check logging",
                "cmd": "grep -c 'os_log' /tmp/NetworkManager.swift",
                "test": True
            }
        ]
    
    def get_verification_steps(self) -> List[str]:
        return [
            "cat /tmp/NetworkManager.swift | head -50",
            "grep -n 'func\\|class' /tmp/NetworkManager.swift | head -20",
            "grep -n 'async\\|await' /tmp/NetworkManager.swift",
            "wc -l /tmp/NetworkManager.swift"
        ]
    
    def get_files_to_create(self) -> Dict[str, str]:
        return {
            "/tmp/NetworkManager.swift": "Production NetworkManager (200-300 lines expected)"
        }
    
    def get_risk_level(self) -> str:
        return "medium"


class ExpressAPITemplate(CodeTemplate):
    """Complete Express.js REST API boilerplate"""
    
    def __init__(self):
        super().__init__(
            "Express.js REST API",
            "Full-featured REST API with authentication, validation, and error handling"
        )
    
    def get_prompt(self) -> str:
        return """Create a complete Express.js REST API at /tmp/api_server.js:

1. SERVER SETUP:
   - Express initialization on port 3000
   - Middleware: JSON parsing, CORS, logging
   - Graceful shutdown

2. DATABASE:
   - MongoDB connection with error handling
   - Connection pooling
   - Retry logic

3. AUTHENTICATION:
   - JWT middleware
   - Token validation
   - Error responses for 401/403

4. ROUTES:
   - GET /users (list with pagination)
   - POST /users (create with validation)
   - GET /users/:id (get single)
   - PUT /users/:id (update)
   - DELETE /users/:id (delete)

5. VALIDATION:
   - Request body validation
   - Parameter validation
   - Error responses for invalid input

6. ERROR HANDLING:
   - Global error handler
   - Try/catch in routes
   - Meaningful error messages
   - Error logging

7. ADVANCED:
   - Request logging middleware
   - Rate limiting
   - CORS configuration
   - Environment variables

Make it immediately runnable: node /tmp/api_server.js"""
    
    def get_test_commands(self) -> List[Dict]:
        return [
            {
                "description": "Check syntax",
                "cmd": "node -c /tmp/api_server.js",
                "test": True
            },
            {
                "description": "Count lines",
                "cmd": "wc -l /tmp/api_server.js",
                "test": True
            },
            {
                "description": "Check routes",
                "cmd": "grep -c \"app\\.\" /tmp/api_server.js",
                "test": True
            },
            {
                "description": "Verify middleware",
                "cmd": "grep -c 'use\\|router' /tmp/api_server.js",
                "test": True
            }
        ]
    
    def get_verification_steps(self) -> List[str]:
        return [
            "cat /tmp/api_server.js | head -30",
            "grep 'app.listen' /tmp/api_server.js",
            "grep -E 'GET|POST|PUT|DELETE' /tmp/api_server.js | head -10",
            "node -c /tmp/api_server.js && echo 'Syntax OK'"
        ]
    
    def get_files_to_create(self) -> Dict[str, str]:
        return {
            "/tmp/api_server.js": "Express API server (150-200 lines expected)"
        }
    
    def get_risk_level(self) -> str:
        return "medium"


# Template registry
TEMPLATES = {
    "web-scraper": PythonWebScraperTemplate,
    "swift-network": SwiftNetworkManagerTemplate,
    "express-api": ExpressAPITemplate
}


def list_templates():
    """Print available templates"""
    print("\n📋 AVAILABLE TEMPLATES:\n")
    for key, template_class in TEMPLATES.items():
        t = template_class()
        print(f"  • {key}")
        print(f"    {t.description}\n")


def get_template(name: str) -> CodeTemplate:
    """Get template by name"""
    template_class = TEMPLATES.get(name)
    if not template_class:
        raise ValueError(f"Template not found: {name}")
    return template_class()


if __name__ == "__main__":
    list_templates()
