from elasticsearch import Elasticsearch

DEFAULT = 1
es = Elasticsearch([{"host": "localhost", "port": 9200, "timeout": 60}])

default_settings = {
    "index": {
        "number_of_shards": 1,
        "number_of_replicas": 1,
    }
}



invoice_index_settings = {
    "settings": default_settings,
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "store_id": {"type": "keyword"},
            "invoice_code": {"type": "keyword"},
            "time_created": {"type": "date"},
            "total": {"type": "integer"},
            "total_product": {"type": "integer"},
            "staff": {"type": "keyword"},
            "order_id": {"type": "integer"},
            "status": {"type": "integer"},
        }
    }
}

product_item_index_settings = {
    "settings": default_settings,
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "store_id": {"type": "keyword"},
            "order_id": {"type": "keyword"},
            "product_id": {"type": "keyword"},
            "product_name": {"type": "string", "index": "not_analyzed"},
            "quantity": {"type": "integer"},
            "price": {"type": "integer"}
        }
    }
}

product_index_setting = {
    "settings": default_settings,
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "store_id": {"type": "keyword"},
            "barcode": {"type": "keyword"},
            "product_code": {"type": "keyword"},
            "product_name": {"type": "string"},
            "description": {"type": "string"},
            "cost_price": {"type": "integer"},
            "sell_price": {"type": "integer"},
            "unit": {"type": "string", "index": "not_analyzed"},
            "status": {"type": "integer"},
            "category_id": {"type": "keyword"},
        }
    }
}


def init():
    if not es.indices.exists(index='invoice'):
        es.indices.create(index='invoice', body=invoice_index_settings)
    if not es.indices.exists(index='product_item'):
        es.indices.create(index='product_item', body=product_item_index_settings)
    if not es.indices.exists(index='product'):
        es.indices.create(index='product', body=product_index_setting)


def index_invoice(invoice_id, invoice_code, total, total_product,
                  time_created, staff, order_id, status, store_id=DEFAULT, **kwargs):
    body = {
        "id": invoice_id,
        "store_id": store_id,
        "invoice_code": invoice_code,
        "time_created": time_created,
        "total": total,
        "total_product": total_product,
        "staff": staff,
        "order_id": order_id,
        "status": status
    }
    body.update(kwargs)
    return es.index(index="invoice", body=body, id=invoice_id)


def index_product_item(pid, order_id, product_id, product_name, quantity,
                       price, store_id=DEFAULT, **kwargs):
    body = {
        "id": pid,
        "store_id": store_id,
        "order_id": order_id,
        "product_id": product_id,
        "product_name": product_name,
        "quantity": quantity,
        "price": price,
    }
    body.update(kwargs)
    return es.index(index="product_item", body=body, id=pid)


def index_product(pid, barcode, product_code, product_name, description, cost_price,
                  sell_price, unit, status, category_id, store_id=DEFAULT, **kwargs):
    body = {
        "id": pid,
        "barcode": barcode,
        "product_code": product_code,
        "product_name": product_name,
        "description": description,
        "cost_price": cost_price,
        "sell_price": sell_price,
        "unit": unit,
        "status": status,
        "category_id": category_id,
        "store_id": store_id,
    }
    body.update(kwargs)
    return es.index(index="product", body=body, id=pid)


def search(script, index, filter_path=None):
    return es.search(body=script, index=index, filter_path=filter_path)


def invoice_delete(doc_id):
    es.delete(index="invoice", id=doc_id)


def product_item_delete(doc_id):
    es.delete(index="product_item", id=doc_id)


def product_delete(doc_id):
    es.delete(index="product", id=doc_id)
