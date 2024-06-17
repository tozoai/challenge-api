copilot app init
copilot env init --name newapp --default-config --profile default
copilot svc init --app newapp --name db mongo:latest --svc-type "Backend Service" --port 27017
copilot svc init --app newapp --name web --dockerfile api/Dockerfile --svc-type "Load Balanced Web Service" --port 8080

copilot env deploy --name newapp
copilot svc deploy --name db --env newapp
copilot svc deploy --name web --env newapp