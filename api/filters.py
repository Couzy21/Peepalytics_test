import django_filters
from .models import Payment


class PaymentFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status", lookup_expr="icontains")
    start_date = django_filters.IsoDateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    end_date = django_filters.IsoDateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = Payment
        fields = ["created_at", "status"]
