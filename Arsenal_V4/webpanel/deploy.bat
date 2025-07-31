@echo off
echo Deploiement Arsenal V4 WebPanel...

docker-compose down
docker-compose up --build -d

echo Deploiement termine!
echo Panel accessible sur: http://localhost

docker-compose logs -f
