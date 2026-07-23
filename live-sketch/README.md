# Live Sketch

Live Sketch is a webapp where each page has a canvas that could be controlled by as REST API and the webpage updates automatically.


## API

View the web page:

```
http://localhost:8080/<sketch-id>
```

Download the SVG:

```
GET http://localhost:8080/<sketch-id>.svg
```

Upload a new svg:

```
PUT http://localhost:8080/<sketch-id>.svg
```
