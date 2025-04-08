# Recipe API

A serverless Recipe API built with AWS SAM, Python, and DynamoDB.

## Features

- RESTful API for managing recipes
- Serverless architecture using AWS Lambda
- DynamoDB for data storage
- Structured logging with structlog
- API Key authentication
- Pagination support

## Prerequisites

- Python 3.12
- Poetry for dependency management
- AWS SAM CLI
- AWS CLI configured with credentials

## Project Structure

```
.
├── app.py                  # Lambda handler and route definitions
├── internal/
│   ├── controllers/        # Request handlers
│   └── repository/         # DynamoDB operations
├── template.yaml           # SAM template
├── build.sh               # Dependency packaging script
└── pyproject.toml         # Poetry dependencies
```

## Setup

1. Install dependencies:
```bash
make install
```

2. Build Python dependencies layer:
```bash
make build
```

3. Deploy to AWS:
```bash
make deploy
```

## API Endpoints

### Recipes

- `GET /recipes` - List all recipes (supports pagination)
- `POST /recipes` - Create a new recipe
- `GET /recipes/{id}` - Get a specific recipe
- `PUT /recipes/{id}` - Update a recipe
- `DELETE /recipes/{id}` - Delete a recipe

### Hello

- `GET /hello` - Health check endpoint

## Development

### Local Testing

Run the API locally:
```bash
sam local start-api
```

### Logging

The API uses structlog for structured logging. Logs are formatted as JSON and include:
- Timestamps
- Log levels
- Request IDs
- Operation context
- Error details

### Error Handling

Errors are handled at the Lambda handler level and return appropriate HTTP status codes:
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

## Deployment

The application is deployed using AWS SAM with:
- API Gateway
- Lambda functions
- DynamoDB table
- S3 bucket for deployment artifacts

## License

MIT 