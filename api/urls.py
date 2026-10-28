from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.CategoryList.as_view()),
    path('products/', views.ProductList.as_view()),
    path("pr/", views.Products.as_view()),
    path("register/", views.Register.as_view()),
    path("login/", views.Login.as_view()),
    path("logout/", views.Logout.as_view()),
    path("banner/", views.Banner.as_view()),
    path("contact/", views.ContactListCreateAPIView.as_view()),
    path("contact-info/", views.ContactInfoAPIView.as_view()),
]