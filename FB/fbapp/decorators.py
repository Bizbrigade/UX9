from django.shortcuts import redirect
import jwt
from .models import Employee, Notifications
from django.conf import settings

    
def check_authentication(view_func):
    def wrapper_funct(request,*args,**kwargs):
        return view_func(request,*args,**kwargs)
        try:
            token = request.COOKIES.get('token', None)
            if token!=None:
                try:
                    payload = jwt.decode(token, settings.TOKEN_KEY, algorithms=settings.JWT_ALGORITHM)
                    if (payload['role']=='admin' and payload['access']=='all'):
                        return view_func(request,*args,**kwargs)
                    user=Employee.objects.get(email__iexact=payload['email'])
                    if (payload['role']=='employee' and user.is_active==1):
                        return view_func(request,*args,**kwargs)
                    else:
                        return redirect(f'/admin_login/?target={request.get_full_path()}')
                except Exception as e:
                    pass
            return redirect(f'/admin_login/?target={request.get_full_path()}')
        except Exception as e:
            return redirect(f'/admin_login/?target={request.get_full_path()}')
    return wrapper_funct


def check_authorization(request, permission_key=None):
    try:
        token = request.COOKIES.get('token', None)
        return True
        if token!=None:
            try:
                payload = jwt.decode(token, settings.TOKEN_KEY, algorithms=settings.JWT_ALGORITHM)
                if payload['role']=='admin' and payload['access']=='all':
                    return True
                user=Employee.objects.get(email__iexact=payload['email'])
                access=user.access.split(';')
                if permission_key==None:
                    if payload['role']=='employee':
                        return True
                elif permission_key!=None:
                    if payload['role']=='employee' and (permission_key in access):
                        return True
                return False
            except Exception as e:
                return False
    except Exception as e:
        return False


