from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from django.views.generic import CreateView
from apps.users.models import Profile
from apps.users.forms import SigninForm, SignupForm, UserPasswordChangeForm, UserSetPasswordForm, UserPasswordResetForm, ProfileForm
from django.contrib.auth import logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from apps.users.utils import user_filter, profile_user_filter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterUserSerializer, LoginSerializer, UpdateProfileSerializer, AppleUserSerializer
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework.authentication import TokenAuthentication

# Create your views here.

class SignInView(LoginView):
    form_class = SigninForm
    template_name = "authentication/sign-in.html"

class SignUpView(CreateView):
    form_class = SignupForm
    template_name = "authentication/sign-up.html"
    success_url = "/users/signin/"

class UserPasswordChangeView(PasswordChangeView):
    template_name = 'authentication/password-change.html'
    form_class = UserPasswordChangeForm

class UserPasswordResetView(PasswordResetView):
    template_name = 'authentication/forgot-password.html'
    form_class = UserPasswordResetForm

class UserPasswrodResetConfirmView(PasswordResetConfirmView):
    template_name = 'authentication/reset-password.html'
    form_class = UserSetPasswordForm


def signout_view(request):
    logout(request)
    return redirect(reverse('signin'))


@login_required(login_url='/users/signin/')
def profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
    else:
        form = ProfileForm(instance=profile)
    
    context = {
        'form': form,
        'segment': 'profile',
    }
    return render(request, 'dashboard/profile.html', context)


def upload_avatar(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        profile.avatar = request.FILES.get('avatar')
        profile.save()
        messages.success(request, 'Avatar uploaded successfully')
    return redirect(request.META.get('HTTP_REFERER'))


def change_password(request):
    user = request.user
    if request.method == 'POST':
        if check_password(request.POST.get('current_password'), user.password):
            user.set_password(request.POST.get('new_password'))
            user.save()
            messages.success(request, 'Password changed successfully')
        else:
            messages.error(request, "Password doesn't match!")
    return redirect(request.META.get('HTTP_REFERER'))

def user_list(request):
    filters = profile_user_filter(request)

    profile_list = Profile.objects.select_related('user').filter(**filters)
    form = SignupForm()

    page = request.GET.get('page', 1)
    paginator = Paginator(profile_list, 5)
    profiles = paginator.page(page)

    if request.method == 'POST':
        print(request.POST)
        form = SignupForm(request.POST)
        if form.is_valid():
            return post_request_handling(request, form)
        else:
            print("Form errors:", form.errors)

    context = {
        'users': profiles,
        'form': form,
    }
    return render(request, 'apps/users.html', context)



@login_required(login_url='/users/signin/')
def post_request_handling(request, form):
    user = form.save()
    Profile.objects.create(user=user)
    return redirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='/users/signin/')
def delete_user(request, id):
    profile = get_object_or_404(Profile, id=id)
    user = profile.user
    user.delete()  # This also deletes the profile due to CASCADE

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='/users/signin/')
def update_user(request, id):
    profile = get_object_or_404(Profile, id=id)
    user = profile.user

    if request.method == 'POST':
        # Update User fields
        user.username = request.POST.get('username')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()

        # Optionally update Profile fields (if included in form)
        profile.country = request.POST.get('country', profile.country)
        profile.city = request.POST.get('city', profile.city)
        profile.address = request.POST.get('address', profile.address)
        profile.phone = request.POST.get('phone', profile.phone)
        profile.role = request.POST.get('role', profile.role)

        # Handle avatar if file is uploaded
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        profile.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='/users/signin/')
def user_change_password(request, id):
    user = User.objects.get(id=id)
    if request.method == 'POST':
        user.set_password(request.POST.get('password'))
        user.save()
    return redirect(request.META.get('HTTP_REFERER'))


# {
#   "username": "radhika",
#   "first_name": "Radhika",
#   "last_name": "Soni",
#   "email": "radhika@gmail.com",
#   "role": "user",
#   "city": "New York",
#   "country": "USA",
#   "phone": "1234567890",
#   "zip_code": "10001",
#   "address": "123 Main Street",
#   "password": "testpassword123"
# }

# {
#     "message": "User registered successfully",
#     "username": "radhika",
#     "email": "radhika@gmail.com",
#     "token": "d0e7ceebc59195308ea1a123a5646550587fa436"
# }

class RegisterUserView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterUserSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                "status": True,
                "message": "Registered Successfully",
                "data": {
                    "username": user.username,
                    "email": user.email,
                },
                "token": token.key
            }, status=status.HTTP_201_CREATED)

        except IntegrityError as e:                       # duplicate email/username etc.
            return Response({
                "status": False,
                "message": "Duplicate user",
                "errors": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:        # serializer errors
            flat = {
                field: " ".join(msgs) if isinstance(msgs, (list, tuple)) else str(msgs)
                for field, msgs in e.detail.items()
            }

            # 2. If BOTH username & email duplicates → craft combined message
            if {"username", "email"} <= flat.keys() and all("already exists" in v for v in flat.values()):
                combined = "A user with this username and email already exists."
            else:
                # Fallback: stitch all unique messages together
                combined = " ".join(dict.fromkeys(flat.values()))  # preserves order, removes dupes

            return Response({
                "status": False,
                "message": "Validation Error",
                "errors": combined
            }, status=status.HTTP_201_CREATED)

        except Exception as e:                            # fallback
            return Response({
                "status": False,
                "message": "Unexpected Error",
                "errors": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# {
#   "username": "radhika",
#   "password": "testpassword123"
# }

# {
#     "message": "Login successful",
#     "token": "d0e7ceebc59195308ea1a123a5646550587fa436",
#     "username": "radhika",
#     "email": "radhika@gmail.com"
# }

class LoginUserView(APIView):
    """
    Returns uniform JSON:
    {
        "status": true/false,
        "message": "...",
        "token": "abc",      # on success
        "errors": "..."      # on error
    }
    """
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            # ------------------ validate input ------------------
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            

            # Serializer may already attach user (see earlier example),
            # otherwise authenticate manually:
            user = serializer.validated_data.get("user") or authenticate(
                email=serializer.validated_data.get("email"),
                password=serializer.validated_data.get("password")
            )

            if not user:
                return Response({
                    "status": False,
                    "message": "Invalid credentials",
                    "errors": "Incorrect email or password."
                }, status=status.HTTP_401_UNAUTHORIZED)

            # ------------------ profile checks ------------------
            profile: Profile = user.profile
            if profile.status == "suspended":
                return Response({
                    "status": False,
                    "message": "Account Suspended",
                    "errors": "This account is suspended."
                }, status=403)

            if profile.status == "deleted":
                return Response({
                    "status": False,
                    "message": "Account Deleted",
                    "errors": "This account has been deleted."
                }, status=403)

            # Activate user on login
            profile.status = "active"
            profile.save()

            # ------------------ success ------------------
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "status": True,
                "message": "Login successful",
                "token": token.key,
                "username": user.username,
                "email": user.email,
            }, status=status.HTTP_200_OK)

        # ------------------ validation errors ------------------
        except ValidationError as e:
            flat = {
                field: " ".join(msgs) if isinstance(msgs, (list, tuple)) else str(msgs)
                for field, msgs in e.detail.items()
            }
            # Merge messages into readable sentence
            combined = " ".join(dict.fromkeys(flat.values()))
            return Response({
                "status": False,
                "message": "Validation Error",
                "errors": combined
            }, status=status.HTTP_400_BAD_REQUEST)

        # ------------------ other DB / logic errors -------------
        except IntegrityError as e:
            return Response({
                "status": False,
                "message": "Database Error",
                "errors": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # ------------------ fallback ----------------------------
        except Exception as e:
            return Response({
                "status": False,
                "message": "Unexpected Error",
                "errors": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# {
#   "apple_id": "001025.44a3a4e14fae4b51a2e7bc437c58db3c.0100",
#   "email": "user@example.com",
#   "first_name": "John",
#   "last_name": "Appleseed"
# }
class AppleRegisterOrLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = AppleUserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            apple_id = serializer.validated_data['apple_id']
            email = serializer.validated_data.get('email')
            first_name = serializer.validated_data.get('first_name', '')
            last_name = serializer.validated_data.get('last_name', '')

            profile = Profile.objects.filter(apple_id=apple_id).first()

            if profile:
                user = profile.user
                message = "User logged in successfully"
            else:
                # Create new user and profile
                username = f"apple_{apple_id[:10]}"
                user = User.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
                Profile.objects.create(user=user, apple_id=apple_id)
                message = "User registered successfully"

            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                "status": True,
                "message": message,
                "data": {
                    "username": user.username,
                    "email": user.email
                },
                "token": token.key
            }, status=status.HTTP_200_OK)

        except IntegrityError as e:
            return Response({
                "status": False,
                "message": "Duplicate entry",
                "errors": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            flat = {
                field: " ".join(msgs) if isinstance(msgs, (list, tuple)) else str(msgs)
                for field, msgs in e.detail.items()
            }
            combined = " ".join(dict.fromkeys(flat.values()))
            return Response({
                "status": False,
                "message": "Validation Error",
                "errors": combined
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": False,
                "message": "Unexpected Error",
                "errors": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutUserView(APIView):
    # authentication_classes = [TokenAuthentication]   # <- explicit
    permission_classes     = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user  # Retrieved via token
            try:
                token = Token.objects.get(user=user)
                token.delete()
            except Token.DoesNotExist:
                return Response({
                    "status": False,
                    "message": "Token missing",
                    "errors": "User is not logged in or token does not exist."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Update profile status if available
            try:
                profile = user.profile
                profile.status = 'logged_out'
                profile.save()
            except ObjectDoesNotExist:
                pass  # Optional: log missing profile

            return Response({
                "status": True,
                "message": f"User '{user.username}' logged out successfully"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": False,
                "message": "Unexpected error",
                "errors": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # for avatar/image


    def put(self, request):
        identifier = request.data.get('username') or request.data.get('email')

        if not identifier:
            return Response({'error': 'Username or email is required to identify the user.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Find user by username or email
            user = User.objects.get(username=identifier) if 'username' in request.data else User.objects.get(email=identifier)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            profile = user.profile
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.update(user, profile, serializer.validated_data)
            return Response({"message": "Profile updated successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


