docker build -t image-recorder .

docker run -d -p 5000:5000 image-recorder



curl -F file=@./camera.jpg http://127.0.0.1:5000/upload/Ding.jpg
