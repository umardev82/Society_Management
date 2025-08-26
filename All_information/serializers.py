
from rest_framework import serializers
from .models import AreaType, BillsSetup, Block_info, Complaint, Currency, Fine, Floor, FormBuilder, MaintenanceCost, ManagementCommittee, MemberTypeSetup, PaymentsCollection,Property_info, PropertyDocument,PropertyType, Tenant,UnitType,Amenity,Service,Owner, OwnerProperty
from rest_framework.exceptions import ValidationError

class Block_info_serlializer(serializers.ModelSerializer):
    class Meta:
        model = Block_info  # Change 'models' to 'model'
        fields = ['id', 'block_name']  
        
class Property_type_serializer(serializers.ModelSerializer):
    class Meta:
        model =PropertyType
        fields=['pro_type_id','property_name']   
 
class Unit_type_serializer(serializers.ModelSerializer):
    class Meta:
        model =UnitType
        fields= ['unit_type_id','unit_number','unit_name']   
        
class Amenity_serializer(serializers.ModelSerializer):
    class Meta:
        model= Amenity
        fields =['amenity_id','amenity_name']    
        
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'        
        
class AreaTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaType
        fields = ['area_type_id', 'area_type_name', 'area_value']   
        
 #Floor Serializer
class FloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = ['id', 'name']     

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model= Currency
        fields=['id','name','symbol','status']
        # optional: Serializer Validation
    # def validate(self, data):
    #     if data.get('status') == 'active':
    #         if Currency.objects.filter(status='active').exclude(pk=self.instance.pk if self.instance else None).exists():
    #             raise serializers.ValidationError("Only one currency can be active at a time.")
    #     return data    
        
class PropertyDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model =PropertyDocument
        fields=['id', 'file', 'uploaded_at']               
       
class Property_info_serializer_for_display_data(serializers.ModelSerializer):
    block_name = Block_info_serlializer()
    property_type = Property_type_serializer()
    unit_type = Unit_type_serializer()
    amenity_name = Amenity_serializer(many=True)
    property_area = AreaTypeSerializer() 
    property_value = CurrencySerializer()
    floor=FloorSerializer()
    documents =PropertyDocumentSerializer(many=True,read_only=True)
    
    class Meta:
        model = Property_info
        fields = '__all__' 
        
    
        
class Property_info_serializer(serializers.ModelSerializer):
    # block_name = Block_info_serlializer()
    documents = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )
    property_value = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.filter(status='active'),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Property_info
        fields = [
            'property_id',
            'block_name',
            'building_name',
            'property_name',
            'property_type',
            'property_number',
            'unit_type',
            'floor',
            'number_of_bedrooms',
            'number_of_bathrooms',
            'balcony_or_patio',
            'parking_space',
            'number_of_halls',
            'street_address',
            'property_area',
            'property_value',
            'any_note',
            'amenity_name',
            'is_active',  # New field for Active/In-Active
            'documents',  # New field for Document Attachment
            'is_rented',  # New field for Rented (Yes/No)
        ]
    
    
    def create(self, validated_data):
     files = validated_data.pop('documents', [])
     amenities = validated_data.pop('amenity_name', [])

     property_info = Property_info.objects.create(**validated_data)

     if amenities:
        property_info.amenity_name.set(amenities)

     for f in files:
        PropertyDocument.objects.create(property=property_info, file=f)

     return property_info
     
     
    def update(self, instance, validated_data):
     files = validated_data.pop('documents', [])

     for attr, value in validated_data.items():
        if attr == 'amenity_name':
            # For ManyToMany: use .set()
            instance.amenity_name.set(value)
        else:
            setattr(instance, attr, value)

     instance.save()

     for f in files:
        PropertyDocument.objects.create(property=instance, file=f)

     return instance
 
  
        
        
class OwnerPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = OwnerProperty
        fields = ['owner', 'property_info', 'status']


class Owner_display_info_Serializer(serializers.ModelSerializer):
    properties = serializers.SerializerMethodField()

    class Meta:
        model = Owner
        fields = [
            'owner_id',
            'owner_name',
            'secondary_owner',
            'third_owner',
            'owner_guardian_name',
            'owner_profile_picture',
            'owner_phone_number',
            'password',
            'owner_email',
            'owner_membership_number',
            'owner_cnic',
            'owner_address',
            'owner_country',
            'owner_city',
            'status',
            'document_attachment',
            'properties',
        ]

    def get_properties(self, obj):
        # Only fetch properties where status is active
        owner_properties = OwnerProperty.objects.filter(owner=obj, status='active')
        properties = [op.property_info for op in owner_properties]
        return Property_info_serializer_for_display_data(properties, many=True).data


   
class OwnerSerializer(serializers.ModelSerializer):
    properties = serializers.PrimaryKeyRelatedField(many=True, queryset=Property_info.objects.all(), required=False)
    properties = serializers.PrimaryKeyRelatedField(many=True,queryset=Property_info.objects.all(),required=False)
    class Meta:
        model = Owner
        fields = [
            'owner_id',
            'owner_name',
            'secondary_owner',
            'third_owner',
            'owner_guardian_name',
            'owner_profile_picture',
            'owner_phone_number',
            'password',
            'owner_email',
            'owner_membership_number',
            'owner_cnic',
            'owner_address',
            'owner_country',
            'owner_city',
            'status',
            'document_attachment',
            'properties',
        ]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Get only active properties assigned to this owner
        assigned_props = OwnerProperty.objects.filter(owner=instance, status='active').values_list('property_info_id', flat=True)
        data['properties'] = list(assigned_props)  # This will return [1, 2, 3]
        return data
    
    
    def validate_properties(self, value):
        for property_obj in value:
            # Check if another active owner already exists
            active_ownership = OwnerProperty.objects.filter(
                property_info=property_obj,
                status='active'
            ).exclude(owner=self.instance).first()

            if active_ownership:
                raise ValidationError(
                    f"Property '{property_obj.property_name}' is already assigned to active owner '{active_ownership.owner.owner_name}'."
                )
        return value

    def create(self, validated_data):
        properties = validated_data.pop('properties', [])
        owner = super().create(validated_data)

        for property_obj in properties:
            OwnerProperty.objects.update_or_create(
                owner=owner,
                property_info=property_obj,
                defaults={'status': 'active'}
            )
        return owner

    def update(self, instance, validated_data):
     properties = validated_data.pop('properties', [])
     owner = super().update(instance, validated_data)

     # Step 1: Mark existing property relations as inactive (do NOT delete)
     OwnerProperty.objects.filter(owner=owner).update(status='inactive')

     # Step 2: Add or update the new properties to active
     for property_obj in properties:
        # Check if another active owner has this property (enforce single active owner)
        active_owner = OwnerProperty.objects.filter(
            property_info=property_obj,
            status='active'
        ).exclude(owner=owner).first()

        if active_owner:
            raise serializers.ValidationError(
                f"Property '{property_obj.property_name}' is already assigned to active owner '{active_owner.owner.owner_name}'."
            )

        # Create or update this owner-property as active
        OwnerProperty.objects.update_or_create(
            owner=owner,
            property_info=property_obj,
            defaults={'status': 'active'}
        )

     return owner
 
 
 

 
 
#Property Transfer Serializer for owner 

class PropertyTransferSerializer(serializers.Serializer):
    property_id = serializers.PrimaryKeyRelatedField(queryset=Property_info.objects.all())
    new_owner_id = serializers.PrimaryKeyRelatedField(queryset=Owner.objects.all())

    def validate(self, data):
        property_obj = data['property_id']
        new_owner = data['new_owner_id']

        # Check if this property is already assigned to another active owner
        existing_active = OwnerProperty.objects.filter(property_info=property_obj, status='active').exclude(owner=new_owner).first()
        if existing_active:
            raise serializers.ValidationError(f"This property is already assigned to another active owner: {existing_active.owner.owner_name}")

        return data

    def save(self):
        property_obj = self.validated_data['property_id']
        new_owner = self.validated_data['new_owner_id']

        # Step 1: Mark current active record as inactive
        OwnerProperty.objects.filter(property_info=property_obj, status='active').update(status='inactive')

        # Step 2: Assign new owner as active
        OwnerProperty.objects.update_or_create(
            owner=new_owner,
            property_info=property_obj,
            defaults={'status': 'active'}
        )
        return {"message": "Property transferred successfully"}



# Property Splitter Serializer

class SubPropertyInputSerializer(serializers.Serializer):
    property_name = serializers.CharField(max_length=200)
    area_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    area_type_id = serializers.IntegerField()

class PropertySplitterSerializer(serializers.Serializer):
    base_property_id = serializers.IntegerField()
    sub_properties = SubPropertyInputSerializer(many=True)

    def validate(self, data):
        try:
            Property_info.objects.get(property_id=data['base_property_id'])
        except Property_info.DoesNotExist:
            raise serializers.ValidationError("Base property does not exist.")
        return data



    
class Tenant_display_info_Serializer(serializers.ModelSerializer):
    assign_property = Property_info_serializer_for_display_data()
    
    class Meta:
        model = Tenant
        fields = '__all__'  
class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = [
            'tenant_id',
            'tenant_name',
            'tenant_guardian_name',
            'tenant_profile_picture',
            'tenant_phone_number',
            'password',
            'tenant_email',
            'tenant_cnic',
            'tenant_address',
            'tenant_city',
            'tenant_country',
            'starting_date',
            'ending_agreement_date',
            'monthly_rent',
            'security_payment',
            'other_monthly_utility_charges',
            'assign_property',
            'agreement_attachment',
        ]   
class FormBuilderSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormBuilder
        fields = '__all__'  # This will include all fields from the FormBuilder model

        
class BillsSetupDisplaySerializer(serializers.ModelSerializer):
    form = FormBuilderSerializer(read_only=True)
    floor=FloorSerializer()
    class Meta:
        model = BillsSetup
        fields = ['bill_setup_id', 'form', 'form_id','property_type_name', 'property_area', 'property_number','floor', 'form_data']

    def validate_charges(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Charges must be a dictionary of key-value pairs.")
        return value                       
class BillsSetupSerializer(serializers.ModelSerializer):

    form_id = serializers.PrimaryKeyRelatedField(queryset=FormBuilder.objects.all(), source='form')
    
    class Meta:
        model = BillsSetup
        fields = ['bill_setup_id', 'form', 'form_id','property_type_name', 'property_area', 'property_number','floor', 'form_data']

    def validate_charges(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Charges must be a dictionary of key-value pairs.")
        return value
# class BillsSetupDisplaySerializer(serializers.ModelSerializer):
#     property_type_name = Property_type_serializer()
#     property_area = AreaTypeSerializer() 
#     class Meta:
#         model = BillsSetup
#         fields = ['bill_setup_id', 'property_type_name', 'property_area', 'property_number', 'charges']

#     def validate_charges(self, value):
#         if not isinstance(value, dict):
#             raise serializers.ValidationError("Charges must be a dictionary of key-value pairs.")
#         return value  
        
# class BillsSetupSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BillsSetup
#         fields = ['bill_setup_id', 'property_type_name', 'property_area', 'property_number', 'charges']

#     def validate_charges(self, value):
#         if not isinstance(value, dict):
#             raise serializers.ValidationError("Charges must be a dictionary of key-value pairs.")
#         return value        
 
 
class MemberTypeSetupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberTypeSetup
        fields = '__all__'

class ManagementCommitteeDisplaySerializer(serializers.ModelSerializer):
    mc_member_type = MemberTypeSetupSerializer() 

    class Meta:
        model = ManagementCommittee
        fields = '__all__'    
        
class ManagementCommitteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagementCommittee
        fields = '__all__'
        
      
class MaintenanceCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceCost
        fields = '__all__' 




class PaymentsCollectionDisplaySerializer(serializers.ModelSerializer):
    # block_name = serializers.StringRelatedField()
    block_name = Block_info_serlializer()
    property_numbers = serializers.SerializerMethodField()
    form = serializers.PrimaryKeyRelatedField(queryset=FormBuilder.objects.all())
    
    class Meta:
        model = PaymentsCollection
        fields = ['id','form','payments_collection_mode','block_name', 'property_number', 'property_numbers', 'name_id', 'month','year', 'bills_fields','monthly_rent','total_current_bills', 'balance','currect_balance','paid_amount', 'bill_status', 'issue_date', 'due_date']

    def get_property_numbers(self, instance):
        block_name = self.context.get('block_name')
        if block_name:
            # Fetch all property numbers based on the selected block
            properties = Property_info.objects.filter(block_name=block_name)
            return [property.property_number for property in properties]
        return []

    def validate_property_number(self, value):
        # Check if the property number exists
        if not Property_info.objects.filter(property_number=value).exists():
            raise ValidationError("Invalid property number.")
        return value

class PaymentsCollectionSerializer(serializers.ModelSerializer):
    block_name = serializers.PrimaryKeyRelatedField(queryset=Block_info.objects.all())
    property_numbers = serializers.SerializerMethodField()
    form = serializers.PrimaryKeyRelatedField(queryset=FormBuilder.objects.all())
    
    class Meta:
        model = PaymentsCollection
        fields = ['id','form','payments_collection_mode','block_name', 'property_number', 'property_numbers', 'name_id', 'month','year', 'bills_fields','monthly_rent','total_current_bills', 'balance','currect_balance','paid_amount', 'bill_status', 'issue_date', 'due_date']

    def get_property_numbers(self, instance):
        block_name = self.context.get('block_name')
        if block_name:
            # Fetch all property numbers based on the selected block
            properties = Property_info.objects.filter(block_name=block_name)
            return [property.property_number for property in properties]
        return []

    def validate_property_number(self, value):
        # Check if the property number exists
        if not Property_info.objects.filter(property_number=value).exists():
            raise ValidationError("Invalid property number.")
        return value


class FineSerializer(serializers.ModelSerializer):
    class Meta:
        model=Fine
        fields=['id','fine']
        
        
        
class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ['id', 'title', 'description', 'status', 'image', 'user_id', 'created_at']
        read_only_fields = ['user_id', 'created_at']        
        
        