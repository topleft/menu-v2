import json
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

import boto3


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling Decimal types."""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DecimalEncoder, self).default(obj)


class DynamoDBRepository:
    """Repository for DynamoDB operations."""

    def __init__(self, table_name: str = "recipes"):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)

    def list_recipes(self, last_evaluated_key: Optional[str] = None) -> Dict[str, Any]:
        """List all recipes with pagination support."""
        scan_kwargs = {}
        if last_evaluated_key:
            scan_kwargs["ExclusiveStartKey"] = json.loads(last_evaluated_key)

        response = self.table.scan(**scan_kwargs)

        return {
            "items": json.loads(
                json.dumps(response.get("Items", []), cls=DecimalEncoder)
            ),
            "last_evaluated_key": json.dumps(
                response.get("LastEvaluatedKey"), cls=DecimalEncoder
            )
            if response.get("LastEvaluatedKey")
            else None,
        }

    def get_recipe(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """Get a recipe by ID."""
        response = self.table.get_item(Key={"id": recipe_id})
        return response.get("Item")

    def create_recipe(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new recipe."""
        self.table.put_item(Item=recipe_data)
        return recipe_data

    def update_recipe(
        self, recipe_id: str, recipe_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an existing recipe."""
        # Remove id from update as it's the key
        update_data = {k: v for k, v in recipe_data.items() if k != "id"}

        update_expression = "SET " + ", ".join(
            [f"#{k} = :{k}" for k in update_data.keys()]
        )
        expression_attribute_names = {f"#{k}": k for k in update_data.keys()}
        expression_attribute_values = {f":{k}": v for k, v in update_data.items()}

        response = self.table.update_item(
            Key={"id": recipe_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW",
        )
        return response.get("Attributes")

    def delete_recipe(self, recipe_id: str) -> bool:
        """Delete a recipe by ID."""
        response = self.table.delete_item(Key={"id": recipe_id}, ReturnValues="ALL_OLD")
        return "Attributes" in response
