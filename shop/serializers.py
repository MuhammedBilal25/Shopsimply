from django.contrib.auth.models import User

from rest_framework import serializers

from shop.models import Product,Category,Brand,Size


class UserSerializer(serializers.ModelSerializer):
    password1=serializers.CharField(write_only=True)
    password2=serializers.CharField(write_only=True)
    class Meta:
        model=User
        fields=["id","username","email","password1","password2","password"]
        read_only_fields=["id","password"]


    def create(self, validated_data):

        password1=validated_data.pop("password1")
        password2=validated_data.pop("password2")
        if password1!=password2:
            raise serializers.ValidationError("password mismatch")
        return User.objects.create_user(**validated_data,password=password1)
    

class CategorySerializers(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=["id","name"]

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model=Brand
        fields=["id","name"]

class SizeSerializers(serializers.ModelSerializer):
    class Meta:
        model=Size
        fields=["id","name"]




    
class ProductSerializer(serializers.ModelSerializer):
    category_object=CategorySerializers(read_only=True)
    # category_object=serializers.StringRelatedField(read_only=True) only for category name
    brand_object=BrandSerializer(read_only=True)
    # brand_object=serializers.StringRelatedField(read_only=True) only for brand name
    size_object=SizeSerializers(read_only=True,many=True)
    # size_object=serializers.StringRelatedField(read_only=True,many=True) only for size name

    class Meta:
        model=Product
        fields="__all__"
