TAG=${1:-latest}

docker build -t codebox .

docker tag codebox:latest shroominic/codebox:$TAG

docker push shroominic/codebox:$TAG
