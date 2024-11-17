from django.shortcuts import render,redirect,get_object_or_404
from ceramiapp.models import userdetails,category,product,cart,order
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate,login,update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.db.models import Sum
import os
# Create your views here.

def index(request):
    if request.user.is_authenticated:
        current=request.user.id  
        cata=category.objects.all()
        user=userdetails.objects.get(user_id=current)
        items=product.objects.all()
        prod=product.objects.filter(id__in=order.objects.values_list('product', flat=True).distinct())
        return render(request,"index.html",{'category':cata,'product':prod,'items':items,'User':user})
    else:
        cata=category.objects.all()
        items=product.objects.all()
        prod=product.objects.filter(id__in=order.objects.values_list('product', flat=True).distinct())
        return render(request,"index.html",{'category':cata,'product':prod,'items':items})
    

def loginpage(request):
    cata=category.objects.all()
    return render(request,"Login.html",{'category':cata})

def loginuser(request):
    if request.method == 'POST':
        user=request.POST['username']
        pwd=request.POST['password']
        usr1=auth.authenticate(username=user, password=pwd)
        if usr1 is not None:
            if usr1.is_staff:
                login(request,usr1)
                return redirect('adminhome')
            else:
                login(request,usr1)
                auth.login(request,usr1)
                return redirect('index') 
        else:
            messages.info(request,'Invalid Username or Password!. Try again')
            return redirect('loginpage')
    else:
        messages.info(request,'Invalid Username or Password!. Try again')
        return redirect('loginpage')

def forgotpage(request):
    cata=category.objects.all()
    usernames = User.objects.values_list('username', flat=True)
    return render(request,"forgotP.html",{'category':cata,'usernames':usernames})

def forgot_password_submit(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        try:
            user = User.objects.get(username=username)

        except User.DoesNotExist:
            messages.error(request, "Username does not exist.")
            return redirect('forgot_password')  
        
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('forgot_password')

        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect('forgot_password')

        user.password = make_password(new_password)
        user.save()

        messages.success(request, "Password updated successfully! You can now log in.")
        return redirect('loginpage')  
    return redirect('forgotpage')


def regpage(request):
    existing_emails = list(User.objects.values_list('email', flat=True))
    usernames = User.objects.values_list('username', flat=True)
    phones=userdetails.objects.values_list('phone', flat=True)
    cata=category.objects.all()
    return render(request,"register.html",{'category':cata,'existing_emails': existing_emails,'usernames':usernames,'phone':phones})

def reguser(request):
    if request.method == 'POST':
        fname=request.POST['fname']
        lname=request.POST['lname']
        user=request.POST['username']
        email=request.POST['email']
        pwd=request.POST['password']
        cpwd=request.POST['cpassword']
        address=request.POST['address']
        phone=request.POST['contact']
        image=request.FILES.get('profile')
        if pwd==cpwd:
            if User.objects.filter(username=user).exists():
                messages.info(request,'This username already exists!!')
                return redirect('regpage')
            else:
                usr=User.objects.create_user(first_name=fname,last_name=lname,username=user,email=email,password=pwd)
                usr.save()

                det=userdetails(address=address,phone=phone,prf_image=image,user=usr)
                det.save()
                # subject='Your ecommerce username and password'
                # message2= 'Username:'+user+'\n'+'Password:'+pwd
                # send_mail(subject,message2,settings.EMAIL_HOST_USER,[email])
                return redirect('loginpage')
        else:
            messages.info(request,'Password doesn"t match!!')
            return redirect('regpage')
    return render(request,'register.html')

def productview(request,slug):
    if request.user.is_authenticated:
        current=request.user.id  
        c=category.objects.all()
        user=userdetails.objects.get(user_id=current)
        prd=product.objects.get(slug=slug)
        return render(request,'product.html',{'product':prd,'nav':c,'User':user})
    else:
        c=category.objects.all()
        prd=product.objects.get(slug=slug)
        return render(request,'product.html',{'product':prd,'nav':c})

@login_required(login_url='loginpage')
def userprofile(request):  
    current=request.user.id  
    c=category.objects.all()
    user=userdetails.objects.get(user_id=current)
    return render(request,'userprofile.html',{'user':user,'nav':c})

@login_required(login_url='loginpage')
def adminhome(request):
    #current=request.user.id 
    #user=User.objects.get(id=current)
    return render(request,"adminhome.html")

@login_required(login_url='loginpage')
def categorypage(request):
    return render(request,"addcategory.html")

@login_required(login_url='loginpage')
def addcata(request):
    if request.method == 'POST':
        cata=request.POST['cname']
        c=category(category_name=cata)
        c.save()
        messages.info(request,'Catagory Added')
        return redirect('categorypage')
    
@login_required(login_url='loginpage')
def productpage(request):
    cata=category.objects.all()
    return render(request,"addproduct.html",{'category':cata})

@login_required(login_url='loginpage')
def addproduct(request):
    if request.method == 'POST':
        pname=request.POST['pname']
        des=request.POST['pdesc']
        sel=request.POST['sel']
        c1=category.objects.get(id=sel)
        qty=request.POST['Nos']
        price=request.POST['price']
        image=request.FILES.get('prdimage')
        p=product(pdname=pname,nos=qty,pdprice=price,pd_desc=des,pdimage=image,category=c1)
        p.save()
        messages.info(request,'Product Added')
        return redirect('productpage')

@login_required(login_url='loginpage')
def productshow(request):
    p=product.objects.all()
    return render(request,"viewproduct.html",{'product':p})

@login_required(login_url='loginpage')
def delete_prod(request,slug):
    p=product.objects.get(slug=slug)
    if len(p.pdimage)>0:
        os.remove(p.pdimage.path)
    up=cart.objects.filter(product__slug=slug)
    up.delete()
    p.delete()
    return redirect('productshow')

@login_required(login_url='loginpage')
def update_product(request, slug):
    prod = product.objects.get(slug=slug)

    if request.method == 'POST':
        pdname = request.POST.get('pdname')
        pd_desc = request.POST.get('pd_desc')
        nos = request.POST.get('nos')
        pdprice = request.POST.get('pdprice')
        cate = request.POST.get('category')
        pdimage = request.FILES.get('pdimage', prod.pdimage)

        # Update the product object
        prod.pdname = pdname
        prod.pd_desc = pd_desc
        prod.nos = nos
        prod.pdprice = pdprice
        prod.category.id = cate  # Assuming `category` is a ForeignKey
        prod.pdimage = pdimage
        prod.save()

        return redirect('productshow')  # Replace with your product list view name
    categ = category.objects.all()  # Fetch all categories for dropdown
    return render(request, 'editproduct.html', {'product': prod, 'categories': categ})

@login_required(login_url='loginpage') 
def usershow(request):
    userd=userdetails.objects.all()
    for user in userd:
        total_quantity = order.objects.filter(user=user.user).aggregate(total=Sum('quantity'))['total'] or 0
        user.total_orders = total_quantity
    return render(request,"showuser.html",{'users':userd})

@login_required(login_url='loginpage') 
def logout_admin(request):
    auth.logout(request)
    return redirect('index')

def allcategory(request):
    if request.user.is_authenticated:
        current=request.user.id 
        user=userdetails.objects.get(user_id=current)
        pd=product.objects.all()
        c=category.objects.all()
        return render(request,"allcate.html",{'products':pd,'User':user,'nav':c})
    else:
        c=category.objects.all()
        pd=product.objects.all()
        return render(request,"allcate.html",{'products':pd,'nav':c})
def showcategory(request,slug):
    if request.user.is_authenticated:
        current=request.user.id 
        user=userdetails.objects.get(user_id=current)
        pd=product.objects.filter(category__slug=slug)
        c=category.objects.all()
        cata=category.objects.get(slug=slug)
        return render(request,"showcate.html",{'products':pd,'category':cata,'User':user,'nav':c})
    else:
        pd=product.objects.filter(category__slug=slug)
        c=category.objects.all()
        cata=category.objects.get(slug=slug)
        return render(request,"showcate.html",{'products':pd,'category':cata,'nav':c})
@login_required(login_url='loginpage')
def cart_view(request):
    current=request.user.id 
    pd=cart.objects.filter(user_id=current)
    each_price=sum(p.total_price for p in pd)
    total_price= each_price + 40
    num=cart.objects.filter(user_id=current).count()
    user=userdetails.objects.get(user_id=current)
    cata=category.objects.all()
    return render(request,"cart.html",{'products':pd,'user':user,'category':cata,'number':num,'total':total_price,'subtotal':each_price})
@login_required(login_url='loginpage')
def addcart(request,slug):
    current=request.user.id 
    user1=User.objects.get(id=current)
    prod=product.objects.get(slug=slug)
    prod.nos = prod.nos-1
    prod.save()
    total=1 * prod.pdprice
    cr=cart(user=user1,product=prod,total_price=total)
    cr.save()
    return redirect('cart_view')
@login_required(login_url='loginpage')
def delete_cart(request,slug):
    pd = product.objects.get(slug=slug)
    c = cart.objects.get(product=pd, user=request.user) 
    pd.nos = pd.nos + c.quantity
    pd.save()
    c.delete()
    return redirect('cart_view')
@login_required(login_url='loginpage')
def update_cart(request, slug):
    if request.method == "POST":
        pd = get_object_or_404(product, slug=slug)
        cart_item = get_object_or_404(cart, product=pd, user=request.user)

        new_quantity = int(request.POST.get('quantity', 1))
        if cart_item.quantity < new_quantity:
            pd.nos -= (new_quantity - cart_item.quantity)
        else:
            pd.nos += (cart_item.quantity - new_quantity)
        pd.save()
        cart_item.quantity = new_quantity
        cart_item.total_price = new_quantity * pd.pdprice
        cart_item.save()
        return redirect('cart_view')
@login_required(login_url='loginpage')
def create_order(request):
    if request.method == "POST":
        user = request.user
        cart_items = cart.objects.filter(user=user)  # Retrieve cart items for the logged-in user

        if cart_items.exists():
            for item in cart_items:
                odr=order(user=user,product=item.product,quantity=item.quantity,total=item.total_price)
                odr.save()
            cart_items.delete()

            messages.success(request, "Order placed successfully!")
        else:
            messages.error(request, "Your cart is empty!")
        
        return redirect("view_order")  # Redirect to homepage or order summary page
    return redirect("cart_view")
@login_required(login_url='loginpage')
def view_order(request):
    user = request.user
    order_items=order.objects.filter(user=user)
    user=userdetails.objects.get(user_id=user.id)
    cata=category.objects.all()
    return render(request,"vieworders.html",{'products':order_items,'user':user,'category':cata})

@login_required(login_url='loginpage')
def change_password(request):
    current=request.user.id 
    user=userdetails.objects.get(user_id=current)
    
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(old_password):
            messages.error(request, "Old password is incorrect.")
            return redirect('change_password')

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect('change_password')

        if old_password == new_password:
            messages.error(request, "New password cannot be the same as the old password.")
            return redirect('change_password')

        # Set the new password
        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)  # Prevent logout after password change
        messages.success(request, "Your password has been successfully updated!")
        return redirect('userprofile')

    return render(request, 'change_passwd.html',{'user':user})



@login_required(login_url='loginpage')
def edit_profile(request):
    user_details = userdetails.objects.get(user=request.user)

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        prf_image = request.FILES.get('prf_image')  # Retrieve the uploaded profile image

        # Basic validation
        if not first_name or not last_name or not email or not phone or not address:
            messages.error(request, "All fields are required.")
            return render(request, 'edit_profile.html', {'user_details': user_details})

        # Update user fields
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        # Update userdetails fields
        user_details.phone = phone
        user_details.address = address

        # Handle profile image upload if provided
        if prf_image:
            # Delete the old image file if it exists and isn't the default image
            if user_details.prf_image and default_storage.exists(user_details.prf_image.path):
                user_details.prf_image.delete()

            user_details.prf_image = prf_image

        user_details.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('userprofile')  # Redirect to the profile page

    return render(request, 'edit_profile.html', {'user_details': user_details})


@login_required(login_url='loginpage')
def logout_user(request):
    auth.logout(request)
    return redirect('index')