from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from . import models, serializer
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .tasks import send_telegram_message


class LogoutAnonThrottle(AnonRateThrottle):
    rate = '5/min'


class LogoutUserThrottle(UserRateThrottle):
    rate = '15/min'


class CategoryList(APIView):
    def get(self, request):
        categories = models.Category.objects.all()
        categories_sr = serializer.CategorySerializer(categories, many=True)
        return Response(categories_sr.data)

    def post(self, request):
        name = request.data.get('name')
        description = request.data.get('description')
        image = request.data.get('image')
        is_home = request.data.get('is_home')
        category = models.Category.objects.create(
            name=name,
            description=description,
            image=image,
            is_home=is_home
        )
        data = {
            "category": serializer.CategorySerializer(category).data
        }
        send_telegram_message(
            chat_id=5427482207,
            message=str(data)
        )
        return Response(data)


class ProductList(APIView):
    def get(self, request):
        data = cache.get("products")
        if not data:
            products = models.Product.objects.all()
            cat = request.query_params.get('c')
            search = request.query_params.get("s")
            price = request.query_params.get("p")
            if cat:
                products = products.filter(category=cat)
            if search:
                products = products.filter(Q(name__icontains=search) | Q(description__icontains=search))
            if price:
                products = products.filter(price=price)

            data = {
                "products": serializer.ProductSerializer(products, many=True).data,
            }
            cache.set("products", data, 60 * 3)
            print("bazdan")
        else:
            print("redisdan")
        return Response(data)


class Banner(APIView):
    def get(self, request):
        banner = models.Banner.objects.all()
        banner_serializer = serializer.BannerSerializer(banner, many=True)
        data = {
            'banners': banner_serializer.data
        }
        return Response(data)


class ContactInfoAPIView(APIView):
    def get(self, request):
        contact_info = models.ContactInfo.objects.first()  # Model nomi ishlatildi
        if not contact_info:
            return Response({"message": "Ma'lumot topilmadi."}, status=status.HTTP_404_NOT_FOUND)
        contact_info_serializer = serializer.ContactInfoSerializer(contact_info)
        return Response(contact_info_serializer.data)


class ContactListCreateAPIView(APIView):
    def get(self, request):
        contacts = models.Contact.objects.all()  # Model nomi ishlatildi
        contacts_serializer = serializer.ContactSerializer(contacts, many=True)
        return Response(contacts_serializer.data)


class CustomPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = "size"
    max_page_size = 100


class Products(generics.ListAPIView):
    queryset = models.Product.objects.all()
    serializer_class = serializer.ProductSerializer
    pagination_class = CustomPagination

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    ordering_fields = ['price']
    search_fields = ['name', 'description']
    filterset_fields = ['category']


# ------------------AUTH------------------
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token


class Register(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        password2 = request.data.get('password2')

        if password != password2:
            return Response({'error': 'parollar mos emas'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password)
        token = Token.objects.create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)


class Login(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Bunday foydalanuvchi mavjud emas'}, status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    throttle_classes = [LogoutAnonThrottle, LogoutUserThrottle]
    
    def post(self, request):
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response({'message': 'logout'}, status=status.HTTP_200_OK)


