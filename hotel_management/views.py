import tablib, os, shutil
from django.shortcuts import render_to_response, RequestContext, HttpResponseRedirect, HttpResponse
from django.template import Template,Context
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from customers.models import Customer, hotel_deposit, hotel_fee, Upload
from django.db.models import Q
from customers.forms import CustomerForm, mess_depositForm, hotel_feeForm, signupform, UploadForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from customers.admin import CustomerResource, xlsImporterModel
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

                       
@login_required(login_url='/index/')
def profile(request):
    query=request.GET.get("search","")
    if query:
        qlist=(Q(name__icontains=query)|Q(usn__icontains=query))
        result=Customer.objects.filter(qlist).distinct()
        
    else:
        result=[]
    return render_to_response('profile.html',{"results":result,"query":query},context_instance=RequestContext(request))

@login_required(login_url='/index/')
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/index/")

@login_required(login_url='/index/')
def search(request):
    query=request.GET["search"]
    if query:
        qlist=(Q(name__icontains=query)|Q(usn__icontains=query))
        result=Customer.objects.filter(qlist).distinct()
        
    else:
        result=[]
    return render_to_response("profile.html",{"results":result,"query":query})

@login_required(login_url='/index/')
def delete_customer(request,que):
    query=request.GET.get("search")
    if query:
        qlist=(Q(name__icontains=query)|Q(usn__icontains=query))
        result=Customer.objects.filter(qlist).distinct()
        result.delete()
    else:
        result=[]
    return render_to_response("profile.html",{"results":result,"query":query})

@login_required(login_url='/index/')
def dataset_export_query(request,query):
        qlist=(Q(name__icontains=query)|Q(usn__icontains=query))
        result=Customer.objects.filter(qlist).distinct()
        ds=CustomerResource().export(result)
        response=HttpResponse(ds.xls,content_type="xls")
        response['Content-Disposition']='filename=Customers.xls'
        return response
    
@login_required(login_url='/index/')
def edit_form(request,Customer_usn):
    Customer=Customer.objects.get(usn=Customer_usn)
    if request.method == "POST":
        form=CustomerForm(request.POST,instance=Customer)
        if form.is_valid():
            form.save()
            msg_html = render_to_string('email_template.html', {'Customer': Customer})
            send_mail('hotel Management System','hey','technoboysid@gmail.com',(Customer.email,),html_message=msg_html)
            return HttpResponse('<script type="text/javascript">window.close();window.opener.parent.location.reload() ;</script>')
    else:
        form=CustomerForm(instance=Customer)
    return render_to_response('edit_form.html',{"form":form,"Customer":Customer},context_instance=RequestContext(request))

@login_required(login_url='/index/')
def hotel_bill(request):
    if request.method=="POST":
        form=mess_depositForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/hotel_bill/')
    else:
        form=mess_depositForm()
    return render_to_response('mess_bill.html',{"form":form,"mess_deposit":mess_deposit.objects.all()},context_instance=RequestContext(request))

@login_required(login_url='/index/')
def hotel_fee_paid(request):
    if request.method=="POST":
        form=hotel_feeForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/hotel_fee/')
    else:
        form=hotel_feeForm()
    return render_to_response('hotel_fee.html',{"form":form,"hotel_fee":hotel_fee.objects.all()},context_instance=RequestContext(request))

@login_required(login_url='/index/')
def dataset_export(request):
        ds=CustomerResource().export()
        response=HttpResponse(ds.xls,content_type="xls")
        response['Content-Disposition']='filename=Customers.xls'
        return response

@login_required(login_url='/index/')
def customer(request):
    try:
        shutil.rmtree("media/files/")
    except:
        pass
    form= UploadForm()
    if request.method=="POST":
        upload="" 
        form=UploadForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            upload=request.FILES["file"]
            my_xls_file= xlsImporterModel(source="media/files/%s"%(upload.name))
            my_xls_file.save()
            temp=Upload.objects.get(name="tempfile")
            temp.delete()
            return HttpResponseRedirect("/Customer/")
    else:
        upload=""
    return render_to_response("Customer.html",{"form":form,"uploaded":upload},context_instance=RequestContext(request))

def signup(request):
    form=UserCreationForm()
    errors={}
    if request.method=="POST":
        form=UserCreationForm(data=request.POST)
        if form.is_valid():
            user=User.objects.create_user(username=form.cleaned_data["username"],password=form.cleaned_data["password1"])
            user.is_staff=True
            user.is_superuser=True
            user.save()
            return HttpResponseRedirect('/index/')
        else:
            errors=form.errors
    else:
        form=UserCreationForm()
    return render_to_response("signup.html",{"form":form,"errors":errors},context_instance=RequestContext(request))
