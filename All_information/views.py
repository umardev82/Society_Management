from rest_framework import viewsets
from .models import AreaType, BillsSetup, Block_info, Complaint, Currency, Fine, Floor, FormBuilder, MaintenanceCost, ManagementCommittee, MemberTypeSetup, PaymentsCollection ,Property_info, PropertyDocument,PropertyType,UnitType,Amenity,Service,Owner, OwnerProperty,Tenant,PaymentReport
from .serializers import AreaTypeSerializer, BillsSetupDisplaySerializer, BillsSetupSerializer, Block_info_serlializer, ComplaintSerializer, CurrencySerializer, FineSerializer, FloorSerializer, FormBuilderSerializer, MaintenanceCostSerializer, ManagementCommitteeDisplaySerializer, ManagementCommitteeSerializer, MemberTypeSetupSerializer, Owner_display_info_Serializer, PaymentsCollectionSerializer, PaymentsCollectionDisplaySerializer, Property_info_serializer, Property_info_serializer_for_display_data,Property_type_serializer, PropertySplitterSerializer, PropertyTransferSerializer, Tenant_display_info_Serializer,Unit_type_serializer,Amenity_serializer,ServiceSerializer,OwnerPropertySerializer,OwnerSerializer,TenantSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.decorators import api_view 
from django.db.models import Q,Sum
from datetime import datetime, timedelta
class BlockInfoViewSet(viewsets.ModelViewSet):
    queryset = Block_info.objects.all()  
    serializer_class = Block_info_serlializer 
 

class PropertyTypeViewSet(viewsets.ModelViewSet):
    queryset= PropertyType.objects.all()
    serializer_class=Property_type_serializer
    
class UnitTypeViewSet(viewsets.ModelViewSet):
    queryset =UnitType.objects.all()
    serializer_class=Unit_type_serializer
    
class AmenityViewSet(viewsets.ModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class=Amenity_serializer 
        
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class=ServiceSerializer 
 
class AreaTypeViewSet(viewsets.ModelViewSet):
    queryset = AreaType.objects.all()
    serializer_class = AreaTypeSerializer    
    
class PropertyInfoViewSet(viewsets.ModelViewSet):
    queryset = Property_info.objects.all()
    # serializer_class = Property_info_serializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Use the flat serializer for write operations
            return Property_info_serializer
        else:
            # Use the nested serializer for read operations
            return Property_info_serializer_for_display_data
          

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        # ✅ Return read serializer with docs included
        read_serializer = Property_info_serializer_for_display_data(instance)
        return Response(read_serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        # ✅ Return read serializer with docs included
        read_serializer = Property_info_serializer_for_display_data(instance)
        return Response(read_serializer.data)

#for get total properties
    @action(detail=False, methods=['get'], url_path='total')
    def get_total_properties(self, request):
        total = Property_info.objects.count()
        return Response({'total_properties': total})    
    
    # @action(detail=True, methods=['post'], url_path='upload-documents')
    # def upload_documents(self, request, pk=None):
    #     property_info = self.get_object()
    #     files = request.FILES.getlist('documents')
    #     for f in files:
    #         PropertyDocument.objects.create(property=property_info, file=f)
    #     return Response({'status': 'documents uploaded'})


# views.py

class OwnerViewSet(viewsets.ModelViewSet):
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return OwnerSerializer
        else:
            return Owner_display_info_Serializer
        
    @action(detail=False, methods=['get'], url_path='total')
    def get_total_owner(self, request):
        total = Owner.objects.count()
        return Response({'total_owners': total})

    @action(detail=False, methods=['get'], url_path='owner-property-numbers')
    def rented_property_numbers(self, request):
        rented_properties = Property_info.objects.filter(is_rented=False)
        serializer = Property_info_serializer_for_display_data(rented_properties, many=True)
        return Response(serializer.data)        
          
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data.pop('csrfmiddlewaretoken', None)
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)

        
        owner = self.get_object()
        if owner.status == 'inactive':
          
            OwnerProperty.objects.filter(owner=owner).update(status='inactive')

        return response



#Floor ViewSet
class FloorViewSet(viewsets.ModelViewSet):
    queryset = Floor.objects.all()
    serializer_class = FloorSerializer
    
#   CurrencyViewSet  
class CurrencyViewSet(viewsets.ModelViewSet):
    queryset=Currency.objects.all()
    serializer_class=CurrencySerializer    

 
#Property Transfer view for owner    
class PropertyTransferViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'], url_path='init-data')
    def init_data(self, request):
        owners = Owner.objects.filter(status='active')
        properties = Property_info.objects.filter(is_active=True)

        owner_data = OwnerSerializer(owners, many=True).data
        property_data = Property_info_serializer_for_display_data(properties, many=True).data

        return Response({
            'owners': owner_data,
            'properties': property_data
        })

    @action(detail=False, methods=['post'], url_path='transfer')
    def transfer_property(self, request):
        serializer = PropertyTransferSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Property transferred successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class OwnerPropertyViewSet(viewsets.ModelViewSet):
    queryset = OwnerProperty.objects.all()
    serializer_class = OwnerPropertySerializer

    def create(self, request, *args, **kwargs):
        owner_id = request.data.get('owner_id')
        property_id = request.data.get('property_id')

        try:
            owner = Owner.objects.get(owner_id=owner_id)
            property_info = Property_info.objects.get(property_id=property_id)

            active_ownership = OwnerProperty.objects.filter(
                property_info=property_info,
                status='active'
            ).exclude(owner=owner).first()

            if active_ownership:
                return Response(
                    {"error": f"Property already assigned to active owner: {active_ownership.owner.owner_name}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            OwnerProperty.objects.update_or_create(
                owner=owner,
                property_info=property_info,
                defaults={'status': 'active'}
            )

            return Response({"message": "Property assigned successfully."}, status=status.HTTP_201_CREATED)

        except Owner.DoesNotExist:
            return Response({"error": "Owner not found."}, status=status.HTTP_404_NOT_FOUND)
        except Property_info.DoesNotExist:
            return Response({"error": "Property not found."}, status=status.HTTP_404_NOT_FOUND)


from rest_framework.views import APIView

# View for Splitting Property
class PropertySplitOptionsView(APIView):
    def get(self, request):
        properties = Property_info.objects.filter(is_active=True)
        serializer = Property_info_serializer_for_display_data(properties, many=True)
        return Response(serializer.data)
    
    
class AreaTypeListView(APIView):
    def get(self, request):
        areas = AreaType.objects.all()
        serializer = AreaTypeSerializer(areas, many=True)
        return Response(serializer.data)



# class PropertySplitterView(APIView):
#     def post(self, request):
#         serializer = PropertySplitterSerializer(data=request.data)
#         if serializer.is_valid():
#             new_properties = serializer.save()
#             return Response({
#                 "message": f"{len(new_properties)} properties created.",
#                 "property_ids": [p.property_id for p in new_properties]
#             }, status=201)
#         return Response(serializer.errors, status=400)


class PropertySplitterView(APIView):
    def post(self, request):
        serializer = PropertySplitterSerializer(data=request.data)
        if serializer.is_valid():
            base_id = serializer.validated_data['base_property_id']
            sub_properties = serializer.validated_data['sub_properties']

            try:
                base_property = Property_info.objects.get(property_id=base_id)
            except Property_info.DoesNotExist:
                return Response({"error": "Base property not found."}, status=404)

            # ✅ Mark parent property inactive
            base_property.is_active = False
            base_property.save()

            base_number = base_property.property_number
            created = []

            for index, sub in enumerate(sub_properties, start=1):
                new_number = f"{base_number}-{index}"

                try:
                    sub_area_type = AreaType.objects.get(pk=sub['area_type_id'])
                except AreaType.DoesNotExist:
                    return Response({"error": f"Invalid area_type_id: {sub['area_type_id']}"}, status=400)

                new_prop = Property_info.objects.create(
                    block_name=base_property.block_name,
                    building_name=base_property.building_name,
                    property_name=sub['property_name'],  # From request
                    property_number=new_number,
                    property_type=base_property.property_type,
                    unit_type=base_property.unit_type,
                    floor=base_property.floor,
                    number_of_bedrooms=base_property.number_of_bedrooms,
                    number_of_bathrooms=base_property.number_of_bathrooms,
                    balcony_or_patio=base_property.balcony_or_patio,
                    parking_space=base_property.parking_space,
                    number_of_halls=base_property.number_of_halls,
                    street_address=base_property.street_address,
                    property_area=sub_area_type,
                    property_value=base_property.property_value,
                    is_active=True,
                    is_rented=False
                )

                if base_property.amenity_name.exists():
                    new_prop.amenity_name.set(base_property.amenity_name.all())

                created.append({
                    "property_id": new_prop.property_id,
                    "property_number": new_prop.property_number,
                    "property_name": new_prop.property_name
                })

            return Response({
                "message": "Property split successfully.",
                "base_property_number": base_number,
                "new_properties": created
            }, status=201)

        return Response(serializer.errors, status=400)

# class PropertySplitterView(APIView):
#     def post(self, request):
#         serializer = PropertySplitterSerializer(data=request.data)
#         if serializer.is_valid():
#             base_id = serializer.validated_data['base_property_id']
#             base_area_value = serializer.validated_data['base_area_value']
#             base_area_type_id = serializer.validated_data['base_area_type_id']
#             sub_properties = serializer.validated_data['sub_properties']

#             try:
#                 base_property = Property_info.objects.get(property_id=base_id)
#                 base_area_type = AreaType.objects.get(pk=base_area_type_id)
#             except (Property_info.DoesNotExist, AreaType.DoesNotExist):
#                 return Response({"error": "Base property or area type not found."}, status=404)

#             base_property.property_area = base_area_type
#             base_property.size_in_sqm = base_area_value
#             base_property.save()

#             base_number = base_property.property_number
#             created = []

#             for index, sub in enumerate(sub_properties, start=1):
#                 new_number = f"{base_number}-{index}"

#                 try:
#                     sub_area_type = AreaType.objects.get(pk=sub['area_type_id'])
#                 except AreaType.DoesNotExist:
#                     return Response({"error": f"Invalid area_type_id: {sub['area_type_id']}"}, status=400)

#                 new_prop = Property_info.objects.create(
#                     block_name=base_property.block_name,
#                     building_name=base_property.building_name,
#                     property_name=f"{base_property.property_name}",
#                     property_number=new_number,  # ✅ generated from base + index
#                     property_type=base_property.property_type,
#                     unit_type=base_property.unit_type,
#                     floor=base_property.floor,
#                     number_of_bedrooms=base_property.number_of_bedrooms,
#                     number_of_bathrooms=base_property.number_of_bathrooms,
#                     balcony_or_patio=base_property.balcony_or_patio,
#                     parking_space=base_property.parking_space,
#                     number_of_halls=base_property.number_of_halls,
#                     street_address=base_property.street_address,
#                     city=base_property.city,
#                     country=base_property.country,
#                     property_area=sub_area_type,
#                     property_value=base_property.property_value,
#                     status="Available",
#                     amenity_name=base_property.amenity_name,
#                     size_in_sqm=sub['area_value'],
#                     is_active=True,
#                     is_rented=False,
#                     document_attachment=base_property.document_attachment
#                 )
#                 created.append({
#                     "property_id": new_prop.property_id,
#                     "property_number": new_prop.property_number,
#                     "property_name": new_prop.property_name
#                 })

#             return Response({
#                 "message": "Property split successfully.",
#                 "base_property_number": base_number,
#                 "new_properties": created
#             }, status=201)

#         return Response(serializer.errors, status=400)



   
   
   
    
    
  
class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return TenantSerializer
        else:
            return Tenant_display_info_Serializer
        
    @action(detail=False, methods=['get'], url_path='rented-property-numbers')
    def rented_property_numbers(self, request):
        rented_properties = Property_info.objects.filter(is_rented=True)
        serializer = Property_info_serializer_for_display_data(rented_properties, many=True)
        return Response(serializer.data)    
    
    # For get total tenants
    @action(detail=False, methods=['get'], url_path='total')
    def get_total_tenant(self, request):
        total = Tenant.objects.count()
        return Response({'total_tenants': total})    

    

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import BillsSetup
from .serializers import BillsSetupSerializer, BillsSetupDisplaySerializer
class BillsSetupViewSet(viewsets.ModelViewSet):
    queryset = BillsSetup.objects.all()
    # serializer_class = BillsSetupSerializer
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return BillsSetupSerializer
        else:
            return BillsSetupDisplaySerializer  

    def get_queryset(self):
        queryset = super().get_queryset()
        property_type_name = self.request.query_params.get('property_type_name')
        property_area = self.request.query_params.get('property_area')
        property_number = self.request.query_params.get('property_number')
        floor = self.request.query_params.get('floor')  # ✅ new filter

        if property_type_name:
            queryset = queryset.filter(property_type_name=property_type_name)
        if property_area:
            queryset = queryset.filter(property_area=property_area)
        if property_number:
            queryset = queryset.filter(property_number=property_number)
        if floor:
            queryset = queryset.filter(floor=floor)  # ✅ Apply floor filter

        return queryset
 
 

    @action(detail=True, methods=['put', 'patch'])
    def update_by_property(self, request, pk=None):
        """
        Custom action to update a BillSetup entry based on property type and area.
        """
        bill_setup = self.get_object()  # Get the instance by primary key (pk)
        
        # Ensure that the request contains 'property_type_name' and 'property_area'
        property_type_name = request.data.get('property_type_name')
        property_area = request.data.get('property_area')

        if property_type_name and property_area:
            # Update the record based on these fields
            bill_setup.property_type_name = property_type_name
            bill_setup.property_area = property_area
            # Optionally update other fields
            bill_setup.charges = request.data.get('charges', bill_setup.charges)
            bill_setup.save()
            return Response(BillsSetupSerializer(bill_setup).data)
        else:
            return Response({"error": "Both property_type_name and property_area are required."}, status=400)
        
class FormBuilderViewSet(viewsets.ModelViewSet):
    queryset = FormBuilder.objects.all()
    serializer_class = FormBuilderSerializer

        
        
# class FormBuilderViewSet(viewsets.ModelViewSet):
#     queryset = FormBuilder.objects.all()
#     serializer_class = FormBuilderSerializer 
 
 
 
class ManagementCommitteeViewSet(viewsets.ModelViewSet):
    queryset = ManagementCommittee.objects.all()
    serializer_class = ManagementCommitteeSerializer
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return ManagementCommitteeSerializer
        else:
            return ManagementCommitteeDisplaySerializer      
    #Get Total  ManagementCommittee  
    @action(detail=False, methods=['get'], url_path='total')
    def get_total_ManagementCommittee(self, request):
        total = ManagementCommittee.objects.count()
        return Response({'total_ManagementCommittee': total})     

class MemberTypeSetupViewSet(viewsets.ModelViewSet):
    queryset = MemberTypeSetup.objects.all()
    serializer_class = MemberTypeSetupSerializer        
        
class MaintenanceCostViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceCost.objects.all()
    serializer_class = MaintenanceCostSerializer        
 


class FineViewSet(viewsets.ModelViewSet):
    queryset=Fine.objects.all()
    serializer_class=FineSerializer
    
    

from django.db.models import Q

# PaymentsCollectionViewSet
class PaymentsCollectionViewSet(viewsets.ModelViewSet):
    queryset = PaymentsCollection.objects.all()
    # serializer_class = PaymentsCollectionSerializer
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return PaymentsCollectionDisplaySerializer
        return PaymentsCollectionSerializer
     

    def get_serializer_context(self):
        context = super().get_serializer_context()
        block_name = self.request.query_params.get('block_name', None)
        if block_name:
            context['block_name'] = block_name  
        return context
    
    
    
    
    
    @action(detail=True, methods=['get'])
    def previous_six_months_history(self, request, pk=None):
     """
     ✅ Get previous 6 months (excluding current month) history.
     ✅ Include all PaymentReports for partially/paid bills.
     """
     current_bill = self.get_object()
     property_number = current_bill.property_number

     today = datetime.today()
     current_year = today.year
     current_month = today.month

     six_months_ago = today - timedelta(days=180)
     six_months_year = six_months_ago.year
     six_months_month = six_months_ago.month
 
     bills = PaymentsCollection.objects.filter(
        property_number=property_number,
     ).filter(
        Q(year__gt=six_months_year) |
        Q(year=six_months_year, month__gte=six_months_month)
     ).exclude(
        Q(year=current_year, month=current_month)
     ).exclude(id=current_bill.id)

     data = []

     for bill in bills:
        # Base info for this bill:
        base_entry = {
            "id": bill.id,
            "month": bill.month,
            "year": bill.year,
            "bill_status": bill.bill_status,
            "total_current_bills": bill.total_current_bills,
            "issue_date": bill.issue_date,
            "due_date": bill.due_date,
        }

        if bill.bill_status in ['partially', 'paid']:
            # ✅ get ALL PaymentReports for this bill
            reports = PaymentReport.objects.filter(payment_collection=bill).order_by('paid_date')
            for report in reports:
                entry = base_entry.copy()
                entry['recept_no'] = report.id
                entry['received_amount'] = report.received_amount
                entry['after_pay_balance'] = report.after_pay_balance
                entry['last_paid_date'] = report.paid_date
                data.append(entry)
        else:
            # If it's still pending, no PaymentReports:
            entry = base_entry.copy()
            entry['recept_no'] = None
            entry['received_amount'] = None
            entry['after_pay_balance'] = None
            entry['last_paid_date'] = None
            data.append(entry)

     return Response({
        "property_number": property_number,
        "previous_six_months_history": data
    })
    
    

    
    @action(detail=False, methods=['get'])
    def get_balance(self, request):
     property_number = request.query_params.get('property_number')

     if not property_number:
        return Response({'error': 'property_number is required'}, status=400)

     # Get the latest bill for the property (regardless of status)
     latest_bill = PaymentsCollection.objects.filter(
        property_number=property_number
     ).order_by('-year', '-month').first()

     if latest_bill:
        if latest_bill.bill_status == 'pending':
            fine_obj = Fine.objects.first()
            fine_percentage = float(fine_obj.fine) if fine_obj else 0.0

            
            total_current_bills = float(latest_bill.total_current_bills)
            fine_amount = (total_current_bills * fine_percentage) / 100
            balance = total_current_bills + fine_amount

        elif latest_bill.bill_status == 'partially':
            # ✅ Get the latest PaymentReport for this PaymentsCollection
            latest_report = PaymentReport.objects.filter(
                payment_collection=latest_bill
            ).order_by('-id').first()

            if latest_report:
                balance = float(latest_report.after_pay_balance)
            else:
                balance = 0.0

        else:  # 'paid'
            balance = 0.0
     else:
        balance = 0.0

     return Response({'balance': round(balance, 2)})


       
    

    @action(detail=False, methods=['get'])
    def get_property_numbers(self, request):
        block_name = request.query_params.get('block_name', None)
        if block_name:
            # Fetching properties based on block_name
            properties = Property_info.objects.filter(block_name=block_name)
            property_numbers = [property.property_number for property in properties]
            return Response({'property_numbers': property_numbers})
        return Response({'property_numbers': []}, status=400)
    
    @action(detail=False, methods=['get'])
    def get_property_owner_or_tenant(self, request):
     property_number = request.query_params.get('property_number', None)

     if not property_number:
        return Response({'error': 'property_number is required'}, status=400)

    # ✅ Get Property_info by number
     property_info = Property_info.objects.filter(property_number=property_number).first()
     if not property_info:
        return Response({'error': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)

    # ✅ Get active Owner(s)
     owner_links = OwnerProperty.objects.filter(property_info=property_info, status='active')
     owners = [link.owner.owner_name for link in owner_links]
     if not owners:
        owners = ["No active owner found"]

    # ✅ Get tenant (if property is rented)
     tenant_name = "Tenant not found"
     monthly_rent = None

     if property_info.is_rented:
        tenant = Tenant.objects.filter(assign_property=property_info).first()
        if tenant:
            tenant_name = tenant.tenant_name
            monthly_rent = tenant.monthly_rent

    # ✅ Bills Setup
     specific_bills_setup = BillsSetup.objects.filter(property_number=property_info).first()
     if specific_bills_setup:
        return Response({
            'property_number': property_info.property_number,
            'owners': owners,
            'tenant_name': tenant_name,
            'monthly_rent': monthly_rent,
            'bills_fields': specific_bills_setup.form_data
        })

    # ✅ Fallback if no specific setup
     bills_setup = BillsSetup.objects.filter(
        property_area=property_info.property_area,
        property_type_name=property_info.property_type
     ).first()

     if bills_setup:
        return Response({
            'property_number': property_info.property_number,
            'owners': owners,
            'tenant_name': tenant_name,
            'monthly_rent': monthly_rent,
            'bills_fields': bills_setup.form_data
        })

     return Response({
        'property_number': property_info.property_number,
        'owners': owners,
        'tenant_name': tenant_name,
        'monthly_rent': monthly_rent,
        'error': 'No matching bills setup found'
     }, status=status.HTTP_404_NOT_FOUND)

    
   
    @action(detail=False, methods=['get'])
    def get_current_partial_balance(self, request):
     property_number = request.query_params.get('property_number')

     if not property_number:
        return Response({'error': 'property_number is required'}, status=400)

    # ✅ Check if property is rented
     try:
         prop = Property_info.objects.get(property_number=property_number)
     except Property_info.DoesNotExist:
         return Response({'error': 'Property not found'}, status=404)

     today = datetime.today()

     if prop.is_rented:
        # ✅ If rented: use previous month
        if today.month == 1:
            year = today.year - 1
            month = 12
        else:
            year = today.year
            month = today.month - 1
     else:
        # ✅ If not rented: use current month
        year = today.year
        month = today.month

    # ✅ Get partially paid bill for selected period
     bill = PaymentsCollection.objects.filter(
        property_number=property_number,
        year=year,
        month=month,
        bill_status='partially'
     ).first()

     if not bill:
        return Response({
            'balance': 0.0,
            'message': f'No partially paid bill for {month}/{year}.'
        })

     report = PaymentReport.objects.filter(payment_collection=bill).order_by('-id').first()

     if report:
        balance = float(report.after_pay_balance)
     else:
         balance = 0.0

     return Response({
        'property_number': property_number,
        'year': year,
        'month': month,
        'after_pay_balance': round(balance, 2)
     })


    @action(detail=False, methods=['get'])
    def total_received_amount_current_month(self, request):
     today = datetime.today()
     current_year = today.year
     current_month = today.month

    # Filter PaymentReports for current month & year (using PaymentCollection relation)
     total = PaymentReport.objects.filter(
        paid_date__year=current_year,  
        paid_date__month=current_month  
     ).aggregate(total_received=Sum('received_amount'))

     return Response({
        'year': current_year,
        'month': current_month,
        'total_received_amount': total['total_received'] or 0.0
     })
     
     
    @action(detail=False, methods=['get'])
    def pending_clearances(self, request):
     today = datetime.today()
     current_year = today.year
     current_month = today.month

    # Determine previous month and year safely
     if current_month == 1:
        prev_month = 12
        prev_year = current_year - 1
     else:
        prev_month = current_month - 1
        prev_year = current_year

    # Get pending bills for current and previous month
     pending_bills = PaymentsCollection.objects.filter(
        bill_status='pending',
     ).filter(
        (Q(year=current_year, month=current_month)) |
        (Q(year=prev_year, month=prev_month))
     )

     pending_total = pending_bills.aggregate(
        total_pending=Sum('total_current_bills')
     )['total_pending'] or 0.0

    # Get partially paid bills for current month
     partially_bills = PaymentsCollection.objects.filter(
        bill_status='partially',
        year=current_year,
        month=current_month
     )

     partial_total = 0.0
     for bill in partially_bills:
        latest_report = PaymentReport.objects.filter(payment_collection=bill).order_by('-paid_date').first()
        if latest_report and latest_report.after_pay_balance:
            partial_total += float(latest_report.after_pay_balance)

     combined_total = pending_total + partial_total

     return Response({
        'pending_total': round(pending_total, 2),
        'partially_total': round(partial_total, 2),
        'combined_total': round(combined_total, 2)
     })
   
    
    @action(detail=True, methods=['post'])
    def pay_bill(self, request, pk=None):
     payment = self.get_object()

     received_amount = float(request.data.get('received_amount', 0))
     discount = float(request.data.get('discount', 0))
     payment_by = request.data.get('payment_by', '')
     reference_no = request.data.get('reference_no', '')
     description = request.data.get('description', '')
     after_pay_balance = float(request.data.get('after_pay_balance', 0))
     total_bills=float(request.data.get('total_bills', 0))
     total_current_bills=float(request.data.get('total_current_bills', 0))
     status = request.data.get('status', payment.bill_status)
    # ✅ Save in PaymentReport
     PaymentReport.objects.create(
        payment_collection=payment,
        total_current_bills=total_current_bills,
        total_bills=total_bills,
        received_amount=received_amount,
        discount=discount,
        payment_by=payment_by,
        reference_no=reference_no,
        after_pay_balance=after_pay_balance,
        description=description,
         status=status
     )
     
      # ✅ Also update the main PaymentsCollection record
     payment.bill_status = status
     payment.current_balance = after_pay_balance
     payment.save()

     return Response({'status': 'Payment recorded and report saved'})

     
    @action(detail=True, methods=['get'])
    def receipt_report(self, request, pk=None):
     """
     Get ALL receipt/report data for a payment collection.
     """
     payment = self.get_object()

    # ⚡️ Get ALL PaymentReports for this payment
     reports = PaymentReport.objects.filter(payment_collection=payment).order_by('-paid_date')

     if not reports.exists():
        return Response({'error': 'No PaymentReports found for this payment'}, status=404)

     data = []
     for report in reports:
        data.append({
            # PaymentsCollection fields
            'id': payment.id,
            'name_id': payment.name_id,
            'month': payment.month,
            'year': payment.year,
            'block_name': payment.block_name.block_name if payment.block_name else None,
            'property_number': payment.property_number,
            'bills_fields': payment.bills_fields,
            'issue_date': payment.issue_date,
            'due_date': payment.due_date,

            # PaymentReport fields
            'recept_no': report.id,
            'total_current_bills': report.total_current_bills,
            'total_bills': report.total_bills,
            'received_amount': report.received_amount,
            'discount': report.discount,
            'payment_by': report.payment_by,
            'reference_no': report.reference_no,
            'after_pay_balance': report.after_pay_balance,
            'description': report.description,
            'status': report.status,
            'paid_date': report.paid_date,
        })

     return Response(data)

   
     
#    Get  All reports  and  include filter  

from django.core.exceptions import ObjectDoesNotExist
# from rest_framework.decorators import api_view
# from rest_framework.response import Response

@api_view(['GET'])
def reports_filter(request):
    block_id = request.query_params.get('block_id')
    property_number = request.query_params.get('property_number')
    month = request.query_params.get('month')
    year = request.query_params.get('year')
    bill_status = request.query_params.get('bill_status')
    paid_date_start = request.query_params.get('paid_date_start')
    paid_date_end = request.query_params.get('paid_date_end')
    area_type_id = request.query_params.get('area_type_id')

    qs = PaymentsCollection.objects.all()

    if block_id:
        qs = qs.filter(block_name_id=block_id)
    if property_number:
        qs = qs.filter(property_number=property_number)
    if month:
        qs = qs.filter(month=month)
    if year:
        qs = qs.filter(year=year)
    if bill_status:
        qs = qs.filter(bill_status=bill_status)
    if area_type_id:
        properties = Property_info.objects.filter(property_area_id=area_type_id)
        property_numbers = properties.values_list('property_number', flat=True)
        qs = qs.filter(property_number__in=property_numbers)
     
    data = []
    total_sum = 0.0  # total_current_bills ka sum
    counted_bills = set()  # already counted bills

    # ✅ Har month ka last after_pay_balance track karne ke liye
    last_after_balance = {}
    
     # ✅ Get total sums
    totals = qs.aggregate(
        
        received_amount_sum=Sum('paymentreport__received_amount'),
        discount_sum=Sum('paymentreport__discount'),
        
    )

    for payment in qs:
        bill_key = (payment.name_id, payment.property_number, payment.month, payment.year)

        owner_info = {}
        tenant_info = {}

        try:
            property_obj = Property_info.objects.get(property_number=payment.property_number)

            # 🔹 Owner info
            try:
                owner_link = OwnerProperty.objects.get(property_info=property_obj, status='active')
                owner = owner_link.owner
                owner_info = {
                    "owner_guardian_name": owner.owner_guardian_name,
                    "owner_phone_number": owner.owner_phone_number,
                    "owner_email": owner.owner_email,
                    "owner_membership_number": owner.owner_membership_number,
                    "owner_cnic": owner.owner_cnic,
                    "owner_address": owner.owner_address,
                    "party_type": "Owner"
                }
            except OwnerProperty.DoesNotExist:
                pass

            # 🔹 Tenant info
            try:
                tenant_link = Tenant.objects.get(assign_property=property_obj)
                tenant_info = {
                    "tenant_guardian_name": tenant_link.tenant_guardian_name,
                    "tenant_phone_number": tenant_link.tenant_phone_number,
                    "tenant_email": tenant_link.tenant_email,
                    "tenant_cnic": tenant_link.tenant_cnic,
                    "tenant_address": tenant_link.tenant_address,
                    "party_type": "Tenant"
                }
            except Tenant.DoesNotExist:
                pass

        except Property_info.DoesNotExist:
            pass

        reports = PaymentReport.objects.filter(payment_collection=payment)

        if paid_date_start and paid_date_end:
            reports = reports.filter(
                paid_date__range=[paid_date_start, paid_date_end],
                paid_date__isnull=False
            )

        if reports.exists():
            for report in reports:
                row = {
                    "name_id": payment.name_id,
                    "month": payment.month,
                    "year": payment.year,
                    "block_name": payment.block_name.block_name if payment.block_name else None,
                    "property_number": payment.property_number,
                    "bills_fields": payment.bills_fields,
                    "issue_date": payment.issue_date,
                    "due_date": payment.due_date,
                    "recept_no": report.id,
                    "total_current_bills": payment.total_current_bills,
                    "received_amount": report.received_amount,
                    "discount": report.discount,
                    "payment_by": report.payment_by,
                    "reference_no": report.reference_no,
                    "after_pay_balance": report.after_pay_balance,
                    "description": report.description,
                    "status": report.status,
                    "paid_date": report.paid_date
                }
                row.update(owner_info)
                row.update(tenant_info)
                data.append(row)

                # ✅ Total_current_bills sum (only first occurrence)
                if bill_key not in counted_bills:
                    try:
                        total_sum += float(payment.total_current_bills or 0)
                    except (ValueError, TypeError):
                        total_sum += 0
                    counted_bills.add(bill_key)

                # ✅ Last after_pay_balance track (latest by paid_date then recept_no)
                month_key = (payment.property_number, payment.month, payment.year)
                current_entry = last_after_balance.get(month_key)
                if (
                    current_entry is None or
                    (report.paid_date and current_entry["paid_date"] and report.paid_date > current_entry["paid_date"]) or
                    (report.paid_date == current_entry["paid_date"] and report.id > current_entry["recept_no"])
                ):
                    last_after_balance[month_key] = {
                        "after_pay_balance": report.after_pay_balance,
                        "paid_date": report.paid_date,
                        "recept_no": report.id
                    }

        else:
            if not paid_date_start and not paid_date_end:
                row = {
                    "name_id": payment.name_id,
                    "month": payment.month,
                    "year": payment.year,
                    "block_name": payment.block_name.block_name if payment.block_name else None,
                    "property_number": payment.property_number,
                    "bills_fields": payment.bills_fields,
                    "issue_date": payment.issue_date,
                    "due_date": payment.due_date,
                    "recept_no": None,
                    "total_current_bills": payment.total_current_bills,
                    "received_amount": None,
                    "discount": None,
                    "payment_by": None,
                    "reference_no": None,
                    "after_pay_balance": None,
                    "description": None,
                    "status": payment.bill_status,
                    "paid_date": None
                }
                row.update(owner_info)
                row.update(tenant_info)
                data.append(row)

                if bill_key not in counted_bills:
                    try:
                        total_sum += float(payment.total_current_bills or 0)
                    except (ValueError, TypeError):
                        total_sum += 0
                    counted_bills.add(bill_key)

    # ✅ Sort data
    sorted_data = sorted(
        data,
        key=lambda x: (x['recept_no'] is None, x['recept_no'] if x['recept_no'] is not None else 0)
    )

    # ✅ After Pay Balance Sum (only last entries)
    after_balance_sum = 0.0
    for val in last_after_balance.values():
        try:
            after_balance_sum += float(val["after_pay_balance"] or 0)
        except (ValueError, TypeError):
            after_balance_sum += 0

    return Response({
        "total_current_bills_sum": total_sum,
        "after_pay_balance_sum": after_balance_sum,
        "totals_received_amount_and_discount": totals,
        "data": sorted_data
    })


# from django.core.exceptions import ObjectDoesNotExist
# @api_view(['GET'])
# def reports_filter(request):
#     block_id = request.query_params.get('block_id')
#     property_number = request.query_params.get('property_number')
#     month = request.query_params.get('month')
#     year = request.query_params.get('year')
#     bill_status = request.query_params.get('bill_status')
#     paid_date_start = request.query_params.get('paid_date_start')
#     paid_date_end = request.query_params.get('paid_date_end')
#     area_type_id = request.query_params.get('area_type_id')

#     qs = PaymentsCollection.objects.all()

#     if block_id:
#         qs = qs.filter(block_name_id=block_id)
#     if property_number:
#         qs = qs.filter(property_number=property_number)
#     if month:
#         qs = qs.filter(month=month)
#     if year:
#         qs = qs.filter(year=year)
#     if bill_status:
#         qs = qs.filter(bill_status=bill_status)
#     if area_type_id:
#         properties = Property_info.objects.filter(property_area_id=area_type_id)
#         property_numbers = properties.values_list('property_number', flat=True)
#         qs = qs.filter(property_number__in=property_numbers)
    
    

#     # ✅ Get total sums
#     totals = qs.aggregate(
        
#         received_amount_sum=Sum('paymentreport__received_amount'),
#         discount_sum=Sum('paymentreport__discount'),
#         after_pay_balance_sum=Sum('paymentreport__after_pay_balance'),
#     )
#     data = []
#     for payment in qs:
#         # -------------------------------
#         # Get Owner or Tenant extra info
#         # -------------------------------
 
#         owner_info = {}
#         tenant_info = {}

#         try:
#             property_obj = Property_info.objects.get(property_number=payment.property_number)

#             # 🔹 Owner check from OwnerProperty model
#             try:
#                 owner_link = OwnerProperty.objects.get(property_info=property_obj, status='active')
#                 owner = owner_link.owner
#                 owner_info = {
#                     "owner_guardian_name": owner.owner_guardian_name,
#                     "owner_phone_number": owner.owner_phone_number,
#                     "owner_email": owner.owner_email,
#                     "owner_membership_number": owner.owner_membership_number,
#                     "owner_cnic": owner.owner_cnic,
#                     "owner_address": owner.owner_address,
#                     "party_type": "Owner"
#                 }
#             except OwnerProperty.DoesNotExist:
#                 pass

#             # 🔹 Tenant check (assuming TenantProperty relation hai)
#            # 🔹 Tenant check
#             try:
#                 tenant_link = Tenant.objects.get(assign_property=property_obj)
#                 tenant_info = {
#                     "tenant_guardian_name": tenant_link.tenant_guardian_name,
#                     "tenant_phone_number": tenant_link.tenant_phone_number,
#                     "tenant_email": tenant_link.tenant_email,
#                     "tenant_cnic": tenant_link.tenant_cnic,
#                     "tenant_address": tenant_link.tenant_address,
#                     "party_type": "Tenant"
#                 }
#             except Tenant.DoesNotExist:
#                 pass


#         except Property_info.DoesNotExist:
#             pass

#         reports = PaymentReport.objects.filter(payment_collection=payment)

#         # ✅ If paid_date filter given, apply it to reports
#         if paid_date_start and paid_date_end:
#             reports = reports.filter(
#                 paid_date__range=[paid_date_start, paid_date_end],
#                 paid_date__isnull=False
#             )

#         if reports.exists():
#             for report in reports:
#                 row = {
#                     "name_id": payment.name_id,
#                     "month": payment.month,
#                     "year": payment.year,
#                     "block_name": payment.block_name.block_name if payment.block_name else None,
#                     "property_number": payment.property_number,
#                     "bills_fields": payment.bills_fields,
#                     "issue_date": payment.issue_date,
#                     "due_date": payment.due_date,
#                     "recept_no": report.id,
#                     "total_current_bills": report.total_current_bills,
#                     "total_bills": report.total_bills,
#                     "received_amount": report.received_amount,
#                     "discount": report.discount,
#                     "payment_by": report.payment_by,
#                     "reference_no": report.reference_no,
#                     "after_pay_balance": report.after_pay_balance,
#                     "description": report.description,
#                     "status": report.status,
#                     "paid_date": report.paid_date
#                 }
#                 # Merge owner or tenant info
#                 row.update(owner_info)
#                 row.update(tenant_info)
#                 data.append(row)
#         else:
#             # ✅ Only add unpaid if NO paid_date filter
#             if not paid_date_start and not paid_date_end:
#                 row = {
#                     "name_id": payment.name_id,
#                     "month": payment.month,
#                     "year": payment.year,
#                     "block_name": payment.block_name.block_name if payment.block_name else None,
#                     "property_number": payment.property_number,
#                     "bills_fields": payment.bills_fields,
#                     "issue_date": payment.issue_date,
#                     "due_date": payment.due_date,
#                     "recept_no": None,
#                     "total_current_bills": None,
#                     "total_bills": None,
#                     "received_amount": None,
#                     "discount": None,
#                     "payment_by": None,
#                     "reference_no": None,
#                     "after_pay_balance": None,
#                     "description": None,
#                     "status": payment.bill_status,
#                     "paid_date": None
#                 }
#                 row.update(owner_info)
#                 row.update(tenant_info)
#                 data.append(row)
                

#     # ✅ Sort the data list by `recept_no` (None at end)
#     sorted_data = sorted(
#         data,
#         key=lambda x: (x['recept_no'] is None, x['recept_no'] if x['recept_no'] is not None else 0)
#     )
    
#     # return Response(sorted_data)
#     return Response({
#     "totals": totals,
#     "data": sorted_data
# })










from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all().order_by('-created_at')
    serializer_class = ComplaintSerializer
    authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        if Owner.objects.filter(user=user).exists():
            # If user is an Owner
            serializer.save(user_id=user.username)
        elif Tenant.objects.filter(user=user).exists():
            # If user is a Tenant
            serializer.save(user_id=user.username)
        else:
            # Assume admin or staff user
            serializer.save(user_id=user.first_name)

    # Get total Complaints
    @action(detail=False, methods=['get'], url_path='total')
    def get_total_complaints(self, request):
        total = Complaint.objects.count()
        return Response({'total_complaints': total})





# class PaymentsCollectionViewSet(viewsets.ModelViewSet):
#     queryset = PaymentsCollection.objects.all()
#     serializer_class = PaymentsCollectionSerializer

#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         block_name = self.request.query_params.get('block_name', None)
#         if block_name:
#             context['block_name'] = block_name  # Passing block_name to the serializer context
#         return context

#     @action(detail=False, methods=['get'])
#     def get_property_numbers(self, request):
#         block_name = request.query_params.get('block_name', None)
#         if block_name:
#             # Fetching properties based on block_name
#             properties = Property_info.objects.filter(block_name=block_name)
#             property_numbers = [property.property_number for property in properties]
#             return Response({'property_numbers': property_numbers})
#         return Response({'property_numbers': []}, status=400)
    
#     @action(detail=False, methods=['get'])
#     def get_property_owner_or_tenant(self, request):
#      property_number = request.query_params.get('property_number', None)
#      if property_number:
#         property_number = property_number.strip()  # Clean the input

#         # Fetch the related Property_info
#         property_info = Property_info.objects.filter(property_number=property_number).first()
#         if property_info:
#             # Check for specific BillsSetup linked to property_number
#             specific_bills_setup = BillsSetup.objects.filter(property_number=property_number).first()
          
#             if specific_bills_setup:
#                 # Case 1: Specific BillsSetup for the property_number
#                 return Response({
#                     'property_number': property_info.property_number,
#                     'related_properties': [property_info.property_number],
#                     'bills_fields': specific_bills_setup.form_data
#                 })

#             # Case 2: Fallback to area/type-based BillsSetup
#             property_area = property_info.property_area
#             property_type = property_info.property_type

#             bills_setup = BillsSetup.objects.filter(
#                 property_area=property_area,
#                 property_type_name=property_type
#             ).first()

#             if bills_setup:
#                 # Fetch all properties linked by area and type
#                 related_properties = Property_info.objects.filter(
#                     property_area=property_area,
#                     property_type=property_type
#                 )
#                 related_property_numbers = [prop.property_number for prop in related_properties]

#                 return Response({
#                     'property_number': property_info.property_number,
#                     'related_properties': related_property_numbers,
#                     'bills_fields': bills_setup.form_data
#                 })

#             return Response({'error': 'No matching bills setup found'}, status=status.HTTP_404_NOT_FOUND)

#         return Response({'error': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)

#      return Response({'error': 'property_number is required'}, status=status.HTTP_400_BAD_REQUEST)



    
    
# class PaymentsCollectionViewSet(viewsets.ModelViewSet):
#     queryset = PaymentsCollection.objects.all()
#     serializer_class = PaymentsCollectionSerializer
    
#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         block_name = self.request.query_params.get('block_name', None)
#         if block_name:
#             context['block_name'] = block_name  # Passing block_name to the serializer context
#         return context
    
#     @action(detail=False, methods=['get'])
#     def get_property_numbers(self, request):
#         block_name = request.query_params.get('block_name', None)
#         if block_name:
#             # Fetching properties based on block_name
#             properties = Property_info.objects.filter(block_name=block_name)
#             property_numbers = [property.property_number for property in properties]
#             return Response({'property_numbers': property_numbers})
#         return Response({'property_numbers': []}, status=400)
#     @action(detail=False, methods=['get'])
#     def get_property_owner_or_tenant(self, request):
    # # Get the selected property number from the request
    #  property_number = request.query_params.get('property_number', None)

    #  if property_number:
    #     # Fetch the Property_info object based on the property_number
    #     property_info = Property_info.objects.filter(property_number=property_number).first()

    #     if property_info:
    #         # Fetch the associated owner from Property_info using owner_id
    #         owner = property_info.owner  # This fetches the Owner instance linked to this Property_info
    #         owner_name = owner.owner_name if owner else "Owner not found"

    #         # Fetch tenant associated with this property using assign_property
    #         tenant = Tenant.objects.filter(assign_property=property_info).first()
    #         tenant_name = tenant.tenant_name if tenant else "Tenant not found"

    #         # Fetch the bills setup for this property
    #         bills_setup = BillsSetup.objects.filter(property_number=property_info).first()
    #         form_data = bills_setup.form_data if bills_setup else "No bills setup found"

#             return Response({
#                 'property_number': property_info.property_number,
#                 'owner_name': owner_name,
#                 'tenant_name': tenant_name,
#                 'bills_fields': form_data
#             })
#         return Response({'error': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)

#      return Response({'error': 'property_number is required'}, status=status.HTTP_400_BAD_REQUEST)




# Owner  And Tenant APIs
@api_view(['GET'])
def owner_payments_list(request, owner_id):
    try:
        owner = Owner.objects.get(pk=owner_id)
    except Owner.DoesNotExist:
        return Response({'message': 'Owner not found'}, status=status.HTTP_404_NOT_FOUND)

    # Example: if PaymentsCollection has name_id as FK to Owner
    payments = PaymentsCollection.objects.filter(name_id=owner)

    # Or adjust filter to your actual link field
    data = []
    for payment in payments:
        # ✅ Get the latest PaymentReport if exists
        latest_report = PaymentReport.objects.filter(payment_collection=payment).order_by('-paid_date').first()
        after_pay_balance = latest_report.after_pay_balance if latest_report else None
        data.append({
            'id': payment.id,
            'name': payment.name_id,
            'month': payment.month,
            'year': payment.year,
            'block_name': payment.block_name.block_name if payment.block_name else None,
            'property_number': payment.property_number,
            'balance': payment.balance,
            'bills_fields': payment.bills_fields,
            'monthly_rent': payment.monthly_rent,
            'total_current_bills': payment.total_current_bills,
            'after_pay_balance': after_pay_balance,
            'bill_status': payment.bill_status,
            'issue_date': payment.issue_date,
            'due_date': payment.due_date
        })

    return Response({'payments': data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def owner_receipt_reports(request, payment_id):
    try:
        payment = PaymentsCollection.objects.get(pk=payment_id)
    except PaymentsCollection.DoesNotExist:
        return Response({'message': 'PaymentCollection not found'}, status=status.HTTP_404_NOT_FOUND)

    reports = PaymentReport.objects.filter(payment_collection=payment).order_by('paid_date')

    data = []
    for report in reports:
        data.append({
            'id': payment.id,
            'receipt_no': report.id,
            "name_id": payment.name_id,
            'block_name': payment.block_name.block_name if payment.block_name else None,
            'property_number': payment.property_number,
            'total_current_bills': report.total_current_bills,
            'total_bills': report.total_bills,
            'received_amount': report.received_amount,
            'discount': report.discount,
            'payment_by': report.payment_by,
            'reference_no': report.reference_no,
            'after_pay_balance': report.after_pay_balance,
            'description': report.description,
            'status': report.status,
            'paid_date': report.paid_date
        })

    return Response({'receipts': data}, status=status.HTTP_200_OK)




@api_view(['POST'])
def create_complaint(request):
    title = request.data.get('title')
    description = request.data.get('description')
    image = request.FILES.get('image')  # Optional
    owner_id = request.data.get('owner_id')
    tenant_id = request.data.get('tenant_id')

    if not title or not description:
        return Response({'error': 'Title and description are required.'}, status=400)

    if not owner_id and not tenant_id:
        return Response({'error': 'owner_id or tenant_id must be provided.'}, status=400)

    complaint = Complaint(title=title, description=description, image=image)

    if owner_id:
        try:
            complaint.owner = Owner.objects.get(pk=owner_id)
        except Owner.DoesNotExist:
            return Response({'error': 'Invalid owner_id'}, status=404)

    if tenant_id:
        try:
            complaint.tenant = Tenant.objects.get(pk=tenant_id)
        except Tenant.DoesNotExist:
            return Response({'error': 'Invalid tenant_id'}, status=404)

    complaint.save()

    return Response({'message': 'Complaint created successfully'}, status=201)

#Get all complaints for a specific owner or tenant
@api_view(['GET'])
def list_complaints(request):
    owner_id = request.query_params.get('owner_id')
    tenant_id = request.query_params.get('tenant_id')

    if not owner_id and not tenant_id:
        return Response({'error': 'owner_id or tenant_id must be provided.'}, status=400)

    if owner_id:
        complaints = Complaint.objects.filter(owner_id=owner_id)
    elif tenant_id:
        complaints = Complaint.objects.filter(tenant_id=tenant_id)

    data = []
    for c in complaints:
        data.append({
            'id': c.id,
            'title': c.title,
            'description': c.description,
            'status': c.status,
            'image': request.build_absolute_uri(c.image.url) if c.image else None,
            'created_at': c.created_at
        })

    return Response(data, status=200)



#API that auto-creates bills for properties.

from datetime import date
from django.db import transaction



from .utils import sum_numeric_from_json
from django.db.models import Max

class AutoCreateBillsView(APIView):
    def post(self, request):
        month = request.data.get("month")
        year = request.data.get("year")
        issue_date_str = request.data.get('issue_date')
        due_date_str = request.data.get('due_date')

        if not month or not year or not issue_date_str or not due_date_str:
            return Response(
                {"error": "month, year, issue_date and due_date are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            issue_date = date.fromisoformat(issue_date_str)
            due_date = date.fromisoformat(due_date_str)
        except ValueError:
            return Response(
                {"error": "Dates must be in ISO format YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        properties = Property_info.objects.all()
        created, skipped = [], []

        with transaction.atomic():
            for prop in properties:
                prop_num = prop.property_number

                # Skip if bill already exists for this month/year
                if PaymentsCollection.objects.filter(
                    property_number=prop_num,
                    year=str(year),
                    month=str(month)
                ).exists():
                    skipped.append({
                        "property_number": prop_num,
                        "reason": "bill already exists",
                        "month": month,
                        "year": year
                    })
                    continue

                # Find owner or tenant
                owner_link = OwnerProperty.objects.filter(
                    property_info__property_number=prop_num,
                    status='active'
                ).first()
                owner_obj = owner_link.owner if owner_link else None
                tenant_obj = Tenant.objects.filter(
                    assign_property__property_number=prop_num
                ).first()

                name_id = owner_obj.owner_name if owner_obj else (
                    tenant_obj.tenant_name if tenant_obj else None
                )

                # monthly_rent Tenant se lo
                monthly_rent = float(getattr(tenant_obj, 'monthly_rent', 0) or 0)

                # BillsSetup find
                bills_setup = BillsSetup.objects.filter(property_number=prop).first()
                if not bills_setup:
                    bills_setup = BillsSetup.objects.filter(
                        property_type_name=prop.property_type,
                        property_area=prop.property_area
                    ).first()

                bills_fields = bills_setup.form_data if bills_setup else {}
                if not bills_fields:
                    bills_fields = {}

                # Base current bills (monthly rent + form bills sum)
                total_current_bills = sum_numeric_from_json(bills_fields) + monthly_rent
                balance = total_current_bills  # start with current month total

                # ✅ Check last previous bill
                previous_bill = PaymentsCollection.objects.filter(
                    property_number=prop_num
                ).exclude(month=str(month), year=str(year)).order_by('-year', '-month').first()

                if previous_bill:
                    if previous_bill.bill_status == 'pending':
                        balance += float(previous_bill.total_current_bills or 0)
                        total_current_bills += float(previous_bill.total_current_bills or 0)

                    elif previous_bill.bill_status == 'partially':
                        last_payment_report = PaymentReport.objects.filter(
                            payment_collection=previous_bill
                        ).order_by('-id').first()
                        if last_payment_report:
                            after_balance = float(last_payment_report.after_pay_balance or 0)
                            balance += after_balance
                            total_current_bills += after_balance

                    elif previous_bill.bill_status == 'paid':
                        # no dues to add
                        pass

                # Create bill
                new_bill = PaymentsCollection.objects.create(
                    form=getattr(bills_setup, 'form', None),
                    payments_collection_mode=None,
                    block_name=prop.block_name,
                    property_number=prop_num,
                    name_id=name_id,
                    month=str(month),
                    year=str(year),
                    bills_fields=bills_fields,
                    monthly_rent=monthly_rent,
                    total_current_bills=total_current_bills,
                    balance=balance,
                    paid_amount=0,
                    bill_status='pending',
                    issue_date=issue_date,
                    due_date=due_date
                )

                created.append({
                    "property_number": prop_num,
                    "bill_id": new_bill.id,
                    "month": month,
                    "year": year,
                    "assigned_to": name_id
                })

        return Response({
            "created_count": len(created),
            "created": created,
            "skipped": skipped
        }, status=status.HTTP_201_CREATED)

# from .utils import  sum_numeric_from_json


# class AutoCreateBillsView(APIView):
#     """
#     POST payload:
#     {
#       "month": "8",
#       "year": "2025",
#       "issue_date": "2025-09-01",
#       "due_date": "2025-09-10"
#     }
#     """
#     def post(self, request):
#         month = request.data.get("month")
#         year = request.data.get("year")
#         issue_date_str = request.data.get('issue_date')
#         due_date_str = request.data.get('due_date')

#         if not month or not year or not issue_date_str or not due_date_str:
#             return Response(
#                 {"error": "month, year, issue_date and due_date are required."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             issue_date = date.fromisoformat(issue_date_str)
#             due_date = date.fromisoformat(due_date_str)
#         except ValueError:
#             return Response(
#                 {"error": "Dates must be in ISO format YYYY-MM-DD."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         properties = Property_info.objects.all()
#         created = []
#         skipped = []

#         with transaction.atomic():
#             for prop in properties:
#                 prop_num = prop.property_number

#                 # Skip if bill already exists for this month/year
#                 if PaymentsCollection.objects.filter(
#                     property_number=prop_num,
#                     year=str(year),
#                     month=str(month)
#                 ).exists():
#                     skipped.append({
#                         "property_number": prop_num,
#                         "reason": "bill already exists",
#                         "month": month,
#                         "year": year
#                     })
#                     continue

#                 # Find owner or tenant
#                 owner_link = OwnerProperty.objects.filter(
#                     property_info__property_number=prop_num,
#                     status='active'
#                 ).first()
#                 owner_obj = owner_link.owner if owner_link else None

#                 tenant_obj = Tenant.objects.filter(
#                     assign_property__property_number=prop_num
#                 ).first()

#                 name_id = owner_obj.owner_name if owner_obj else (
#                     tenant_obj.tenant_name if tenant_obj else None
#                 )

#                 # ✅ monthly_rent Tenant se lo agar tenant exist karta hai
#                 if tenant_obj and hasattr(tenant_obj, 'monthly_rent'):
#                   monthly_rent = float(tenant_obj.monthly_rent or 0)
#                 else:
#                  monthly_rent = 0.0

#                 bills_setup = BillsSetup.objects.filter(property_number=prop).first()
#                 if not bills_setup:
#                     bills_setup = BillsSetup.objects.filter(
#                         property_type_name=prop.property_type,
#                         property_area=prop.property_area
#                     ).first()

#                 bills_fields = bills_setup.form_data if bills_setup else {}
#                 if not bills_fields:
#                     bills_fields = {}

#                 # ✅ Ab sum_numeric_from_json ka result + tenant monthly_rent add kare
#                 total_current_bills = sum_numeric_from_json(bills_fields) + monthly_rent




#                 # Create bill
#                 new_bill = PaymentsCollection.objects.create(
#                     form=getattr(bills_setup, 'form', None),
#                     payments_collection_mode=None,
#                     block_name=prop.block_name,
#                     property_number=prop_num,
#                     name_id=name_id,
#                     month=str(month),
#                     year=str(year),
#                     bills_fields=bills_fields,
#                     monthly_rent=monthly_rent,
#                     total_current_bills=total_current_bills,
#                     balance=0,
#                     paid_amount=0,
#                     bill_status='pending',
#                     issue_date=issue_date,
#                     due_date=due_date
#                 )

#                 created.append({
#                     "property_number": prop_num,
#                     "bill_id": new_bill.id,
#                     "month": month,
#                     "year": year,
#                     "assigned_to": name_id
#                 })

#         return Response({
#             "created_count": len(created),
#             "created": created,
#             "skipped": skipped
#         }, status=status.HTTP_201_CREATED)

