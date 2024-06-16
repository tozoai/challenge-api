copilot env deploy --name newapp
copilot svc deploy --name db --env newapp
copilot svc deploy --name web --env newapp