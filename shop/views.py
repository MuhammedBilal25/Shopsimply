from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView,ListAPIView,RetrieveAPIView,UpdateAPIView,DestroyAPIView
from rest_framework import authentication,permissions
from rest_framework.views import APIView
from rest_framework import status
from shop.serializers import UserSerializer,ProductSerializer,BasketSerilizer,BasketItemSerilizer,Orderserilizer
from django.contrib.auth.models import User
from shop.models import Product,Size,BasketItem,Order
import razorpay


# Create your views here.
KEY_ID="rzp_test_oCFtiK9xM2H3af"
KEY_SECRET="YWr76dRt69Km2Ld5rcwV5o1J"
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

class AddtoCartView(APIView):

    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]

    def post(self,request,*args,**kwargs):

        basket_object=request.user.cart
        id=kwargs.get("pk")
        product_object=Product.objects.get(id=id)
        size_name=request.data.get("size")
        size_object=Size.objects.get(name=size_name)
        quantity=request.data.get("quantity")
        BasketItem.objects.create(
            basket_object=basket_object,
            product_object=product_object,
            size_object=size_object,
            quantity=quantity
        )
        return Response(data={"message":"created"})
    
class CartListView(APIView):

    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]

    def get(self,request,*args,**kwargs):

        qs=request.user.cart
        serilizer_instance=BasketSerilizer(qs)
        return Response(data=serilizer_instance.data)
    

class CartItemUpdateView(UpdateAPIView,DestroyAPIView):

    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    serializer_class=BasketItemSerilizer
    queryset=BasketItem.objects.all()
    
    def perform_update(self, serializer):
        size_name=self.request.data.get("size_object")
        size_obj=Size.objects.get(name=size_name)
        serializer.save(size_object=size_obj)

class CkeckOutView(APIView):

    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    def post(self,request,*args,**kwargs):
        user_object=request.user
        delivery_address=request.data.get("delivery_address")
        phone=request.data.get("phone")
        pin=request.data.get("pin")
        email=request.data.get("email")
        payment_mode=request.data.get("payment_mode")
        order_instance=Order.objects.create(
            user_object=user_object,
            delivery_address=delivery_address,
            phone=phone,
            pin=pin,
            email=email,
            payment_mode=payment_mode
        )
        cart_items=request.user.cart.basketitems
        for bi in cart_items:
            order_instance.basket_item_objects.add(bi)
            bi.is_order_placed=True
            bi.save()
        if payment_mode=="cod":
            order_instance.save()
            return Response(data={"message":"created"})
        elif payment_mode=="online" and order_instance:
            client= razorpay.Client(auth=(KEY_ID,KEY_SECRET))
            data = { "amount": order_instance.order_total*100, "currency": "INR", "receipt": "order_rcptid_11" }
            payment = client.order.create(data=data)
            order_id=payment.get("id")
            key_id=KEY_ID
            order_total=payment.get("amount")
            user=request.user.username
            data={
                "order_id":order_id,
                "key_id":key_id,
                "order_total":order_total,
                "user":user,
                "phone":phone
            }
            order_instance.order_id=order_id
            order_instance.save()
            return Response(data=data,status=status.HTTP_201_CREATED)


class OrderSummaryListView(ListAPIView):
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    serializer_class=Orderserilizer
    queryset=Order.objects.all()
    def get_queryset(self):
        return Order.objects.filter(user_object=self.request.user)
    
class PaymentVerificationView(APIView):
    
    def post(self,request,*args,**kwargs):

        data=request.data
        client=razorpay.client(auth=(KEY_ID,KEY_SECRET))
        try:
            client.utility.verify_payment_signature(data)
            order_id=data.get('razorpay_order_id')
            order_object=Order.objects.get(order_id=order_id)
            order_object.is_paid=True
            order_object.save()
            return Response(data={"message":"Payment Success"},status=status.HTTP_200_OK)
        except:
            return Response(data={"message":"Payment Failed"},status=status.HTTP_400_BAD_REQUEST)


