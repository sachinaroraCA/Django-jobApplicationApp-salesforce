from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from main_app.utils.drive_api import GoogleDrive
from main_app.utils.ip_location_utils import get_ip_address, get_city, get_location
from main_app.utils.sf_api import SFConnectAPI
from main_app.utils.drive_utils import get_folder_id
import re


def home(request):
    return render(request,
                  "application_form.html",
                  {'designations': ['', 'Developer', 'Consultant', 'HR', 'QA', 'Bussiness Developer Executive', 'Content Writer', 'UI Developer', 'Sales Executive', 'Web Developer', 'Sales'],
                   'experiences': ['0-6 months', '1 year', '2 years', '3-5 years', '5+ years'],
                   'education': ['', 'Graduation', 'Masters', 'B.Tech']},)


def upload_details(request):
    try:
        if request.method == 'POST':
            first_name = str(request.POST.get("firstName")).strip()
            last_name = str(request.POST.get("firstName")).strip()
            name = first_name+" "+last_name
            email = request.POST.get("Email__c")
            contact = request.POST.get("Contact_Number__c")
            education = request.POST.get("Education__c")
            experience = request.POST.get("Experience__c")
            resume = request.FILES["resumeFile"]
            designation = request.POST.get("Designation__c")

            if not name or name == "" or not bool(re.match('^[a-zA-Z ]+$', name)):
                messages.error(request, "Error: Name field must contains only Characters")
                return HttpResponseRedirect('/home/')

            if not re.match('^[0-9]+$', contact):
                messages.error(request, "Error: Phone field must contains only Numbers")
                return HttpResponseRedirect('/home/')


            # Uploading the file in DRIVE
            file_name = name + " | " + contact + " | " + email
            folder_info = get_folder_id(designation)
            if folder_info[0]:
                folder_id = folder_info[1]
                gd_instance = GoogleDrive()
                file_id, file_url = gd_instance.upload_file(file_name, media=resume, folder_id=folder_id)

                ip_address = get_ip_address()
                if not ip_address or ip_address == '127.0.0.1':
                    ip_address = '122.176.52.148'

                location = get_location(ip_address)
                city = get_city(ip_address)

                # CREATE RECORD IN SALESFORCE
                sf_instance = SFConnectAPI()
                result = sf_instance.create_record(object_name='Resume_Google_Drive_Link__c',
                                                   data={'Name__c': name,
                                                         'Contact_Number__c': contact,
                                                         'Email__c': email,
                                                         'Google_Drive_URL__c': file_url,
                                                         'Position__c': designation,
                                                         'Address__latitude__s': location[1],
                                                         'Address__longitude__s': location[0],
                                                         'City__c': city,
                                                         'Highest_Education__c': education,
                                                         'Experience__c': experience,
                                                         })
                if "id" in result.keys():
                    print(result["id"] + " created")

                if result['success']:
                    messages.success(request, 'You have applied successfully !!!')
                else:
                    print("Record not created in salesforce:" + str(result))
                    messages.error(request, 'Unable to process request.. try again later !!!')
                    
            else:
                print("google drive folder does not exists")
                messages.error(request, 'Unable to process request.. try again later !!!')
    except Exception as ex:
        print("Exception:"+ repr(ex))
        messages.error(request, 'Unable to process request.. try again later !!!')
    return HttpResponseRedirect('/')