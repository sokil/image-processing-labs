```
jpegtran -outfile /dev/null -verbose test-image.jpeg 
```

```
magick test-image.jpeg -define jpeg:restart-interval=1 test-image-restart1.jpeg
magick test-image.jpeg -define jpeg:restart-interval=2 test-image-restart2.jpeg
magick test-image.jpeg -define jpeg:restart-interval=3 test-image-restart3.jpeg
magick test-image.jpeg -define jpeg:restart-interval=4 test-image-restart4.jpeg
```
