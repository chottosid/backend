from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from .models import *
import json
import math
from django.utils import timezone


def haversine_distance(lat1, lon1, lat2, lon2):

    '''
    Calculate the haversine distance between two points
    '''
    R = 6371  # Earth radius in kilometers
    
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance * 1000  # Convert to meters

@csrf_exempt
def user_login(request):
    '''
    User login
    POST /user/login/
    {
        "email": "email"
        "password": "password"
    }
    '''
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            print(email)
            password = data.get('password')
            #print(password)
            try:
                user = User.objects.get(email=email)
                #print(user.password)
                # Check password (assuming passwords are hashed)
                if check_password(password, user.password):
                    return JsonResponse({
                        'user_id': user.user_id,
                        'name': user.name,
                        'email': user.email,
                    }, status=200)
                else:
                    return JsonResponse({'error': 'Invalid credentials'}, status=401)
            
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def user_register(request):
    '''
    User registration
    POST /user/register/
    {
        "name": "name",
        "email": "email",
        "password": "password",
        "address": "address",
        "dob": "yyyy-mm-dd",
        "gender": "Male",
        "number": "number",
        "profile_picture": FILE
    }
    '''
    if request.method == 'POST':
        try:
            data = request.POST.dict()
            # Check if user already exists
            #print(data)
            if User.objects.filter(email=data.get('email')).exists():
                return JsonResponse({'error': 'Email already exists'}, status=409)
            dob = data.get('dob')
            # Change dob from yyyy-mm-dd format to django datetime format
            data['dob'] = f'{dob}T00:00:00Z'
            # Create new user
            user = User.objects.create(
                name=data.get('name'),
                email=data.get('email'),
                password=make_password(data.get('password')),
                address=data.get('address'),
                dob=dob,
                gender=data.get('gender'),
                number=data.get('number'),
                profile_picture=request.FILES.get('profile_picture'),
                created_at=timezone.now()
            )
            
            return JsonResponse({
                'message': 'User registered successfully',
                'user_id': user.user_id
            }, status=201)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def send_request(request):
    '''
    Send a request to the system from user
    POST /pending/send/
    {
        "userId": 1,
        "assistantId": 1,
        "category": "category",
        "description": "description",
        "latitude": "latitude",
        "longitude": "longitude"
    }
    '''
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            assistant = Assistant.objects.get(assistant_id=data.get('assistantId'))
            if assistant.status != 'available':
                return JsonResponse({'error': 'Assistant is not available'}, status=400)
            user = User.objects.get(user_id=data.get('userId'))
            pending_request = PendingRequest.objects.create(
                user=user,
                category=data.get('category'),
                description=data.get('description'),
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                status='pending',
                assistant=assistant
            )
            return JsonResponse({'message': 'Request sent successfully', 'requestId': pending_request.request_id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def get_pending_requests_user(request,user_id):
    '''
        GET pending/requests/user/1
        returns
        [
            {
                "requestId": 1,
                "userId": 1,
                "userName": "name",
                "category": "category",
                "description": "description",
                "latitude": "latitude",
                "longitude": "longitude",
                "created_at": "2022-01-01T00:00:00Z"
            }
        ]
    '''
    if request.method == 'GET':
        user = User.objects.get(user_id=user_id)
        pending_requests = PendingRequest.objects.filter(user=user)
        request_list = []
        for req in pending_requests:
            request_list.append({
                'requestId': req.request_id,
                'userId': req.user.user_id,
                'userName': req.user.name,
                'category': req.category,
                'description': req.description,
                'latitude': req.latitude,
                'longitude': req.longitude,
                'created_at': req.created_at,
                'status': req.status
            })
        return JsonResponse(request_list, safe=False, status=200)


@csrf_exempt
def get_pending_requests(request,assistantId):
    '''
    Get all pending requests for assistants
    GET /pending/requests/1

    returns
    [
        {
            "requestId": 1,
            "userId": 1,
            "userName": "name",
            "category": "category",
            "description": "description",
            "latitude": "latitude",
            "longitude": "longitude",
            "created_at": "2022-01-01T00:00:00Z"
        }
    ]
    '''
    if request.method == 'GET':
        assistant = Assistant.objects.get(assistant_id=assistantId)
        pending_requests = PendingRequest.objects.filter(assistant=assistant)
        request_list = []
        for req in pending_requests:
            request_list.append({
                'requestId': req.request_id,
                'userId': req.user.user_id,
                'userName': req.user.name,
                'category': req.category,
                'description': req.description,
                'latitude': req.latitude,
                'longitude': req.longitude,
                'created_at': req.created_at,
                'status': req.status
            })
        return JsonResponse(request_list, safe=False, status=200)

@csrf_exempt
def confirm_request(request):
    '''
    Confirm a request by assistant
    POST /pending/confirm/
    {
        "requestId": 1,
        "assistantId": 1
    }
    '''
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            request_id = data.get('requestId')
            assistant_id = data.get('assistantId')
            try:
                req = PendingRequest.objects.get(request_id=request_id)
                assistant = Assistant.objects.get(assistant_id=assistant_id)
                req.status = 'accepted'
                req.assistant = assistant
                req.save()
                assistant.status = 'busy'
                assistant.save()
                return JsonResponse({'message': 'Request confirmed'}, status=200)
            except PendingRequest.DoesNotExist:
                return JsonResponse({'error': 'Request not found'}, status=404)
            except Assistant.DoesNotExist:
                return JsonResponse({'error': 'Assistant not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def completed_request(request):
    '''
    confirm request completion by assistant
    POST /pending/completed/
    {
        "requestId": 1,
        "assistantId": 1
    }
    '''
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            request_id = data.get('requestId')
            assistant_id = data.get('assistantId')
            try:
                req = PendingRequest.objects.get(request_id=request_id)
                assistant = Assistant.objects.get(assistant_id=assistant_id)
                req.status = 'completed'
                req.save()
                assistant.status = 'available'
                assistant.save()
                return JsonResponse({'message': 'Request completed'}, status=200)
            except PendingRequest.DoesNotExist:
                return JsonResponse({'error': 'Request not found'}, status=404)
            except Assistant.DoesNotExist:
                return JsonResponse({'error': 'Assistant not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
def get_notification(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
        pending_requests = PendingRequest.objects.filter(user=user, status='accepted', notified=0)
        
        if not pending_requests:
            return JsonResponse({'message': 'No new notifications'}, status=204)
        
        accepted_requests = []
        for req in pending_requests:
            accepted_requests.append({
                'id': req.id,
                'latitude': req.latitude,
                'longitude': req.longitude,
                'assistantId': req.assistant.id if req.assistant else None,
                'assistantName': req.assistant.name if req.assistant else None
            })
            req.notified = 1
            req.save()
        
        return JsonResponse(accepted_requests, safe=False, status=200)
    
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def check_request(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
        pending_requests = PendingRequest.objects.filter(user=user)
        
        if not pending_requests:
            return JsonResponse({'message': 'No requests found'}, status=204)
        
        request_list = [{
            'id': req.id,
            'status': req.status,
            'latitude': req.latitude,
            'longitude': req.longitude,
            'assistantId': req.assistant.id if req.assistant else None,
            'assistantName': req.assistant.name if req.assistant else None
        } for req in pending_requests]
        
        return JsonResponse(request_list, safe=False, status=200)
    
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
'''
    Assistant login
    POST /assistant/login/
    {
        "email": "email"
        "password": "password"
    }
'''
@csrf_exempt
def assistant_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            
            try:
                assistant = Assistant.objects.get(email=email)
                
                # Check password (assuming passwords are hashed)
                if check_password(password, assistant.password):
                    return JsonResponse({
                        'assistant_id': assistant.assistant_id,
                        'name': assistant.name,
                        'email': assistant.email,
                    }, status=200)
                else:
                    return JsonResponse({'error': 'Invalid credentials'}, status=401)
            
            except Assistant.DoesNotExist:
                return JsonResponse({'error': 'Assistant not found'}, status=404)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def assistant_register(request):
    '''
    Assistant registration
    POST /assistant/register/
    {
        "name": "name",
        "email": "email",
        "password": "password",
        "dob": "yyyy-mm-dd",
        "latitude": "latitude",
        "longitude": "longitude
    }
    '''
    if request.method == 'POST':
        try:
            data = request.POST.dict()
            # Check if assistant already exists
            if Assistant.objects.filter(email=data.get('email')).exists():
                return JsonResponse({'error': 'Email already exists'}, status=409)
            dob = data.get('dob')
            # Change dob from yyyy-mm-dd format to django datetime format
            data['dob'] = f'{dob}T00:00:00Z'
            # Create new assistant
            assistant = Assistant.objects.create(
                name=data.get('name'),
                email=data.get('email'),
                password=make_password(data.get('password')),
                dob=dob,
                profile_picture=request.FILES.get('profile_picture'),
                id_proof=request.FILES.get('id_proof'),
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                gender = data.get('gender'),
                number = data.get('number'),
                address = data.get('address')
            )
            return JsonResponse({
                'assistant_id': assistant.assistant_id,
                'name': assistant.name,
                'email': assistant.email,
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def doctor_login(request):
    '''
    Doctor login
    POST /doctor/login/
    {
        "email": "email"
        "password": "password"
    }
    '''
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            try:
                doctor = Doctor.objects.get(email=email)
                # Check password (assuming passwords are hashed)
                if check_password(password, doctor.password):
                    return JsonResponse({
                        'doctor_id': doctor.doctor_id,
                        'name': doctor.name,
                        'email': doctor.email,
                    }, status=200)
                else:
                    return JsonResponse({'error': 'Invalid credentials'}, status=401)
            except Doctor.DoesNotExist:
                return JsonResponse({'error': 'Doctor not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
'''

    Doctor registration
    POST /doctor/register/
    {
        "name": "name",
        "email": "email",
        "password": "password",
        "dob": "yyyy-mm-dd",
    
'''
@csrf_exempt
def doctor_register(request):
    if request.method == 'POST':
        try:
            data = request.POST.dict()
            # Check if doctor already exists
            print(data)
            if Doctor.objects.filter(email=data.get('email')).exists():
                return JsonResponse({'error': 'Email already exists'}, status=409)
            dob = data.get('dob')
            # Change dob from yyyy-mm-dd format to django datetime format
            data['dob'] = f'{dob}T00:00:00Z'
            # Create new doctor
            doctor = Doctor.objects.create(
                name=data.get('name'),
                email=data.get('email'),
                password=make_password(data.get('password')),
                dob=dob,
                profile_picture=request.FILES.get('profile_picture'),
                reg_no=data.get('reg_no'),
                gender=data.get('gender'),
                id_proof=request.FILES.get('id_proof'),
                specialization=data.get('specialization'),
                experience=data.get('experience'),
                address=data.get('address')
            )
            return JsonResponse({
                'message': 'Doctor registered successfully',
                'doctor_id': doctor.doctor_id
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def add_appointment(request):

    '''
    Add an appointment from user to doctor
    POST doctor/appointment/add/
    {
        "user_id": 1,
        "doctor_id": 1,
        "date": "2022-01-01",
        "time": "10:00"
    }

    '''
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data)
            user_id = data.get('user_id')
            doctor_id = data.get('doctor_id')
            date = data.get('date')
            time = data.get('time')
            try:
                user = User.objects.get(user_id=user_id)
                doctor = Doctor.objects.get(doctor_id=doctor_id)
                appointment_time = f'{date} {time}'
                appointment = Appointment.objects.create(
                    user=user,
                    doctor=doctor,
                    appointment_time=appointment_time,
                    status='pending'
                )
                return JsonResponse({
                    'message': 'Appointment added successfully',
                    'appointment_id': appointment.appointment_id
                }, status=201)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
            except Doctor.DoesNotExist:
                return JsonResponse({'error': 'Doctor not found'}, status=404)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def confirm_appointment(request):
    '''
    Confirm an appointment by doctor
    POST doctor/appointment/confirm/
    {
        "appointment_id": 1
        "doctor_id": 1
    }
    '''
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            appointment_id = data.get('appointment_id')
            doctor_id = data.get('doctor_id')
            try:
                appointment = Appointment.objects.get(appointment_id=appointment_id)
                doctor = Doctor.objects.get(doctor_id=doctor_id)
                appointment.status = 'confirmed'
                appointment.save()
                return JsonResponse({'message': 'Appointment confirmed'}, status=200)
            except Appointment.DoesNotExist:
                return JsonResponse({'error': 'Appointment not found'}, status=404)
            except Doctor.DoesNotExist:
                return JsonResponse({'error': 'Doctor not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def get_user_appointments(request, user_id):
    '''
    Get appointments for a user
    GET doctor/appointment/user/1/
    '''
    try:
        user = User.objects.get(user_id=user_id)
        appointments = Appointment.objects.filter(user=user)
        if not appointments:
            return JsonResponse({'message': 'No appointments found'}, status=204)
        appointment_list = []
        for appointment in appointments:
            appointment = {
                'appointment_id': appointment.appointment_id,
                'doctor_id': appointment.doctor.doctor_id,
                'doctor_name': appointment.doctor.name,
                'date': appointment.appointment_time.strftime('%Y-%m-%d'),
                'time': appointment.appointment_time.strftime('%H:%M'),
                'status': appointment.status
            }
            appointment_list.append(appointment)
        return JsonResponse(appointment_list, safe=False, status=200)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=400)


def get_doctor_appointments(request, doctor_id):
    '''
    Get appointments for a doctor
    GET doctor/appointment/doctor/1/
    '''
    if request.method == 'GET':
        try:
            doctor = Doctor.objects.get(doctor_id=doctor_id)
            appointments = Appointment.objects.filter(doctor=doctor)
            if not appointments:
                return JsonResponse({'message': 'No appointments found'}, status=204)
            appointment_list = [{
                'appointment_id': appointment.appointment_id,
                'user_id': appointment.user.user_id,
                'user_name': appointment.user.name,
                'date': appointment.appointment_time.strftime('%Y-%m-%d'),
                'time': appointment.appointment_time.strftime('%H:%M'),
                'status': appointment.status
            } for appointment in appointments]
            return JsonResponse(appointment_list, safe=False, status=200)
        except Doctor.DoesNotExist:
            return JsonResponse({'error': 'Doctor not found'}, status=404)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

    

def get_doctors(request):
    '''
    Get all doctors
    GET /doctor/all/
    returns
    [
        {
            "doctor_id": 1,
            "name": "name",
            "profile_picture": "image",
            "gender": "gender"
            "specialization": "specialization",
            "experience": 1,
            "address": "address"
        }
    ]
    '''
    if request.method == 'GET':
        doctors = Doctor.objects.all()
        if not doctors:
            return JsonResponse({'message': 'No doctors found'}, status=204)
        doctor_list = [{
            'doctor_id': doctor.doctor_id,
            'name': doctor.name,
            'profile_picture': request.build_absolute_uri(doctor.profile_picture.url),
            'gender': doctor.gender,
            'specialization': doctor.specialization,
            'experience': doctor.experience,
            'address': doctor.address
        } for doctor in doctors]
        return JsonResponse(doctor_list, safe=False, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def get_assistants(request):
    '''
    Get all assistants who are available for a request
    GET /assistant/all/
    '''
    if request.method == 'GET':
        assistants = Assistant.objects.filter(status='available')
        if not assistants:
            return JsonResponse({'message': 'No assistants found'}, status=204)
        #get the assistant along with profile picture
        assistant_list = [{
            'assistant_id': assistant.assistant_id,
            'name': assistant.name,
            'latitude': assistant.latitude,
            'longitude': assistant.longitude,
            'profile_picture': request.build_absolute_uri(assistant.profile_picture.url),
            'number': assistant.number,
        } for assistant in assistants]

        return JsonResponse(assistant_list, safe=False, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def post_feed(request):
    '''
    Post to news feed
    POST /user/feed/post/
    {
        "user_id": 1,
        "content": "content",
        "image": FILE
    }
    '''
    if request.method == 'POST':
        try:
            data = request.POST.dict()
            #print(data.get('user_id'))
            post = Post.objects.create(
                user=User.objects.get(user_id=data.get('user_id')),
                content=data.get('content'),
                media=request.FILES.get('image'),
            )
            return JsonResponse({'message': 'Post added successfully', 'post_id': post.id}, status=201)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def comment(request):
    '''
    Comment on a post
    POST /user/feed/comment/
    {
        "user_id": 1,
        "post_id": 1,
        "content": "content"
    }
    '''
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            comment = Comment.objects.create(
                user=User.objects.get(user_id=data.get('user_id')),
                post=Post.objects.get(id=data.get('post_id')),
                content=data.get('content')
            )
            notification = Notification.objects.create(
                user=comment.post.user,
                content=f'{comment.user.name} commented on your post',
                is_read=False,
                post=comment.post
            )
            return JsonResponse({'message': 'Comment added successfully', 'comment_id': comment.id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def get_all_notifications(request, user_id):
    '''
    Get all notifications for a user
    GET /user/notifications/all/id/
    returns
    [
        {
            "notification_id": 1,
            "content": "content",
            "created_at": "2022-01-01T00:00:00Z",
            "post_id": 1
        }
    ]

    '''
    if request.method == 'GET':
        try:
            user = User.objects.get(user_id=user_id)
            notifications = Notification.objects.filter(user=user, is_read=False)
            if not notifications:
                return JsonResponse({'message': 'No notifications found'}, status=204)
            notification_list = [{
                'notification_id': notification.id,
                'content': notification.content,
                'created_at': notification.created_at,
                'post_id': notification.post.id if notification.post else None
            } for notification in notifications]
            return JsonResponse(notification_list, safe=False, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
@csrf_exempt
def get_post(request,post_id):
    '''
    Get a post by post id
    GET /user/feed/id/

    '''
    if request.method == 'GET':
        try:
            post = Post.objects.get(id=post_id)
            comments = Comment.objects.filter(post=post)
            comment_list = []
            for comment in comments:
                comment_list.append({
                    'comment_id': comment.id,
                    'user_id': comment.user.user_id,
                    'user_name': comment.user.name,
                    'content': comment.content,
                    'created_at': comment.created_at
                })
            return JsonResponse({
                'post_id': post.id,
                'user_id': post.user.user_id,
                'user_name': post.user.name,
                'content': post.content,
                'image': post.image.url if post.image else None,
                'created_at': post.created_at,
                'comments': comment_list
            }, status=200)
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
@csrf_exempt
def get_all_posts(request,uid):
    '''
    Get all posts
    GET /user/feed/all/<int:uid>
    returns 
    [
        {
            "post_id": 1,
            "user_id": 1,
            "user_name": "name",
            "user_image" : "image",
            "content": "content",
            "image": "image",
            "created_at": "2022-01-01T00:00:00Z",
            "comments": [
                {
                    "comment_id": 1,
                    "user_id": 1,
                    "user_name": "name",
                    'user_image': 'image',
                    "content": "content",
                    "created_at": "2022-01-01T00:00:00Z"
                }
            ],
            likes: 3,
            liked: true
        }
    ]
    '''
    if request.method=='GET':
        #get posts sorted by created_at
        posts = Post.objects.all().order_by('-created_at')
        post_list = []
        for post in posts:
            comments = Comment.objects.filter(post=post)
            comment_list = []
            like_cnt = post.liked_by.count()
            for comment in comments:
                comment_list.append({
                    'comment_id': comment.id,
                    'user_id': comment.user.user_id,
                    'user_name': comment.user.name,
                    'user_image': request.build_absolute_uri(comment.user.profile_picture.url),
                    'content': comment.content,
                    'created_at': comment.created_at
                })
            post_list.append({
                'post_id': post.id,
                'user_id': post.user.user_id,
                'user_name': post.user.name,
                'user_image': request.build_absolute_uri(post.user.profile_picture.url),
                'content': post.content,
                'image': request.build_absolute_uri(post.media.url if post.media else None),
                'created_at': post.created_at,
                'comments': comment_list,
                'likes': like_cnt,
                'liked': post.liked_by.filter(user_id=uid).exists()
            })
        return JsonResponse(post_list, safe=False, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def like_post(request):
    '''
    Like a post
    POST /user/feed/like/
    {
        "user_id": 1,
        "post_id": 1
    }
    '''
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            post = Post.objects.get(id=data.get('post_id'))
            #check if user already liked the post
            if post.liked_by.filter(user_id=data.get('user_id')).exists():
                #unlike the post
                post.liked_by.remove(data.get('user_id'))
            else:
                #like the post
                post.liked_by.add(data.get('user_id'))
                # create a notification
                notification = Notification.objects.create(
                    user=post.user,
                    content=f'{User.objects.get(user_id=data.get("user_id")).name} liked your post',
                    is_read=False,
                    post=post
                )
            post.save()
            return JsonResponse({'message': 'Successfully'}, status=200)
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
