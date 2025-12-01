from rest_framework import serializers
from apps.catalyst_app.models import User, Company, Subscription


class CompanySerializer(serializers.ModelSerializer):
    """Serializador para la empresa"""
    
    class Meta:
        model = Company
        fields = ['id', 'name', 'rut', 'email', 'phone', 'address', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializador para suscripción/plan"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    plan_display = serializers.CharField(source='get_plan_name_display', read_only=True)
    
    class Meta:
        model = Subscription
        fields = ['id', 'company', 'company_name', 'plan_name', 'plan_display', 
                  'start_date', 'end_date', 'active', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializador básico para usuario"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 
                  'role_display', 'rut', 'company', 'company_name', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializador para crear usuarios con password"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 
                  'last_name', 'role', 'rut']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado para usuario con información adicional"""
    company = CompanySerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 
                  'role_display', 'rut', 'company', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
