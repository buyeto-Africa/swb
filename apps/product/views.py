from django.shortcuts import render

# Create your views here.
# apps/products/views.py

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Convert prices based on location/user preference
        for product in queryset:
            self.convert_price_fields(product, self.request)
            
        return queryset