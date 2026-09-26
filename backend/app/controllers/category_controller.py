from flask import jsonify, request

from app.services.category_service import CategoryService
from app.decorators import roles_required

def list_categories():
    categories = CategoryService.get_all()

    return jsonify(
        {
            "data": [
                category.to_dict()
                for category in categories
            ],
            "count": len(categories),
        }
    ), 200


def get_category(category_id):
    category = CategoryService.get_by_id(category_id)

    if category is None:
        return jsonify(
            {
                "error": "La categoría no existe.",
            }
        ), 404

    return jsonify(
        {
            "data": category.to_dict(),
        }
    ), 200

@roles_required("ADMINISTRADOR")
def create_category():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            {
                "error": "Debe enviar un objeto JSON válido.",
            }
        ), 400

    try:
        category = CategoryService.create(data)
    except ValueError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 400
    except FileExistsError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 409

    return jsonify(
        {
            "message": "Categoría creada correctamente.",
            "data": category.to_dict(),
        }
    ), 201

@roles_required("ADMINISTRADOR")
def update_category(category_id):
    category = CategoryService.get_by_id(category_id)

    if category is None:
        return jsonify(
            {
                "error": "La categoría no existe.",
            }
        ), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            {
                "error": "Debe enviar un objeto JSON válido.",
            }
        ), 400

    try:
        category = CategoryService.update(category, data)
    except ValueError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 400
    except FileExistsError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 409

    return jsonify(
        {
            "message": "Categoría actualizada correctamente.",
            "data": category.to_dict(),
        }
    ), 200


@roles_required("ADMINISTRADOR")
def delete_category(category_id):
    category = CategoryService.get_by_id(category_id)

    if category is None:
        return jsonify(
            {
                "error": "La categoría no existe.",
            }
        ), 404

    category = CategoryService.deactivate(category)

    return jsonify(
        {
            "message": "Categoría desactivada correctamente.",
            "data": category.to_dict(),
        }
    ), 200