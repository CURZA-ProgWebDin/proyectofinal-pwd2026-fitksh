from flask import jsonify, request

from app.services.product_service import ProductService


def list_products():
    products = ProductService.get_all()

    return jsonify(
        {
            "data": [
                product.to_dict()
                for product in products
            ],
            "count": len(products),
        }
    ), 200


def get_product(product_id):
    product = ProductService.get_by_id(product_id)

    if product is None:
        return jsonify(
            {
                "error": "El producto no existe.",
            }
        ), 404

    return jsonify(
        {
            "data": product.to_dict(),
        }
    ), 200


def create_product():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            {
                "error": "Debe enviar un objeto JSON válido.",
            }
        ), 400

    try:
        product = ProductService.create(data)
    except ValueError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 400

    return jsonify(
        {
            "message": "Producto creado correctamente.",
            "data": product.to_dict(),
        }
    ), 201


def update_product(product_id):
    product = ProductService.get_by_id(product_id)

    if product is None:
        return jsonify(
            {
                "error": "El producto no existe.",
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
        product = ProductService.update(product, data)
    except ValueError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 400

    return jsonify(
        {
            "message": "Producto actualizado correctamente.",
            "data": product.to_dict(),
        }
    ), 200


def delete_product(product_id):
    product = ProductService.get_by_id(product_id)

    if product is None:
        return jsonify(
            {
                "error": "El producto no existe.",
            }
        ), 404

    product = ProductService.deactivate(product)

    return jsonify(
        {
            "message": "Producto desactivado correctamente.",
            "data": product.to_dict(),
        }
    ), 200