from django.conf import settings
from elasticsearch import Elasticsearch, helpers

from core.utils import server_timezone

DEFAULT = 1
es = Elasticsearch([{"host": "localhost", "port": 9200, "timeout": 60}])

default_settings = {
    "index": {
        "number_of_shards": 1,
        "number_of_replicas": 1,
    },
    "analysis": {
        "filter": {  # https://www.elastic.co/guide/en/elasticsearch/guide/current/_index_time_search_as_you_type.html
            "autocomplete_filter": {
                "type": "edge_ngram",
                "min_gram": 1,
                "max_gram": 10
            }
        },
        "analyzer": {
            "my_analyzer": {
                "tokenizer": "standard",
                "filter": ["lowercase", "asciifolding", "autocomplete_filter"]
                # example for filter:
                # "Tôi yêu Việt Nam"
                # lowercase: tôi yêu việt nam
                # asciifolding: toi yeu vietnam
                # autocomplete_filter: analyze to terms: t, to, toi, y, ye, yeu ...
            }
        }
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
            "total_product": {"type": "float"},
            "staff": {"type": "keyword"},
            "order_id": {"type": "integer"},
            "status": {"type": "integer"},
            "customer_id": {"type": "integer"},
        }
    }
}

product_item_index_settings = {
    "settings": default_settings,
    "mappings": {
        "properties": {
            "store_id": {"type": "keyword"},
            "order_id": {"type": "keyword"},
            "product_id": {"type": "keyword"},
            "product_name": {"type": "keyword"},
            "quantity": {"type": "float"},
            "price": {"type": "integer"},
            "cost_price": {"type": "integer"},
            "time_created": {"type": "date"}
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
            "product_name": {"type": "text", "analyzer": "my_analyzer"},
            "description": {"type": "text", "analyzer": "my_analyzer"},
            "cost_price": {"type": "integer"},
            "sell_price": {"type": "integer"},
            "unit": {"type": "keyword"},
            "status": {"type": "integer"},
            "category_id": {"type": "keyword"},
        }
    }
}

customer_index_settings = {
    "settings": default_settings,
    "mappings": {
        "properties": {
            "id": {"type": "integer"},
            "store_id": {"type": "integer"},
            "customer_code": {"type": "keyword"},
            "customer_name": {"type": "text", "analyzer": "my_analyzer"},
            "phone_number": {"type": "keyword"},
            "email": {"type": "keyword"},
            "address": {"type": "text", "analyzer": "my_analyzer"},
            "group_type": {"type": "integer"}
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
    if not es.indices.exists(index='customer'):
        es.indices.create(index='customer', body=customer_index_settings)


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
                       price, time_created, store_id=DEFAULT, **kwargs):
    body = {
        "id": pid,
        "store_id": store_id,
        "order_id": order_id,
        "product_id": product_id,
        "product_name": product_name,
        "quantity": quantity,
        "price": price,
        "time_created": time_created
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


def index_customer(customer_id, customer_code, customer_name, group_type, store_id=DEFAULT, **kwargs):
    body = {
        "id": customer_id,
        "customer_code": customer_code,
        "customer_name": customer_name,
        "store_id": store_id,
        "group_type": group_type
    }
    body.update(kwargs)
    return es.index(index="customer", body=body, id=customer_id)


def bulk_index_product_item(list_product_items, store_id=DEFAULT):
    actions = [
        {
            "_index": "product_item",
            "_id": item.id,
            "_source": {
                "id": item.id,
                "store_id": store_id,
                "order_id": item.order.id,
                "product_id": item.product.id,
                "product_name": item.product.product_name,
                "quantity": item.quantity,
                "price": item.price,
                "time_created": item.order.time_create
            }
        }
        for item in list_product_items
    ]
    helpers.bulk(es, actions)


def search(script, index, filter_path=None):
    return es.search(body=script, index=index, filter_path=filter_path)


def invoice_delete(doc_id):
    es.delete(index="invoice", id=doc_id)


def product_item_delete(doc_id):
    es.delete(index="product_item", id=doc_id)


def product_delete(doc_id):
    es.delete(index="product", id=doc_id)


def build_revenue_aggregation_scripts(group_name, timezone, from_time, to_time, store_id=DEFAULT):
    if group_name == "day":
        script = {
            "lang": "painless",
            "source": "doc['time_created'].value.withZoneSameInstant(ZoneId.of("
                      "'{timezone}')).getDayOfMonth()".format(timezone=timezone)
        }
    elif group_name == "hour":
        script = {
            "lang": "painless",
            "source": "doc['time_created'].value.withZoneSameInstant(ZoneId.of("
                      "'{timezone}')).getHour()".format(timezone=timezone)
        }
    elif group_name == "dayofweek":
        script = {
            "lang": "painless",
            "source": "doc['time_created'].value.withZoneSameInstant(ZoneId.of("
                      "'{timezone}')).getDayOfWeek().getValue()".format(timezone=timezone)
        }
    script_template = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"store_id": store_id}},
                    {"term": {"status": 1}}
                ],
                "filter": {
                    "range": {
                        "time_created": {
                            "gte": from_time,
                            "lt": to_time,
                            "time_zone": timezone
                        }
                    }
                }
            }
        },
        "size": 0,
        "aggs": {
            group_name: {
                "terms": {
                    "script": script,
                    "order": {
                        "_key": "asc"
                    },
                    "min_doc_count": 1
                },
                "aggs": {
                    "revenue": {
                        "sum": {
                            "field": "total"
                        }
                    },
                    "total_product": {
                        "sum": {
                            "field": "total_product"
                        }
                    }
                }
            },
            "total_revenue": {
                "sum": {"field": "total"}
            }
        }
    }
    return script_template


def build_top_product_aggregation_scripts(group_name, timezone, from_time, to_time, store_id=DEFAULT):
    if group_name == "revenue":
        sum_scripts = {"script": "doc['price'].value * doc['quantity'].value"}
    elif group_name == "quantity":
        sum_scripts = {"field": "quantity"}
    script_template = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"store_id": store_id}}
                ],
                "filter": {
                    "range": {
                        "time_created": {
                            "gte": from_time,
                            "lt": to_time,
                            "time_zone": timezone
                        }
                    }
                }
            }
        },
        "size": 0,
        "aggs": {
            group_name: {
                "terms": {
                    "field": "product_id",
                    "size": 10,
                    "order": {"total.value": "desc"}
                },
                "aggs": {
                    "total": {
                        "sum": sum_scripts
                    },
                    "product_name": {
                        "top_hits": {
                            "sort": [{"time_created": {"order": "desc"}}],
                            "_source": ["product_name"],
                            "size": 1
                        }
                    }
                }
            }
        }
    }
    return script_template


def aggregate_sales_today(yesterday, today_begin, today, last_month_begin, last_month,
                          timezone=settings.TIME_ZONE, store_id=DEFAULT):
    script = {
        "query": {"bool": {"must": [
            {"term": {"store_id": store_id}},
            {"term": {"status": 1}}
        ]}},
        "size": 0,
        "aggs": {
            "yesterday_today": {
                "filter": {"range": {"time_created": {"gte": yesterday, "lte": today, "time_zone": timezone}}},
                "aggs": {
                    "group_by_day": {
                        "date_histogram": {
                            "field": "time_created",
                            "calendar_interval": "day",
                            "min_doc_count": 0,
                            "extended_bounds": {
                                "min": yesterday,
                                "max": today
                            },
                            "time_zone": timezone,
                            "order": {
                                "_key": "asc"
                            }
                        },
                        "aggs": {"group_by_fees": {"sum": {"field": "total"}}}
                    }
                }
            },
            "lastmonth": {
                "filter": {
                    "range": {"time_created": {"gte": last_month_begin, "lte": last_month, "time_zone": timezone}}
                },
                "aggs": {"group_by_fees": {"sum": {"field": "total"}}}
            },
            "now": {
                "filter": {
                    "range": {"time_created": {"gte": today_begin, "lte": today, "time_zone": timezone}}
                },
                "aggs": {"group_by_fees": {"sum": {"field": "total"}}}
            }
        }
    }
    filter_path = ["aggregations"]
    res = search(script, index="invoice", filter_path=filter_path)
    yesterday_today = res["aggregations"]["yesterday_today"]
    last_month = res["aggregations"]["lastmonth"]
    now = res["aggregations"]["now"]
    print(res)
    return {
        "yesterday": {
            "total_invoices": yesterday_today["group_by_day"]["buckets"][0]["doc_count"],
            "revenue": int(yesterday_today["group_by_day"]["buckets"][0]["group_by_fees"]["value"])
        },
        "today": {
            "total_invoices": yesterday_today["group_by_day"]["buckets"][1]["doc_count"],
            "revenue": int(yesterday_today["group_by_day"]["buckets"][1]["group_by_fees"]["value"])
        },
        "lastmonth": {
            "total_invoices": last_month["doc_count"],
            "revenue": int(last_month["group_by_fees"]["value"])
        },
        "now": {
            "total_invoices": now["doc_count"],
            "revenue": int(now["group_by_fees"]["value"])
        }
    }


def search_customer(key, store_id=DEFAULT):
    query = {
        "query": {
            "dis_max": {
                "tie_breaker": 0.7,
                "boost": 1.2,
                "queries": [
                    {
                        "match": {"store_id": store_id}
                    },
                    {
                        "match": {
                            "customer_name": key
                        }
                    },
                    {
                        "match": {
                            "address": key
                        }
                    },
                    {
                        "wildcard": {
                            "phone_number": "*%s*" % key.upper()
                        }
                    },
                    {
                        "wildcard": {
                            "customer_code": {
                                "value": "*%s*" % key
                            }
                        }
                    }
                ]
            }
        }
    }
    filter_path = ["hits"]
    return search(script=query, index="customer", filter_path=filter_path)


def update_invoice_status(invoice_id, new_status):
    body = {
        "script": {
            "source": "ctx._source.status=params.new_status",
            "lang": "painless",
            "params": {
                "new_status": new_status
            }
        }
    }
    es.update(index="invoice", id=invoice_id, body=body)
