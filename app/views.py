from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from .models import Assistant
import json
import math
from django.utils import timezone
from .models import User, PendingRequest
def haversine_distance(lat1, lon1, lat2, lon2):
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
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            
            try:
                user = User.objects.get(email=email)
                
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
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Check if user already exists
            if User.objects.filter(email=data.get('email')).exists():
                return JsonResponse({'error': 'Email already exists'}, status=409)
            
            # Create new user
            user = User.objects.create(
                name=data.get('name'),
                email=data.get('email'),
                password=make_password(data.get('password')),
                user_name=data.get('userName', data.get('email').split('@')[0]),
                address=data.get('address'),
                dob=data.get('dob') and timezone.datetime.fromisoformat(data.get('dob')),
                gender=data.get('gender'),
                number=data.get('number'),
                profile_picture=data.get('profilePicture'),
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
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            try:
                user = User.objects.get(user_id=data.get('userId'))
                
                pending_request = PendingRequest.objects.create(
                    user=user,
                    latitude=data.get('latitude'),
                    longitude=data.get('longitude'),
                    status='pending',
                    notified=0
                )
                
                return JsonResponse({
                    'message': 'Request sent',
                    'request_id': pending_request.id
                }, status=201)
            
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def get_pending_requests(request):
    if request.method == 'GET':
        try:
            latitude = float(request.GET.get('latitude'))
            longitude = float(request.GET.get('longitude'))
            
            # Get all pending requests
            all_requests = PendingRequest.objects.filter(status='pending')
            
            # Filter requests within 3000 meters
            nearby_requests = []
            for req in all_requests:
                distance = haversine_distance(latitude, longitude, req.latitude, req.longitude)
                if distance <= 3000:
                    nearby_requests.append(req)
            
            if not nearby_requests:
                return JsonResponse({'message': 'No nearby requests'}, status=204)
            
            # Return the first nearby request
            first_request = nearby_requests[0]
            return JsonResponse({
                'id': first_request.id,
                'userId': first_request.user.user_id,
                'latitude': first_request.latitude,
                'longitude': first_request.longitude,
            }, status=200)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def confirm_request(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            request_id = data.get('requestId')
            assistant_id = data.get('assistantId')
            
            try:
                pending_request = PendingRequest.objects.get(id=request_id)
                assistant = Assistant.objects.get(id=assistant_id)
                
                # Check if request is already accepted
                if pending_request.status == 'accepted':
                    return JsonResponse({'error': 'Request already accepted'}, status=400)
                
                # Update request
                pending_request.status = 'accepted'
                pending_request.assistant = assistant
                pending_request.save()
                
                return JsonResponse({'message': 'Request accepted'}, status=200)
            
            except PendingRequest.DoesNotExist:
                return JsonResponse({'error': 'Request not found'}, status=404)
            except Assistant.DoesNotExist:
                return JsonResponse({'error': 'Assistant not found'}, status=404)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

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
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Check if assistant already exists
            if Assistant.objects.filter(email=data.get('email')).exists():
                return JsonResponse({'error': 'Email already exists'}, status=409)
            
            # Create new assistant
            assistant = Assistant.objects.create(
               name=data.get('name'),
                email=data.get('email'),
                password=data.get('password'),
                dob=data.get('dob'),
                gender=data.get('gender'),
                profile_picture=data.get('profile_picture'),
                number=data.get('number'),
                address=data.get('address'),
                id_document=data.get('id_document'),
                latitude=data.get('latitude'),
                longitude=data.get('longitude')
            )
            assistant.save()
            return JsonResponse({
                'message': 'Assistant registered successfully',
                'assistant_id': assistant.assistant_id
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

