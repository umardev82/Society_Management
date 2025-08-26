
# society_management/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from All_information.views import AreaTypeListView, AreaTypeViewSet, AutoCreateBillsView, BillsSetupViewSet, BlockInfoViewSet, ComplaintViewSet, CurrencyViewSet, FineViewSet, FloorViewSet, FormBuilderViewSet, MaintenanceCostViewSet, ManagementCommitteeViewSet, MemberTypeSetupViewSet, PaymentsCollectionViewSet,PropertyInfoViewSet, PropertySplitOptionsView, PropertySplitterView, PropertyTransferViewSet,PropertyTypeViewSet, TenantViewSet,UnitTypeViewSet,AmenityViewSet,ServiceViewSet,OwnerViewSet,OwnerPropertyViewSet, create_complaint, list_complaints, owner_payments_list, owner_receipt_reports, reports_filter


# Define the router and register the viewset
router = DefaultRouter()
router.register('block_info', BlockInfoViewSet, basename='block_info')
router.register('area-type', AreaTypeViewSet, basename='area-type')
router.register('property_type_info',PropertyTypeViewSet,basename='property_type_information')
router.register('unit_type_info',UnitTypeViewSet,basename='unit_type_information')
router.register('amenity_info',AmenityViewSet,basename='amenity_information')


router.register('service_info',ServiceViewSet,basename='service_information')
router.register('property_info', PropertyInfoViewSet, basename='property_info')
router.register('owners', OwnerViewSet, basename='owner')

router.register('owner-property', OwnerPropertyViewSet, basename='owner_property')


#add new  for transfor property 
#Get Lists -> http://127.0.0.1:8000/property-transfer/init-data/
#Post Method -> http://127.0.0.1:8000/property-transfer/transfer/
# {
#   "property_id": 3,
#   "new_owner_id": 6
# }

router.register('property-transfer', PropertyTransferViewSet, basename='property-transfer')
# end 
#add new for  floor 
router.register('floors', FloorViewSet) 
router.register('currency',CurrencyViewSet,basename='currenct-tab')
router.register('tenant', TenantViewSet, basename='tenant')
router.register('form-builder', FormBuilderViewSet, basename='form-builder')
router.register('bills-setup', BillsSetupViewSet, basename='bills_setup')
router.register('member-type-setup', MemberTypeSetupViewSet)
router.register('management-committee', ManagementCommitteeViewSet)
router.register('maintenance_costs', MaintenanceCostViewSet)


router.register('payments-collection', PaymentsCollectionViewSet)
router.register('fine-set',FineViewSet,basename='fine')
router.register('complaints', ComplaintViewSet, basename='complaints')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auto-create-bills/', AutoCreateBillsView.as_view(), name='auto_create_bills'),
    # Add this to urlpatterns

    # path('reports/', PaymentsCollectionViewSet.as_view({'get': 'reports'}), name='reports'),
    path('reports-filter/', reports_filter, name='reports_filter'),
    
    path('get-property-numbers/', PaymentsCollectionViewSet.as_view({'get': 'get_property_numbers'}), name='get_property_numbers'),
    path('get_property_owner_or_tenant/', PaymentsCollectionViewSet.as_view({'get': 'get_property_owner_or_tenant'}), name='get_property_owner_or_tenant'),
    #http://127.0.0.1:8000/payments/get-balance/?property_number=13 for get balance of previous month 
    path('payments/get-balance/', PaymentsCollectionViewSet.as_view({'get': 'get_balance'}), name='get_balance'),
    path('get-current-partial-balance/',PaymentsCollectionViewSet.as_view({'get': 'get_current_partial_balance'}),name='get_current_partial_balance'),

    path('api/user/', include('user_management.urls')),
  
     path('property/split/', PropertySplitterView.as_view(), name='property-split'),
     path('property/split-options/', PropertySplitOptionsView.as_view(), name='property-split-options'),
     path('area-types/', AreaTypeListView.as_view(), name='area'),
    path('owner-payments/<int:owner_id>/', owner_payments_list, name='owner-payments'),
    path('owner-receipts/<int:payment_id>/', owner_receipt_reports, name='owner-receipts'),
    path('complaints/create/', create_complaint),
    path('complaints/list/', list_complaints),
    path('', include(router.urls)), 
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
