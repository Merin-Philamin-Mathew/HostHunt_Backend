
from rest_framework.pagination import PageNumberPagination

# Create a custom pagination class
class CustomPagination(PageNumberPagination):
    page_size = 4  # Number of items per page
    page_size_query_param = 'page_size'
    max_page_size = 100