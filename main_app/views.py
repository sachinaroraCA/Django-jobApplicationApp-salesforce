from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from main_app.utils.drive_api import GoogleDrive
from main_app.utils.ip_location_utils import get_ip_address, get_city, get_location
from main_app.utils.sf_api import SFConnectAPI
from main_app.utils.drive_utils import get_folder_id
import re



@csrf_exempt
def home(request):
    sf = SFConnectAPI()
    designations = sf.get_position_values()
    print(designations)
    designation = 'Developer'
    return render(request,
                  "application_form.html",
                  {'designations': designations,'designation':designation})


@csrf_exempt
def upload_details(request):
    try:
        if request.method == 'POST':
            name = str(request.POST.get("name")).strip()
            email = request.POST.get("Email__c")
            contact = request.POST.get("Contact_Number__c")
            resume = request.FILES["resumeFile"]
            resume_field = request.POST.get("resumeFile")
            designation = request.POST.get("Designation__c")

            if not name or name == "" or not bool(re.match('^[a-zA-Z ]+$', name)):
                messages.error(request, "Error: Name field must contains only Characters")
                sf = SFConnectAPI()
                designations = sf.get_position_values()
                msg_html = render_to_string(request,
                               "message.html",  {'msg':"Name field must contains only Characters"})
                return {"msg_html": msg_html}

            elif not re.match('^[0-9]+$', contact) or len(contact) != 10:
                sf = SFConnectAPI()
                designations = sf.get_position_values()
                messages.error(request, "Error: Phone field must contains only Numbers and length should be 10")
                msg_html = render_to_string(request,
                               "message.html", { "msg": "Error: Phone field must contains only Numbers and length should be 10"
                                                      })
                return {"msg_html": msg_html}


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
                                                         })
                if "id" in result.keys():
                    print(result["id"] + " created")

                if result['success']:
                    messages.success(request, 'Thank you for apply successfully in Cloudanalogy !!!')
                    msg_html = render_to_string(request,
                                                "message.html", {
                                                    "msg": "'Thank you for apply successfully in Cloudanalogy !!!'"
                                                    })
                    return {"msg_html": msg_html}
                else:
                    print("Record not created in salesforce:" + str(result))
                    messages.error(request, 'Unable to process request.. try again later !!!')
            else:
                print("google drive folder does not exists")
                messages.error(request, 'Unable to process request.. try again later !!!')
    except Exception as ex:
        print("Exception:" + repr(ex))
        messages.error(request, 'Unable to process request.. try again later !!!')
    return HttpResponseRedirect('/')

from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt

@xframe_options_exempt
def ok_to_load_in_a_frame(request):
    return HttpResponse("This page is safe to load in a frame on any site.")