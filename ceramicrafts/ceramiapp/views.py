from django.shortcuts import render,redirect,get_object_or_404
from ceramiapp.models import userdetails,category,product,cart,order
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate,login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
import os
# Create your views here.
def index(request):
    cata=category.objects.all()
    items=product.objects.all()
    prod=product.objects.filter(id__in=order.objects.values_list('product', flat=True).distinct())
    return render(request,"index.html",{'category':cata,'product':prod,'items':items})
@login_required(login_url='loginpage')
def userindex(request):
    current=request.user.id 
    user=userdetails.objects.get(user_id=current)
    prod=prod=product.objects.filter(id__in=order.objects.values_list('product', flat=True).distinct())
    items=product.objects.all()
    cata=category.objects.all()
    return render(request,"userindex.html",{'category':cata,'user':user,'product':prod,'items':items})
@login_required(login_url='loginpage')
def userprofile(request):  
    current=request.user.id  
    c=category.objects.all()
    user=userdetails.objects.get(user_id=current)
    return render(request,'userprofile.html',{'user':user,'nav':c})
def productview(request,a):
    if request.user.is_authenticated:
        current=request.user.id  
        c=category.objects.all()
        user=userdetails.objects.get(user_id=current)
        prd=product.objects.get(id=a)
        return render(request,'product.html',{'product':prd,'nav':c,'user':user})
    else:
        c=category.objects.all()
        prd=product.objects.get(id=a)
        return render(request,'productV.html',{'product':prd,'nav':c})

def loginpage(request):
    cata=category.objects.all()
    return render(request,"Login.html",{'category':cata})
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
                # messages.info(request,f'{usr1}')
                return redirect('userindex')
            # request.session['uid']= usr.id
            
        else:
            messages.info(request,'Invalid Username or Password!. Try again')
            return redirect('loginpage')
    else:
        messages.info(request,'Invalid Username or Password!. Try again')
        return redirect('loginpage')



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
def delete_prod(request,a):
    p=product.objects.get(id=a)
    if len(p.pdimage)>0:
        os.remove(p.pdimage.path)
    up=cart.objects.filter(product_id=a)
    up.delete()
    p.delete()
    return redirect('productshow')
@login_required(login_url='loginpage')
def update_product(request, a):
    prod = product.objects.get(id=a)

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
        return render(request,"userallcate.html",{'products':pd,'user':user,'nav':c})
    else:
        c=category.objects.all()
        pd=product.objects.all()
        return render(request,"allcate.html",{'products':pd,'nav':c})
def showcategory(request,a):
    if request.user.is_authenticated:
        current=request.user.id 
        user=userdetails.objects.get(user_id=current)
        pd=product.objects.filter(category_id=a)
        c=category.objects.all()
        cata=category.objects.get(id=a)
        return render(request,"usershowcate.html",{'products':pd,'category':cata,'user':user,'nav':c})
    else:
        pd=product.objects.filter(category_id=a)
        c=category.objects.all()
        cata=category.objects.get(id=a)
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
def addcart(request,a):
    current=request.user.id 
    user1=User.objects.get(id=current)
    prod=product.objects.get(id=a)
    prod.nos = prod.nos-1
    prod.save()
    total=1 * prod.pdprice
    cr=cart(user=user1,product=prod,total_price=total)
    cr.save()
    return redirect('cart_view')
@login_required(login_url='loginpage')
def delete_cart(request,a):
    c=cart.objects.get(id=a)
    pd=product.objects.get(id=c.product.pk)
    pd.nos = pd.nos + c.quantity
    pd.save()
    c.delete()
    return redirect('cart_view')
@login_required(login_url='loginpage')
def update_cart(request, p_id):
    if request.method == "POST":
        cart_item = get_object_or_404(cart, id=p_id)
        new_quantity = int(request.POST.get('quantity', 1))
        if cart_item.quantity < new_quantity:
            pd=product.objects.get(id=cart_item.product.pk)
            pd.nos = pd.nos - (new_quantity-1)
        else:
            pd=product.objects.get(id=cart_item.product.pk)
            pd.nos = pd.nos + (new_quantity+1)
        pd.save()
        cart_item.quantity = new_quantity
        cart_item.total_price = new_quantity * cart_item.product.pdprice
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
def logout_user(request):
    auth.logout(request)
    return redirect('index')