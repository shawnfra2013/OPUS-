# Complex Test Prompts for Agent

**Purpose**: Test agent's ability to handle multi-step reasoning, code generation, and real-world tasks

---

## Test 1: Build a Python Web Scraper
```
Create a Python script at /tmp/web_scraper.py that:
1. Uses requests to fetch https://example.com
2. Parses HTML with BeautifulSoup
3. Extracts all links and their titles
4. Saves results to /tmp/scraped_links.json
5. Includes proper error handling
6. Has a main() function with argument parsing for the URL

Make it production-ready with docstrings and type hints.
```

**Verification**: 
```bash
python3 /tmp/web_scraper.py https://example.com
cat /tmp/scraped_links.json
```

---

## Test 2: Create a Complete Swift iOS Module
```
Generate a complete, production-ready Swift file at /tmp/NetworkManager.swift that implements:
1. A NetworkManager class using URLSession
2. Generic method for GET/POST/PUT requests
3. Proper error handling with custom NetworkError enum
4. Request/response logging
5. Bearer token authentication support
6. Timeout configuration
7. Full docstrings and MARK comments for organization

The code should be immediately usable in a real iOS project.
```

**Verification**:
```bash
cat /tmp/NetworkManager.swift | head -50
```

---

## Test 3: Build a Node.js REST API Boilerplate
```
Create a complete Express.js REST API boilerplate at /tmp/api_server.js with:
1. Express server setup on port 3000
2. Middleware for JSON parsing and CORS
3. Database connection setup (MongoDB example)
4. Authentication middleware (JWT)
5. Error handling middleware
6. Routes for: GET /users, POST /users, GET /users/:id, PUT /users/:id, DELETE /users/:id
7. Environment variable configuration
8. Request validation
9. Comprehensive comments

The code should be ready to run with: node /tmp/api_server.js
```

**Verification**:
```bash
cat /tmp/api_server.js | grep "app.listen"
```

---

## Test 4: Generate Test Suite
```
Create a comprehensive Python test file at /tmp/test_utilities.py that:
1. Uses pytest framework
2. Contains 5 different test classes
3. Tests for utility functions (string manipulation, data validation, etc)
4. Includes fixtures, parametrized tests, and mocking
5. Has setup/teardown methods
6. Includes both positive and negative test cases
7. Uses assertions and expected exceptions
8. Has a pytest.ini configuration for the test runner

Make it demonstrate advanced pytest patterns.
```

**Verification**:
```bash
pytest /tmp/test_utilities.py -v
```

---

## Test 5: Data Processing Pipeline
```
Create a Python data processing script at /tmp/data_pipeline.py that:
1. Reads CSV data (generates sample data if needed)
2. Cleans data (removes duplicates, handles missing values)
3. Transforms data (normalizes, aggregates)
4. Performs analysis (groupby, statistics)
5. Generates visualizations (matplotlib)
6. Exports results to multiple formats (JSON, CSV, Excel)
7. Includes logging for debugging
8. Has performance timing for each step
9. Can be run with command-line arguments for input/output paths

Then execute it to generate sample output files.
```

**Verification**:
```bash
python3 /tmp/data_pipeline.py
ls -la /tmp/output_*
```

---

## Test 6: Docker & Kubernetes Config
```
Create a complete Docker + Kubernetes setup:
1. Dockerfile at /tmp/Dockerfile for a Node.js app with:
   - Multi-stage build
   - Security best practices
   - Proper caching layers
   - Health checks

2. docker-compose.yml at /tmp/docker-compose.yml with:
   - App service
   - PostgreSQL service
   - Redis cache service
   - Proper networking and volumes

3. kubernetes/deployment.yaml at /tmp/k8s_deployment.yaml with:
   - Deployment specification
   - Service definition
   - ConfigMap for environment variables
   - PersistentVolume claim
   - Resource limits and requests
   - Horizontal Pod Autoscaler

Then verify all files were created correctly.
```

**Verification**:
```bash
ls -la /tmp/Dockerfile /tmp/docker-compose.yml /tmp/k8s_deployment.yaml
wc -l /tmp/Dockerfile
```

---

## Test 7: API Integration & Testing
```
Create an automated API testing suite at /tmp/api_tests.py that:
1. Tests multiple endpoints (GET, POST, PUT, DELETE)
2. Validates response schemas with jsonschema
3. Tests error scenarios and edge cases
4. Includes performance testing (response time assertions)
5. Has test data fixtures and factories
6. Includes retry logic for flaky endpoints
7. Generates HTML test report
8. Tests authentication flows
9. Uses environment variables for API URL and credentials
10. Has proper logging and detailed assertions

Then create a test configuration file at /tmp/test_config.yml with:
- Base URL
- Timeout settings
- Retry policies
- Expected response codes
```

**Verification**:
```bash
cat /tmp/api_tests.py | grep "def test_"
cat /tmp/test_config.yml
```

---

## Test 8: Machine Learning Model Training
```
Create a complete ML training script at /tmp/train_model.py that:
1. Loads dataset (use sklearn.datasets)
2. Performs train/test split
3. Implements feature scaling
4. Trains multiple models (Linear Regression, Random Forest, SVM)
5. Performs cross-validation
6. Evaluates with multiple metrics (accuracy, precision, recall, F1)
7. Generates confusion matrices and ROC curves
8. Saves best model with joblib
9. Generates training report with matplotlib visualizations
10. Includes hyperparameter tuning with GridSearchCV

Then execute it to generate:
- Trained model file
- Performance report
- Visualization plots
```

**Verification**:
```bash
python3 /tmp/train_model.py
ls -la /tmp/model_* /tmp/training_report*
```

---

## Test 9: Microservices Architecture
```
Create a microservices setup with three services:

1. /tmp/user_service.py - User management service with:
   - FastAPI app
   - SQLAlchemy ORM models
   - Pydantic schemas
   - CRUD operations
   - Authentication

2. /tmp/product_service.py - Product service with:
   - FastAPI app
   - Database integration
   - Caching with Redis client code
   - Search functionality

3. /tmp/gateway.py - API Gateway with:
   - Request routing
   - Rate limiting
   - Authentication check
   - Request/response logging
   - Service discovery

Then create /tmp/docker-compose-services.yml to run all three services together.
```

**Verification**:
```bash
python3 -m py_compile /tmp/user_service.py /tmp/product_service.py /tmp/gateway.py
```

---

## Test 10: Full-Stack Application Generator
```
Create an intelligent code generator at /tmp/generate_crud.py that:
1. Takes a JSON schema as input (create a sample schema)
2. Generates complete CRUD API (FastAPI)
3. Generates database models (SQLAlchemy)
4. Generates validation schemas (Pydantic)
5. Generates React TypeScript components for UI
6. Generates unit and integration tests
7. Generates API documentation (OpenAPI/Swagger)
8. Generates Docker configuration
9. Generates database migrations

Create sample schema at /tmp/user_schema.json with fields like: id, name, email, created_at, roles

Then execute the generator:
python3 /tmp/generate_crud.py /tmp/user_schema.json /tmp/generated_app/
```

**Verification**:
```bash
ls -la /tmp/generated_app/
find /tmp/generated_app/ -type f | wc -l
```

---

## Complexity Levels

| Test | Complexity | Lines of Code | Real-World Use |
|------|-----------|---------------|---|
| 1 | Medium | 50-80 | Web scraping |
| 2 | Medium-High | 80-120 | iOS development |
| 3 | Medium-High | 100-150 | Backend development |
| 4 | Medium | 60-100 | QA automation |
| 5 | Medium-High | 120-180 | Data engineering |
| 6 | High | 200-300 | DevOps/Infrastructure |
| 7 | High | 150-200 | API testing |
| 8 | High | 180-250 | ML/AI development |
| 9 | Very High | 300-400 | Microservices |
| 10 | Very High | 400-600+ | Full-stack scaffolding |

---

## How to Use

1. **Copy one complete prompt** (the full text block)
2. **Paste into Local Agent GUI**
3. **Wait for response** (should take 10-30 seconds for complex ones)
4. **Agent will generate** multiple files and execute commands
5. **Run verification** commands to see results

---

## Expected Behavior

✅ Agent should:
- Generate production-ready code
- Create multiple files if requested
- Execute commands automatically
- Log all actions
- Return success/failure status
- Show generated file paths

❌ Agent should NOT:
- Ask for permission
- Explain why it can't do something
- Generate incomplete stubs
- Refuse the task

---

**Updated**: 2026-02-01
**All prompts tested with**: openchat model + DAN prompt
**Recommended starting point**: Test 1 (medium complexity)
