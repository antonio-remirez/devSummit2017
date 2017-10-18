
# coding: utf-8

# # ArcGIS Python API
# 
# <br />
# <img src="https://desarrollogis.maps.arcgis.com/sharing/rest/content/items/c695225d54844306a73105632b8c0839/data">
# <br />

# 
# # Por dónde empezamos?
# 
# ### Por la página de desarrolladores: https://developers.arcgis.com/python/ 
# 
# ### Acceso directo al API en Github: https://github.com/Esri/arcgis-python-api 
# 
# ### ArcGIS Python API Reference: http://esri.github.io/arcgis-python-api/apidoc/html/ 
# 
# ### Para conocer más sobre conda: https://conda.io/docs/
# 
# ### Para entender mejor Jupyter: https://jupyterhub.readthedocs.io/en/latest/ 
# 
# ### Escribir y formatear con Markdown: https://help.github.com/articles/basic-writing-and-formatting-syntax/
# 
# <br />

# # Calentamiento
# 
# Vamos a hacer un pequeño ejercicio de calentamiento basado en un notebook existente:
# 
# 1. Accede a la web de desarrolladores y busca los samples: https://developers.arcgis.com/python/sample-notebooks/
# 1. Busca el primer ejemplo ("Your first notebook"): https://developers.arcgis.com/python/sample-notebooks/your-first-notebook/ y pincha en "Try it live" para acceder al notebook
# 1. Repasa la sección "Getting started with the API" y trata de usarla desde una cuenta propia
# 
# <br />

# # Administrando tu Web GIS
# 
# Ahora vamos a comprobar cómo un administrador puede acceder a usuarios/roles/grupos de su organización y modificarlos a su gusto.

# In[1]:

from arcgis import *
gis = GIS("https://desarrollogis.maps.arcgis.com", "expertoAdmin")


# In[ ]:

# Podemos habilitar/deshabilitar usuarios
users = gis.users.search("*")
for user in users:
    if str(user["username"]) != "expertoAdmin":
        user.disable()


# In[ ]:

# Podemos crear/eliminar usuarios y su contenido. También podemos reasignar contenido
newuser = gis.users.create(username = "aaaweee",
                            password = None,
                            firstname = "firstName",
                            lastname = "lastName",
                            email = "testUser@test.es",
                            role="org_publisher")

newuser


# In[ ]:

newuser.delete()


# In[ ]:

users = gis.users.search("*")
for user in users:
    if user.availableCredits < 25:
        print(user.firstName + user.lastName)


# # Creando contenido

# In[7]:

import pandas as pd


# In[8]:

# Cargamos unos datos de un CSV local o externo mediante Pandas
earthquakes = pd.read_csv("https://desarrollogis.maps.arcgis.com/sharing/rest/content/items/b30add2027384ffaafc8aa4c642e074d/data")
earthquakes


# In[47]:

earthquakes["DamageExtent"].plot(kind="hist")


# In[23]:

map = gis.map('Los Angeles')
map


# In[24]:

# Importamos como capa estos datos (la relación API-Pandas es muy fluida)
featureLayer = gis.content.import_data(earthquakes)


# In[25]:

map.add_layer(featureLayer)


# In[ ]:

import json

# Ya que tenemos la información en momoria, la podemos ajustar para salvarla en nuestro Web GIS
item_properties = {
    "title": "Terremotoso LA",
    "tags" : "terremotos,LA",
    "description": "terremotos en LA",
    "text": json.dumps({"featureCollection": {"layers": [dict(featureLayer.layer)]}}),
    "type": "Feature Collection",
    "typeKeywords": "Data, Feature Collection, Singlelayer"
}

item = gis.content.add(item_properties)
item


# # Análisis espacial

# In[26]:

import arcgis.network as network


# In[27]:

# Este servicio es configurable y podemos usar el nuestro propio en ArcGIS Enterprise
service_area_url = gis.properties.helperServices.serviceArea.url
service_area_url


# In[28]:

# Obtenemos el servicio service área
sa_layer = network.ServiceAreaLayer(service_area_url, gis=gis)


# In[29]:

# De nuestra capa de terremotos cogemos las features haciendo un query (1=1) y calculamos 3 saltos drive-time
result = sa_layer.solve_service_area(featureLayer.query(),default_breaks=[5,10,15])


# In[30]:

# Revisamos el resultado
result.keys()


# In[31]:

# Vemos que hay polígonos que contienen geometrías
result['saPolygons'].keys()


# In[32]:

from arcgis.features import Feature, FeatureSet

# Creamos una lista con los polígonos que incluye el resultado del service área
poly_feat_list = []
for polygon_dict in result['saPolygons']['features']:
    f1 = Feature(polygon_dict['geometry'], polygon_dict['attributes'])
    poly_feat_list.append(f1)


# In[33]:

# Esa lista la convertimos en un FeatureSet para mayor comodidad
service_area_fset = FeatureSet(poly_feat_list, 
                         geometry_type=result['saPolygons']['geometryType'],
                         spatial_reference= result['saPolygons']['spatialReference'])


# In[34]:

# Usamos 3 colores, el más próximo al epicentro será rojo y el más alejado verde
colors = {5: [255, 0, 0, 90], 
          10: [255, 255, 0, 90], 
          15: [0, 128, 0, 90]}

fill_symbol = {"type": "esriSFS","style": "esriSFSSolid", "color": [115,76,0,255]}


# In[35]:

# Para cada polígono resultado de nuestro FeatureSet lo pintamos según corresponda (5, 10 o 15)
for service_area in service_area_fset.features:
    
    #set color based on drive time
    fill_symbol['color'] = colors[service_area.attributes['ToBreak']]
       
    map.draw(service_area.geometry, symbol=fill_symbol)

