from rest_framework import serializers
from .models import Listing, Booking, Review
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = UserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'listing', 'reviewer', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']

class ListingSerializer(serializers.ModelSerializer):
    host = UserSerializer(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'address', 'city', 'country',
            'price_per_night', 'bedrooms', 'bathrooms', 'max_guests',
            'property_type', 'amenities', 'images', 'host', 'is_available',
            'created_at', 'updated_at', 'reviews', 'average_rating'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return None

class BookingSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    guest = UserSerializer(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(), 
        write_only=True, 
        source='listing'
    )
    
    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'listing_id', 'guest', 'check_in_date', 
            'check_out_date', 'guests_count', 'total_price', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at', 'updated_at']
    
    def validate(self, data):
        """
        Check that check_out_date is after check_in_date and the listing is available
        """
        if data['check_out_date'] <= data['check_in_date']:
            raise serializers.ValidationError("Check-out date must be after check-in date")
        
        if not data['listing'].is_available:
            raise serializers.ValidationError("This listing is not available for booking")
        
        # Check if there are any overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            listing=data['listing'],
            status__in=['pending', 'confirmed'],
            check_in_date__lte=data['check_out_date'],
            check_out_date__gte=data['check_in_date']
        )
        
        if self.instance:
            overlapping_bookings = overlapping_bookings.exclude(id=self.instance.id)
            
        if overlapping_bookings.exists():
            raise serializers.ValidationError("This listing is already booked for the selected dates")
        
        return data
    
    def create(self, validated_data):
        # Calculate total price based on number of nights and price per night
        check_in = validated_data['check_in_date']
        check_out = validated_data['check_out_date']
        nights = (check_out - check_in).days
        price_per_night = validated_data['listing'].price_per_night
        validated_data['total_price'] = nights * price_per_night
        
        # Set the guest to the current user
        validated_data['guest'] = self.context['request'].user
        
        return super().create(validated_data)