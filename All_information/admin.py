# from django.contrib import admin
# from .models import Block_info,Property_info,PropertyType,UnitType,Amenity

# @admin.register(Block_info)
# class AdminBlock(admin.ModelAdmin):
#     list_display = ['id', 'block_name']

# @admin.register(PropertyType)
# class AdminPropertyType(admin.ModelAdmin):
#     list_display =['pro_type_id','property_name']  
    
# @admin.register(UnitType)
# class AdminUnitType(admin.ModelAdmin):
#     list_display= ['unit_type_id','unit_number','unit_name'] 
    
# @admin.register(Amenity)
# class AdminAmenity(admin.ModelAdmin):
#     list_display =['amenity_id','amenity_name']         
    
# # Admin customization for Property model

# @admin.register(Property_info)
# class PropertyAdmin(admin.ModelAdmin):
#     list_display = (
#             'property_id',
#             'block_name',
#             'building_name',
#             'property_name',
#             'property_type',
            
#             'unit_type',
#             'floor',
#             'number_of_bedrooms',
#             'number_of_bathrooms',
#             'balcony_or_patio',
#             'parking_space',
#             'number_of_halls',
#             'street_address',
#             'city',
#             'country',
           
#             'property_value',
#             'amenity_name',
#             'size_in_sqm',  
#     )  # Fields to display in the list view

     