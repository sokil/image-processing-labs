```
jpegtran -outfile /dev/null -verbose test-image.jpeg 
```

```
magick test-image.jpeg -define jpeg:restart-interval=2 test0mage-restart4.jpeg
```