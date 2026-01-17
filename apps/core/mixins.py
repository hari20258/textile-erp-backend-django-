from apps.users.permissions import IsStoreManager

class StoreManagerModificationMixin:
    """
    Mixin to enforce Store Manager permissions for modification actions
    (create, update, partial_update, destroy).
    Read actions fall back to default ViewSet permissions.
    """
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsStoreManager()]
        return super().get_permissions()


class QuickAddValidationMixin:
    """
    Mixin to handle 'Quick Add' logic in serializers.
    Constructs 'items' list from 'quick_variant' and 'quick_quantity' if not provided.
    Expects 'quick_variant' and 'quick_quantity' to be present in attrs or initial data.
    """
    def validate_quick_add(self, attrs, price_source_field=None):
        """
        Validates and constructs items list.
        :param attrs: The validated attributes from valid()
        :param price_source_field: (Optional) Field on variant to use as unit_price (e.g., 'retail_price')
        """
        from rest_framework import serializers

        if 'items' not in attrs or not attrs['items']:
            variant = attrs.get('quick_variant')
            quantity = attrs.get('quick_quantity', 1) # Default to 1 if not set
            
            if variant:
                item_data = {
                    'variant': variant, 
                    'quantity': quantity
                }
                
                # Optionally set unit_price if a source field is provided
                if price_source_field and hasattr(variant, price_source_field):
                     item_data['unit_price'] = getattr(variant, price_source_field)

                attrs['items'] = [item_data]
                
                # Cleanup helper fields
                attrs.pop('quick_variant', None)
                attrs.pop('quick_quantity', None)
            else:
                raise serializers.ValidationError(
                    "You must either provide a list of 'items' (JSON) OR select an item in 'Select Item' (HTML Form)."
                )
        return attrs
