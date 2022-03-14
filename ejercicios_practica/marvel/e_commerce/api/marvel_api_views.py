# Import models:
from e_commerce.models import *

from marvel.settings import VERDE, CIAN, AMARILLO
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
#from rest_framework.decorators import api_view,  permission_classes
import requests
import json
import hashlib

from django.shortcuts import render

# NOTE: Declaramos las variables que tienen que ver con la API KEY de Marvel:

PUBLIC_KEY = '7656a41bc960e34cda6c7d3ed5099ca6'
PRIVATE_KEY = '1bb24bb8e627fb2f79c5a86860c0985d9efcdf77'
TS = 1
TO_HASH = str(TS)+PRIVATE_KEY+PUBLIC_KEY
HASHED = hashlib.md5(TO_HASH.encode())
URL_BASE = 'http://gateway.marvel.com/v1/public/'
ENDPOINT = 'comics'
PARAMS = dict(ts=TS, apikey=PUBLIC_KEY, hash=HASHED.hexdigest())

# NOTE: Ejemplo de hello world con método GET
@csrf_exempt
def hello_world(request):
    return render(request,'hello-world.html', {
        'message': 'Mensage desde vista 2'
    })


@csrf_exempt
def get_comics(request):
    '''
    Vista personalizada de API para comprar comics, 
    primero consultamos los comics disponibles en la página de Marvel, 
    luego generamos una lista de los que tienen precio y descripción, 
    porque varios vienen `null`.
    '''
    # Declaramos nuestras variables:
    id = []
    title = []
    description = []
    prices = []
    thumbnail = []
    products = {}
    limit = 0
    offset = 0
    # NOTE: Para obtener los valores de request, dependemos del tipo de petición, así:
    # GET METHOD: request.GET['algo']   O también: request.GET.get('algo')
    # POST METHOD: request.POST['algo'] O también: request.POST.get('algo')
    # POST METHOD: request.data['algo'] O también: request.data.get('algo')
    # Como son similares a los diccionarios se puede hacer de las dos maneras.

    # Traemos los datos del request, asegurandonos que son numeros, sino, les asignamos
    # un valor por defecto:
    if request.GET.get('offset') == None or request.GET['offset'].isdigit() == False:
        offset = 0
    else:
        offset = request.GET.get('offset')
    if request.GET.get('limit') == None or request.GET['limit'].isdigit() == False:
        limit = 15
    else:
        limit = request.GET.get('limit')

    offset = int(offset)
    limit = int(limit)

    # Realizamos el request:
    aditional_params = {'limit': limit, 'offset': offset}
    params = PARAMS
    params.update(aditional_params)
    # NOTE: A los parametros de hash, api key y demás, sumamos limit y offset para paginación.
    res = requests.get(URL_BASE+ENDPOINT, params=params)
    comics = json.loads(res.text)

    # Obtenemos la lista de comics:
    comics_list = comics.get('data').get('results')



    # Filtramos la lista de comics y nos quedamos con lo que nos interesa:
    
    for comic in comics_list:
        prods = {}
        id.append(comic.get('id'))
        description.append(comic.get('description'))
        title.append(comic.get('title'))
        prices.append(comic.get('prices')[0].get('price'))
        thumbnail.append(
            f"{comic.get('thumbnail').get('path')}/standard_xlarge.jpg")
        prods = {'id': comic.get('id'), 
             'description': comic.get('description'),
             'title': comic.get('title'), 
             'prices': comic.get('prices')[0].get('price'),
             'thumbnail':f"{comic.get('thumbnail').get('path')}/standard_xlarge.jpg"
        }
        products.update(prods)
             
        
    # NOTE: Invoca template get-comics
    return render(request,'get-comics.html', {
        'products': [
            {'id':id[0], 'description': description[0], 'title': title[0], 'prices':prices[0],'thumbnail':thumbnail[0]},
            {'id':id[1], 'description': description[1], 'title': title[1], 'prices':prices[1],'thumbnail':thumbnail[1]}, 
            {'id':id[2], 'description': description[2], 'title': title[2], 'prices':prices[2],'thumbnail':thumbnail[2]},
            {'id':id[3], 'description': description[3], 'title': title[3], 'prices':prices[3],'thumbnail':thumbnail[3]},
            {'id':id[4], 'description': description[4], 'title': title[4], 'prices':prices[4],'thumbnail':thumbnail[4]},
            {'id':id[5], 'description': description[5], 'title': title[5], 'prices':prices[5],'thumbnail':thumbnail[5]},
            {'id':id[6], 'description': description[6], 'title': title[6], 'prices':prices[6],'thumbnail':thumbnail[6]},
            {'id':id[7], 'description': description[7], 'title': title[7], 'prices':prices[7],'thumbnail':thumbnail[7]},
            {'id':id[8], 'description': description[8], 'title': title[8], 'prices':prices[8],'thumbnail':thumbnail[8]},
            {'id':id[9], 'description': description[9], 'title': title[9], 'prices':prices[9],'thumbnail':thumbnail[9]},
            {'id':id[10], 'description': description[10], 'title': title[10], 'prices':prices[10],'thumbnail':thumbnail[10]},
            {'id':id[11], 'description': description[11], 'title': title[11], 'prices':prices[11],'thumbnail':thumbnail[11]},
            {'id':id[12], 'description': description[12], 'title': title[12], 'prices':prices[12],'thumbnail':thumbnail[12]},
            {'id':id[13], 'description': description[13], 'title': title[13], 'prices':prices[13],'thumbnail':thumbnail[13]},
            {'id':id[14], 'description': description[14], 'title': title[14], 'prices':prices[14],'thumbnail':thumbnail[14]},
        ] 
        }
    )

@csrf_exempt
def purchased_item(request):
    '''Incluye la lógica de guardar lo pedido en la base de datos 
    y devuelve el detalle de lo adquirido '''

    # Obtenemos los datos del request:
    title = request.POST.get('title')
    thumbnail = request.POST.get('thumbnail')
    description = request.POST.get('description')
    price = request.POST.get('prices')
    qty = request.POST.get('qty')
    id = request.POST.get('id')

    # TODO: Construimos la Query:
    # Verificamos que el comic no se encuentra en nuestro stock:

    queryset = Comic.objects.filter(marvel_id=id)

    if len(queryset.values_list()) == 0 :
        # Si el resultado nos trae una lista vacía, creamos un nuevo registro:
        item = Comic(title=title, description=description, price=price,
                    stock_qty=qty, picture=thumbnail, marvel_id=id)
        print(CIAN,queryset)
        item.save()
    else:
        # Si el comic está registrado, actualizamos su cantidad:
        comic = Comic.objects.get(marvel_id=id)
        actual_stock = comic.stock_qty
        actual_stock += int(qty)
        Comic.objects.filter(marvel_id=id).update(stock_qty=actual_stock)

    # NOTE: Construimos la respuesta
    # Calculamos el precio total:
    try:
        total = float(price) * int(qty)
    except:
        total = ". . ."
    
    # NOTE: invoca a template purchased_item
    return render(request,'purchased_item.html', {
        'id': id,
        'title': title,
        'description': description,
        'thumbnail': thumbnail,
        'price': price,
        'qty': qty,
        'total': total,

    })

