TAG=${1:-latest}

docker build -t codebox .

# todo move container to seperate codeboxapi account
docker tag codebox:latest shroominic/codebox:$TAG

docker push shroominic/codebox:$TAG
