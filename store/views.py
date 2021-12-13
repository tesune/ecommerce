from typing import ItemsView
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, request
from django.core.mail import BadHeaderError, send_mail
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from store.forms import NewUserForm
from . utils import cookieCart, cartData, guestOrder
from . models import *
import datetime
import json

# Create your views here.
def home(request):   
    data = cartData(request)
    cartItems = data['cartItems']  
    context = {'cartItems':cartItems}
    return render(request, 'store/home.html', context)

def store(request):
    data = cartData(request)
    cartItems = data['cartItems'] 
    products = Product.objects.all()
    context = {'products':products, 'cartItems':cartItems}
    return render(request, 'store/store.html', context)
    
def product_detail(request, id):   
    data = cartData(request)
    cartItems = data['cartItems'] 
    
    products = Product.objects.get(id =id)
    context = {'products':products, 'cartItems':cartItems}
    return render(request, 'store/product_detail.html', context)
    
def cart(request): 
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']  
    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']   
    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html', context)

# captcha for enquiry page
def enquiry(request):  
    captcha_token = request.POST.get("g-recaptcha-response")
    print("Captcha Token:"+request.POST.get("g-recaptcha-response" ))
    cap_url = "https://www.google.com/recaptcha/api/siteverify"
    cap_secret="6LeRR5QdAAAAAJR8_gWFPNXReyCOnYZDVEykO0X";
    cap_data = {"secret":cap_secret,"response":captcha_token}
    cap_server_response = request.post(url=cap_url,data=cap_data )
    cap_json=json.loads(cap_server_response.text)
    if cap_json['sucess'] == False:
        messages.error(request, "Invalid Captcha Try Again")
        return HttpResponseRedirect("/")
    
# send mail for enquiry page   
def enquiry(request):  
    
    if request.method == 'POST':   
        subject = request.POST['subject']
        message = request.POST['message']
        from_email = request.POST['from_email']      
        
        if subject and message and from_email:
            try:
                send_mail(subject, message, from_email, ['admin@example.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            messages.success(request,f'Thanks for Contacting !')
            return render(request,'enquiry.html', {'subject':subject})  
        else:
            return render(request,'enquiry.html',{})
          
def enquiry(request):     
    data = cartData(request)
    cartItems = data['cartItems']    
    context = {'cartItems':cartItems}
    return render(request,'store/enquiry.html', context )

def register_request(request):

	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("home")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
            
	return render (request=request, template_name='store/register.html', context={"register_form":form})

def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("home")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="store/login.html", context={"login_form":form})

def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("home")

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
  
    order, created = Order.objects.get_or_create(customer=customer, complete=False) 
    
    #get_or_create - If order exist, it will update quantity instead of add
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product) 
    
    #Python does not provide 'Switch' or 'Case' but 'Elif' is similar
    #This is add and remove action
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)  
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1) 
    orderItem.save()
    
    if orderItem.quantity <= 0:
        orderItem.delete()
        
    return JsonResponse('Item was added', safe=False)  


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)          
    else:
        customer, order = guestOrder(request, data)
        
    total = float(data['form']['total'])
    order.transaction_id = transaction_id
        
    if total == float(order.get_cart_total):
        order.complete = True
    order.save()    
            
    if order.shipping == True:
        ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )                 
    return JsonResponse('Payment Complete !', safe=False)   