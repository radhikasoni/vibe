from rest_framework import serializers
from .models import Profile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class RegisterUserSerializer(serializers.ModelSerializer):
    # Include profile fields
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    role = serializers.ChoiceField(choices=[('admin', 'Admin'), ('user', 'User')], default='user')
    country = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    zip_code = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    avatar = serializers.ImageField(required=False, allow_null=True)

    password = serializers.CharField(write_only=True, min_length=6)

    apple_id = serializers.CharField(required=False, allow_blank=True)
    is_apple_user = serializers.BooleanField(required=False, default=False)



    class Meta:
        model = User
        fields = ['username', 'email', 'password',
                  'first_name', 'last_name', 'role', 'country', 'city',
                  'zip_code', 'address', 'phone', 'avatar', 'apple_id', 'is_apple_user']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def create(self, validated_data):
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        profile_fields = {
            'role': validated_data.pop('role', 'user'),
            'country': validated_data.pop('country', ''),
            'city': validated_data.pop('city', ''),
            'zip_code': validated_data.pop('zip_code', ''),
            'address': validated_data.pop('address', ''),
            'phone': validated_data.pop('phone', ''),
            'avatar': validated_data.pop('avatar', None),
            'apple_id': validated_data.pop('apple_id', None),
            'is_apple_user': validated_data.pop('is_apple_user', False)
        }

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name
        )

        Profile.objects.create(user=user, **profile_fields)

        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    apple_id = serializers.CharField(required=False)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        apple_id = data.get('apple_id')

        if apple_id:
            try:
                profile = Profile.objects.get(apple_id=apple_id)
                data['user'] = profile.user
            except Profile.DoesNotExist:
                raise serializers.ValidationError("Invalid Apple ID.")
        else:
            if not email or not password:
                raise serializers.ValidationError("Email and password are required.")
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials.")
            data['user'] = user

        return data

class AppleUserSerializer(serializers.Serializer):
    apple_id = serializers.CharField(required=True)
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

class UpdateProfileSerializer(serializers.Serializer):
    # User fields
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    # Profile fields
    role = serializers.ChoiceField(choices=[('admin', 'Admin'), ('user', 'User')], required=False)
    country = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    zip_code = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    avatar = serializers.ImageField(required=False, allow_null=True)

    def update(self, user, profile, validated_data):
        # Separate fields for user and profile
        user_fields = ['username', 'email', 'first_name', 'last_name']
        profile_fields = ['role', 'country', 'city', 'zip_code', 'address', 'phone', 'avatar']

        # Update user fields
        for field in user_fields:
            value = validated_data.get(field, None)
            if value is not None:
                setattr(user, field, value)
        user.save()

        # Update profile fields
        for field in profile_fields:
            value = validated_data.get(field, None)
            if value is not None:
                setattr(profile, field, value)
        profile.save()

        return user  # optional, for chaining or logging