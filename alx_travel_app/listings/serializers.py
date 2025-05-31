from .models import Property, Review, Booking, User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'user_id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'role',
            'created_at'
        ]
        read_only_fields = ['user_id', 'created_at']


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = [
            'property_id',
            'host_id',
            'name',
            'description',
            'location',
            'price_per_night',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['property_id', 'host_id', 'created_at', 'updated_at']  # Added missing comma

    def create(self, validated_data):
        validated_data['host_id'] = self.context['request'].user
        return super().create(validated_data)

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'review_id',
            'property_id',
            'user_id',
            'rating',
            'comment',
            'created_at'
        ]

        read_only_fields = ['review_id', 'created_at']


class BookingSerializer(serializers.ModelSerializer):
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = [
            'booking_id',
            'property_id',
            'user_id',
            'start_date',
            'end_date',
            'created_at'
        ]

        read_only_fields = ['booking_id', 'total_price', 'created_at']