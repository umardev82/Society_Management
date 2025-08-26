from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# from django.contrib.auth.models import User
from django.db.models import UniqueConstraint

from user_management.models import User

class Block_info(models.Model):
    block_name=models.CharField(max_length=100)
    
    def __str__(self):
        return self.block_name
    
    

# add  PropertyType Model
class PropertyType(models.Model):
    pro_type_id = models.AutoField(primary_key=True)
    property_name = models.CharField(max_length=100)


    def __str__(self):
        return f" {self.property_name} "
   
    
    # add  UnitType Model
class UnitType(models.Model):
    unit_type_id = models.AutoField(primary_key=True)
    unit_number = models.IntegerField(unique=True)  # Ensures uniqueness
    unit_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.unit_number} - {self.unit_name}"    
    
    
 # add  Amenity Model  
class Amenity(models.Model):
    amenity_id = models.AutoField(primary_key=True)
    amenity_name = models.CharField(max_length=100)  # Name of the amenity (e.g., Gym, Pool, etc.)
   

    def __str__(self):
        return self.amenity_name 
    
class AreaType(models.Model):
    area_type_id = models.AutoField(primary_key=True)
    AREA_TYPE_CHOICES = [
        ('SQFT', 'Square Feet (SQFT)'),
        ('MARLA', 'Marla'),
        ('KANAL', 'Kanal'),
    ]
    area_type_name = models.CharField(max_length=10, choices=AREA_TYPE_CHOICES,null=True, blank=True)
    area_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
       return f"{self.area_type_name} - {self.area_value}"
       
class Service(models.Model):
    service_id = models.AutoField(primary_key=True)
    service_name = models.CharField(max_length=100)

    def __str__(self):
        return self.name



# add Floor Model

class Floor(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Currency(models.Model):
    name = models.CharField(max_length=50, unique=True)
    symbol = models.CharField(max_length=10, unique=True)
    status = models.CharField(max_length=10, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='Inactive')

    def save(self, *args, **kwargs):
        if self.status == 'active':
            # Deactivate all other currencies
            Currency.objects.exclude(pk=self.pk).update(status='inactive')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.symbol})"




# add Property_info Model
class Property_info(models.Model):
    property_id = models.AutoField(primary_key=True)
    block_name = models.ForeignKey('Block_info', on_delete=models.CASCADE)
    building_name = models.CharField(max_length=200)
    property_name = models.CharField(max_length=200)
    property_type = models.ForeignKey(PropertyType, on_delete=models.CASCADE)
    property_number = models.CharField(max_length=200,null=True,unique=True)  # Ensures uniqueness
    floor = models.ForeignKey('Floor', on_delete=models.SET_NULL, null=True, blank=True)
    unit_type = models.ForeignKey('UnitType', on_delete=models.CASCADE)
    number_of_bedrooms = models.PositiveIntegerField()
    number_of_bathrooms = models.PositiveIntegerField()
    balcony_or_patio = models.CharField(max_length=3, choices=[('No', 'No'), ('Yes', 'Yes')], default='No')
    parking_space = models.CharField(max_length=3, choices=[('No', 'No'), ('Yes', 'Yes')], default='No')
    number_of_halls = models.PositiveIntegerField()
    street_address = models.CharField(max_length=255, null=True, blank=True)
    property_area = models.ForeignKey('AreaType', on_delete=models.CASCADE,null=True, blank=True)
    property_value = models.ForeignKey('Currency',on_delete=models.SET_NULL,null=True, blank=True)                  
    any_note = models.CharField(max_length=500,null=True, blank=True)
    amenity_name =models.ManyToManyField('Amenity',blank=True)
    is_active = models.BooleanField(default=True)  # Active/In-Active field
    # document_attachment = models.FileField(upload_to='documents/', null=True, blank=True)  # Document attachment
    is_rented = models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False)  # Rented (Yes/No)
        
    def __str__(self):
     return (
        f" ({self.property_number}) - "
        f" {self.block_name.block_name}"
    )

    
class PropertyDocument(models.Model):
    property = models.ForeignKey(Property_info, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)    

#add owner models

class Owner(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    owner_id = models.AutoField(primary_key=True)
    owner_name = models.CharField(max_length=200)
    secondary_owner=models.CharField(max_length=200 ,null=True, blank=True)
    third_owner=models.CharField(max_length=200,null=True, blank=True)
    owner_guardian_name = models.CharField(max_length=200, null=True, blank=True)
    owner_profile_picture = models.ImageField(upload_to='owner_profile_pictures/', null=True, blank=True)
    owner_phone_number = models.CharField(max_length=15)
    password = models.CharField(max_length=128)  # Consider using hashed passwords in production
    owner_email = models.EmailField(unique=True)
    owner_membership_number = models.CharField(max_length=50, null=True, blank=True)
    owner_cnic = models.CharField(max_length=15, unique=True)
    owner_address = models.CharField(max_length=255, null=True, blank=True)
    owner_city = models.CharField(max_length=255, null=True, blank=True)
    owner_country = models.CharField(max_length=255, null=True, blank=True)
    document_attachment = models.FileField(upload_to='owner_documents/', null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    status=models.CharField(max_length=10,choices=STATUS_CHOICES,default='active')
    def __str__(self):
        return self.owner_name
    
    
 # add OwnerProperty   model 
class OwnerProperty(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    owner = models.ForeignKey('Owner', on_delete=models.CASCADE)
    property_info = models.ForeignKey('Property_info', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    assigned_at = models.DateTimeField(null=True,auto_now_add=True)  # Optional for logging

    class Meta:
        unique_together = ('owner', 'property_info')  # Prevent duplicates

    def __str__(self):
        return f"{self.owner.owner_name} - {self.property_info.property_name} ({self.status})"
    
    
       
    #tenant model
class Tenant(models.Model):
    tenant_id = models.AutoField(primary_key=True)
    tenant_name = models.CharField(max_length=255)
    tenant_guardian_name = models.CharField(max_length=200, null=True, blank=True)
    tenant_profile_picture = models.ImageField(upload_to='tenant_profiles/', null=True, blank=True)
    tenant_phone_number = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255)
    tenant_email = models.EmailField(unique=True)
    tenant_cnic = models.CharField(max_length=15)
    tenant_address = models.TextField()
    tenant_country = models.CharField(max_length=100)
    tenant_city = models.CharField(max_length=100)
    starting_date = models.DateField()
    ending_agreement_date = models.DateField()
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    security_payment = models.DecimalField(max_digits=10, decimal_places=2)
    other_monthly_utility_charges = models.DecimalField(max_digits=10, decimal_places=2)
    assign_property = models.ForeignKey('Property_info', on_delete=models.CASCADE)
    agreement_attachment = models.FileField(upload_to='agreements/', null=True, blank=True)

    def __str__(self):
        return self.tenant_name
    
    
    
# add model form Bilders
    
class FormBuilder(models.Model):
    form_name = models.CharField(max_length=255, unique=True)
    form_fields = models.JSONField()  # Stores field definitions as JSON
    
    def __str__(self):
        return self.form_name    
   #bills Setup models 
class BillsSetup(models.Model):
    form = models.ForeignKey(FormBuilder, on_delete=models.CASCADE, related_name='bills', null=True, blank=True)
    bill_setup_id = models.AutoField(primary_key=True)  # Custom primary key
    property_type_name = models.ForeignKey('PropertyType', on_delete=models.CASCADE, related_name='bills_setups')
    property_area = models.ForeignKey('AreaType', on_delete=models.CASCADE, related_name='bills_setups')
    property_number = models.ForeignKey( 'Property_info',on_delete=models.CASCADE, 
        related_name='bills_setups', 
        null=True, 
        blank=True)
    floor = models.ForeignKey('Floor', on_delete=models.SET_NULL, null=True, blank=True, related_name='bills_setups')
    form_data = models.JSONField()  # Use JSONField for dynamic fields

    def __str__(self):
        return f"Bills setup for {self.property_type_name} - {self.property_area} - {self.property_number} - {self.floor}"
    
   #add model ManagementCommittee
class ManagementCommittee(models.Model):
    mc_id = models.AutoField(primary_key=True)
    mc_name = models.CharField(max_length=200)
    GUARDIAN_TYPE_CHOICES = [
        ('S/O', 'Son of'),
        ('D/O', 'Daughter of'),
        ('W/O', 'Wife of'),
    ]  
    mc_guardian_type = models.CharField(
        max_length=255,
        choices=GUARDIAN_TYPE_CHOICES,
        null=True,
        blank=True
    )
    STATUS_CHOICES = [
        (1, 'Active'),
        (0, 'Expired'),
    ]
    mc_guardian_name = models.CharField(max_length=255, null=True, blank=True)
    mc_email = models.EmailField(max_length=200)
    mc_contact = models.CharField(max_length=200)
    mc_pre_address = models.CharField(max_length=500)
    mc_per_address = models.CharField(max_length=500)
    mc_cnic = models.CharField(max_length=200)
    mc_member_type = models.ForeignKey('MemberTypeSetup',on_delete=models.CASCADE)
    mc_joining_date = models.DateField()  # Consider DateField for date
    mc_ending_date = models.DateField()   # Consider DateField for date
    mc_status = models.IntegerField(choices=STATUS_CHOICES, default=1)  # Updated with choices
    mc_image = models.ImageField(upload_to='M_C_profiles/', null=True, blank=True)
    mc_password = models.CharField(max_length=200)

    def __str__(self):
        return self.mc_name    
    
    # add model MemberTypeSetup
class MemberTypeSetup(models.Model):
    member_type_id = models.AutoField(primary_key=True)
    member_type_name = models.CharField(max_length=200)

    def __str__(self):
        return self.member_type_name   
    
    
# add model MaintenanceCost
class MaintenanceCost(models.Model):
    m_id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    m_title = models.CharField(max_length=200)  # Title of the maintenance cost
    m_date = models.DateField()  # Date of the maintenance cost
    m_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount of the maintenance cost
    m_details = models.TextField(null=True, blank=True)  # Additional details

    def __str__(self):
        return self.m_title    
 
 

# Payments Collection model
class PaymentsCollection(models.Model):
    form = models.ForeignKey(FormBuilder, on_delete=models.CASCADE, null=True, blank=True)
    payments_collection_mode=models.CharField(max_length=255,blank=True,null=True)
    block_name = models.ForeignKey(Block_info, on_delete=models.CASCADE)
    property_number = models.CharField(max_length=255, blank=True, null=True)
    name_id = models.CharField(max_length=255, blank=True, null=True)  # Owner/Tenant name
    month = models.CharField(max_length=255, blank=True,null=True)
    year = models.CharField(max_length=255, blank=True,null=True)
    bills_fields = models.JSONField(blank=True, null=True)
    monthly_rent = models.CharField(max_length=255, blank=True,null=True)
    total_current_bills = models.CharField(max_length=255, blank=True,null=True)
    issue_date = models.DateField()
    due_date = models.DateField()
    balance = models.CharField(max_length=255, blank=True, null=True, default='0')  
    currect_balance = models.CharField(max_length=255, blank=True, null=True, default='0') 
    paid_amount = models.CharField(max_length=255, blank=True, null=True, default='0') 
    bill_status = models.CharField(max_length=50, default='pending') 

    def __str__(self):
        return f"Payment for {self.property_number} in block {self.block_name}"
    





class PaymentReport(models.Model):
    payment_collection = models.ForeignKey('PaymentsCollection', on_delete=models.CASCADE)
    total_current_bills = models.FloatField()
    total_bills = models.FloatField()
    received_amount = models.FloatField()
    discount = models.FloatField(default=0)
    payment_by = models.CharField(max_length=100)  # Cash, Bank Transfer, etc.
    reference_no = models.CharField(max_length=255, blank=True, null=True)
    after_pay_balance = models.FloatField()
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default='pending')  # paid / partial paid

    paid_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for Payment ID {self.payment_collection.id}"




class Fine(models.Model):
    fine = models.CharField(max_length=255, blank=True, null=True, default='0') 

    def __str__(self):
        return f"{self.fine}%"    
    
    
    
    


class Complaint(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    image = models.ImageField(upload_to='complaints/', null=True, blank=True)
    user_id = models.CharField(max_length=150)  # stores username instead of FK

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user_id}"    
    
    
    
    
    
    
    
class Complaint(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    image = models.ImageField(upload_to='complaints/', null=True, blank=True)
    # user_id = models.CharField(max_length=150)  # stores username instead of FK
    owner = models.ForeignKey(Owner, on_delete=models.SET_NULL, null=True, blank=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.owner}" if self.owner else f"{self.title} - {self.tenant}"