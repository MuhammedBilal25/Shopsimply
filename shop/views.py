from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView,ListAPIView,RetrieveAPIView
from rest_framework import authentication,permissions

from shop.serializers import UserSerializer,ProductSerializer
from django.contrib.auth.models import User
from shop.models import Product


# Create your views here.

class SignUpView(CreateAPIView):
    serializer_class=UserSerializer
    queryset=User.objects.all()

class ProductListView(ListAPIView):
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    serializer_class=ProductSerializer
    queryset=Product.objects.all()

class ProductDetailView(RetrieveAPIView):
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    serializer_class=ProductSerializer
    queryset=Product.objects.all()

    
