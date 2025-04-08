import json
from typing import Any, Callable, Dict

import structlog

from src.controllers.recipes import RecipeController
from src.repository.dynamodb import DynamoDBRepository

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

# Get logger
logger = structlog.get_logger()

# Initialize repository and controller
repository = DynamoDBRepository()
controller = RecipeController(repository)


def get_recipe(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Get a recipe by ID."""
    logger.info(
        "handling_get_recipe_request",
        recipe_id=event["pathParameters"]["id"],
        request_id=event["requestContext"]["requestId"],
    )
    try:
        recipe_id = event["pathParameters"]["id"]
        response = controller.get_recipe(recipe_id)
        logger.info(
            "successfully_retrieved_recipe",
            recipe_id=recipe_id,
            status_code=response["statusCode"],
        )
        return {
            "statusCode": response["statusCode"],
            "body": json.dumps(response["body"]),
        }
    except Exception as e:
        logger.exception(
            "error_retrieving_recipe",
            recipe_id=event["pathParameters"]["id"],
            error=str(e),
            exc_info=True,
        )
        raise


def create_recipe(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Create a new recipe."""
    logger.info(
        "handling_create_recipe_request",
        request_id=event["requestContext"]["requestId"],
    )
    try:
        body = json.loads(event["body"])
        response = controller.create_recipe(body)
        logger.info(
            "successfully_created_recipe",
            recipe_id=response["body"]["id"],
            status_code=response["statusCode"],
        )
        return {
            "statusCode": response["statusCode"],
            "body": json.dumps(response["body"]),
        }
    except Exception as e:
        logger.exception(
            "error_creating_recipe",
            error=str(e),
            request_body=event["body"],
            exc_info=True,
        )
        raise


def update_recipe(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Update an existing recipe."""
    logger.info(
        "handling_update_recipe_request",
        recipe_id=event["pathParameters"]["id"],
        request_id=event["requestContext"]["requestId"],
    )
    try:
        recipe_id = event["pathParameters"]["id"]
        body = json.loads(event["body"])
        response = controller.update_recipe(recipe_id, body)
        logger.info(
            "successfully_updated_recipe",
            recipe_id=recipe_id,
            status_code=response["statusCode"],
        )
        return {
            "statusCode": response["statusCode"],
            "body": json.dumps(response["body"]),
        }
    except Exception as e:
        logger.exception(
            "error_updating_recipe",
            recipe_id=event["pathParameters"]["id"],
            error=str(e),
            exc_info=True,
        )
        raise


def delete_recipe(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Delete a recipe by ID."""
    logger.info(
        "handling_delete_recipe_request",
        recipe_id=event["pathParameters"]["id"],
        request_id=event["requestContext"]["requestId"],
    )
    try:
        recipe_id = event["pathParameters"]["id"]
        response = controller.delete_recipe(recipe_id)
        logger.info(
            "successfully_deleted_recipe",
            recipe_id=recipe_id,
            status_code=response["statusCode"],
        )
        return {
            "statusCode": response["statusCode"],
            "body": json.dumps(response["body"]),
        }
    except Exception as e:
        logger.exception(
            "error_deleting_recipe",
            recipe_id=event["pathParameters"]["id"],
            error=str(e),
            exc_info=True,
        )
        raise


def list_recipes(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """List all recipes with pagination support."""
    logger.info(
        "handling_list_recipes_request",
        request_id=event["requestContext"]["requestId"],
    )
    try:
        query_params = event.get("queryStringParameters", {})
        if query_params in [None, "null"]:
            query_params = {}

        last_evaluated_key = query_params.get("last_evaluated_key")
        response = controller.list_recipes(last_evaluated_key)
        logger.info(response)
        logger.info(
            "successfully_listed_recipes",
            count=len(response["body"]["data"]),
            status_code=response["statusCode"],
        )
        return {
            "statusCode": response["statusCode"],
            "body": json.dumps(response["body"]),
        }
    except Exception as e:
        logger.exception(
            "error_listing_recipes",
            error=str(e),
            exc_info=True,
        )
        raise


def hello(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Health check endpoint."""
    logger.info(
        "handling_hello_request",
        request_id=event["requestContext"]["requestId"],
    )
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Hello from Recipe API!"}),
    }


# Define route map
ROUTE_MAP: Dict[str, Dict[str, Callable]] = {
    "/hello": {"GET": hello},
    "/recipes": {"GET": list_recipes, "POST": create_recipe},
    "/recipes/{id}": {
        "GET": get_recipe,
        "PUT": update_recipe,
        "DELETE": delete_recipe,
    },
}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler for the Recipe API."""
    try:
        # Log incoming request
        logger.info(
            "received_request",
            path=event["path"],
            method=event["httpMethod"],
            request_id=event["requestContext"]["requestId"],
        )

        # Extract HTTP method and path
        http_method = event["httpMethod"]
        path = event["path"]

        # Find matching route handler
        for route_path, methods in ROUTE_MAP.items():
            if path == route_path or path.startswith(route_path.replace("{id}", "")):
                if http_method in methods:
                    return methods[http_method](event, context)

        # If no matching route found
        logger.warning(
            "route_not_found",
            path=path,
            method=http_method,
        )
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "Not Found"}),
        }

    except Exception as e:
        logger.exception(
            "unhandled_error_in_lambda_handler",
            error=str(e),
            path=event.get("path"),
            method=event.get("httpMethod"),
            exc_info=True,
        )
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }
