from typing import Any, Dict, Optional

from src.repository.dynamodb import DynamoDBRepository


class RecipeController:
    def __init__(self, repository: DynamoDBRepository):
        self.repository = repository

    def list_recipes(self, last_evaluated_key: Optional[str] = None) -> Dict[str, Any]:
        recipes = self.repository.list_recipes(last_evaluated_key)
        return {
            "statusCode": 200,
            "body": {
                "data": recipes.get("items", []),
                "metadata": {"last_evaluated_key": recipes.get("last_evaluated_key")},
            },
        }

    def get_recipe(self, recipe_id: str) -> Dict[str, Any]:
        recipe = self.repository.get_recipe(recipe_id)
        if not recipe:
            return {"statusCode": 404, "body": {"errors": ["Recipe not found"]}}
        return {"statusCode": 200, "body": recipe}

    def create_recipe(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        recipe = self.repository.create_recipe(recipe_data)
        return {"statusCode": 201, "body": recipe}

    def update_recipe(
        self, recipe_id: str, recipe_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        recipe = self.repository.update_recipe(recipe_id, recipe_data)
        if not recipe:
            return {"statusCode": 404, "body": {"errors": ["Recipe not found"]}}
        return {"statusCode": 200, "body": recipe}

    def delete_recipe(self, recipe_id: str) -> Dict[str, Any]:
        self.repository.delete_recipe(recipe_id)
        return {"statusCode": 204, "body": None}
