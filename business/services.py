from calendar import mdays

from django.utils import timezone
from django.conf import settings

from core.utils import client_timezone
from elasticsearch_client import es


class ReportManagement:
    DAY_OF_WEEK = {
        "1": "T2",
        "2": "T3",
        "3": "T4",
        "4": "T5",
        "5": "T6",
        "6": "T7",
        "7": "CN"
    }
    TOP_PRODUCT_MAPPINGS = {
        "revenue": "Doanh thu",
        "quantity": "Số lượng"
    }
    time_format = "%Y-%m-%d"

    def __init__(self, request):
        self.request = request

    def get_revenue_aggregations(self):
        time = self.request.GET.get("time", "today")
        group_by = self.request.GET.get("groupBy", "day")
        from_time, to_time = self.__get_time(time)

        scripts = es.build_revenue_aggregation_scripts(group_name=group_by,
                                                       timezone=settings.TIME_ZONE,
                                                       from_time=from_time,
                                                       to_time=to_time)
        filter_path = ["aggregations"]
        response = es.search(script=scripts, index="invoice", filter_path=filter_path)
        buckets = response["aggregations"][group_by]["buckets"]
        labels = []
        data = []
        for bucket in buckets:
            labels.append(bucket["key"])
            data.append(bucket["revenue"]["value"])
        labels = self._rich_labels_func(group_by)(labels)
        print(labels, data)
        return {
            "labels": labels,
            "data": data,
            "total": response["aggregations"]["total_revenue"]["value"]
        }

    def get_top_product_aggregations(self):
        time = self.request.GET.get("time", "today")
        group_by = self.request.GET.get("groupBy", "day")
        from_time, to_time = self.__get_time(time)
        scripts = es.build_top_product_aggregation_scripts(group_name=group_by,
                                                           timezone=settings.TIME_ZONE,
                                                           from_time=from_time,
                                                           to_time=to_time)
        filter_path = ["aggregations"]
        response = es.search(script=scripts, index="product_item", filter_path=filter_path)
        print(response)
        buckets = response["aggregations"][group_by]["buckets"]
        labels = []
        data = []
        for bucket in buckets:
            labels.append(bucket["product_name"]["hits"]["hits"][0]["_source"]["product_name"])
            data.append(bucket["total"]["value"])
        # print("top product: ", labels, data)
        return {
            "labels": labels,
            "data": data,
            "bar_label": self.TOP_PRODUCT_MAPPINGS[group_by]
        }

    def get_data_aggregations(self):
        aggs_type = self.request.GET.get("type")
        if aggs_type == "revenue":
            return self.get_revenue_aggregations()
        elif aggs_type == "topProduct":
            return self.get_top_product_aggregations()

    def __get_time(self, time):
        now = client_timezone(timezone.now())

        if time == "today":
            begin = now.strftime(self.time_format)
            end = (now + timezone.timedelta(days=1)).strftime(self.time_format)
        elif time == "yesterday":
            begin = (now - timezone.timedelta(days=1)).strftime(self.time_format)
            end = now.strftime(self.time_format)
        elif time == "week":
            begin_of_week = now - timezone.timedelta(days=now.weekday())
            begin = begin_of_week.strftime(self.time_format)
            end = (begin_of_week + timezone.timedelta(days=6)).strftime(self.time_format)
        elif time == "month":
            begin = now.strftime("%Y-%m-01")
            end = (now + timezone.timedelta(days=mdays[now.month])).strftime("%Y-%m-01")
        elif time == "lastweek":
            begin_of_week = now - timezone.timedelta(days=now.weekday())
            begin = (begin_of_week - timezone.timedelta(days=7)).strftime(self.time_format)
            end = begin_of_week.strftime(self.time_format)
        elif time == "lastmonth":
            begin = (now - timezone.timedelta(days=mdays[now.month])).strftime("%Y-%m-01")
            end = now.strftime("%Y-%m-01")

        print(begin, end)
        return begin, end

    def __rich_labels_day(self, labels):
        return labels

    def __rich_labels_hour(self, labels):
        rich_labels = []
        for label in labels:
            rich_labels.append(label + ":00")
        return rich_labels

    def __rich_labels_dayofweek(self, labels):
        rich_labels = []
        for label in labels:
            rich_labels.append(self.DAY_OF_WEEK[label])
        return rich_labels

    def _rich_labels_func(self, group_by):
        if group_by == "day":
            return self.__rich_labels_day
        elif group_by == "hour":
            return self.__rich_labels_hour
        elif group_by == "dayofweek":
            return self.__rich_labels_dayofweek

