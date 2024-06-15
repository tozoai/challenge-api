# challenge-api

Stack Python + Flask + MongoDB + Docker


## Installation

Build docker image:

```bash

docker build -t challenge-api .
docker image (get image id)
docker run --name challenge-api -d challenge-api

```

To set proper keys create an .env file in the root of the project and add the following:

```
JWT_SECRET_KEY=your_secret_key_here
MONGO_URI=mongodb://localhost:5000
```

Run the app:

Set AWS Elastic Container Registry:
```
(Get-ECRLoginCommand).Password | docker login --username AWS --password-stdin 471112676018.dkr.ecr.us-east-2.amazonaws.com
docker build -t challenge-image-repository .
docker tag challenge-image-repository:latest 471112676018.dkr.ecr.us-east-2.amazonaws.com/challenge-image-repository:latest
docker push 471112676018.dkr.ecr.us-east-2.amazonaws.com/challenge-image-repository:latest
```