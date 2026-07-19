import django_filters
from apps.lms.models import LiveClass

class LiveClassFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    course_id = django_filters.UUIDFilter(field_name="course_id")
    teacher_id = django_filters.UUIDFilter(field_name="teacher_id")

    class Meta:
        model = LiveClass
        fields = ["status", "course_id", "teacher_id"]
