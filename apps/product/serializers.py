# apps/products/serializers.py

from apps.core.mixins import PriceConversionMixin

class ProductSerializer(PriceConversionMixin, serializers.ModelSerializer):
    price_converted = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    currency = serializers.CharField(read_only=True)
    price_fields = ['price']  # Fields to convert

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price',
            'price_converted', 'currency'
        ]

    def to_representation(self, instance):
        instance = self.convert_price_fields(
            instance, 
            self.context['request'].user
        )
        return super().to_representation(instance)