from django.shortcuts import render
from .models import *
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

import base64

from django.conf import settings
import os
from datetime import datetime
import logging
# Create your views here.

def calculator(request):
    # Fetch product data from the database
    all_products = PriceCalculation.objects.all()

    # Prepare product data for the dropdown (product names and their corresponding prices)
    product_data = {}
    for product in all_products:
        product_data[product.product_name] = product.product_price

    # Send the product data to the frontend
    return render(request, 'calculator.html', {'product_data': product_data})

@csrf_exempt
def manage_products(request):
    if request.method == 'GET':
        # Fetch all products to display
        all_products = PriceCalculation.objects.all()
        product_data = []
        for product in all_products:
            product_data.append({
                'id': product.id,
                'product_name': product.product_name,
                'product_price': product.product_price
            })
        return render(request, 'manage_products.html', {'product_data': product_data})
    
    elif request.method == 'POST':
        try:
            # Get JSON data from the request body
            json_data = json.loads(request.body)
            action = json_data.get('action')

            if action == 'add':
                # Add a new product
                product_name = json_data.get('product_name')
                product_price = json_data.get('product_price')

                if not product_name or not product_price:
                    return JsonResponse({'error': 'Both product_name and product_price are required.'}, status=400)
                
                PriceCalculation.objects.create(product_name=product_name, product_price=product_price)
                return JsonResponse({'success': 'Product added successfully.'})

            elif action == 'update':
                # Update an existing product's price
                product_id = json_data.get('product_id')
                product_price = json_data.get('product_price')

                if not product_id or not product_price:
                    return JsonResponse({'error': 'Both product_id and product_price are required.'}, status=400)
                
                product = PriceCalculation.objects.get(id=product_id)
                product.product_price = product_price
                product.save()

                return JsonResponse({'success': 'Product price updated successfully.'})

            elif action == 'delete':
                # Delete a product
                product_id = json_data.get('product_id')

                if not product_id:
                    return JsonResponse({'error': 'Product ID is required.'}, status=400)

                PriceCalculation.objects.filter(id=product_id).delete()
                return JsonResponse({'success': 'Product deleted successfully.'})
        
        except Exception as e:
            return JsonResponse({'error': f'Error: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)



logger = logging.getLogger(__name__)

def save_screenshot(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            image_data = data.get('image')

            if image_data:
                # Decode base64 image
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                img_data = base64.b64decode(imgstr)

                # Define the file path
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
                filepath = os.path.join(settings.STATIC_ROOT, 'screenshots', filename)

                # Ensure the directory exists
                os.makedirs(os.path.dirname(filepath), exist_ok=True)

                # Debugging logs
                logger.debug(f"Saving file at {filepath}")

                # Save the image in the static folder
                with open(filepath, 'wb') as f:
                    f.write(img_data)

                # Generate the URL for the image
                image_url = os.path.join(settings.STATIC_URL, 'screenshots', filename)

                logger.debug(f"Image saved successfully: {image_url}")

                return JsonResponse({'success': True, 'image_url': image_url})

            logger.error("No image data provided.")
            return JsonResponse({'success': False, 'error': 'No image data provided.'})
        except Exception as e:
            logger.error(f"Error while saving screenshot: {str(e)}")
            return JsonResponse({'success': False, 'error': 'Failed to save image.'})