TAG=${1:-latest}

rye build --wheel -c -q

docker build -t codebox .

# todo move container to seperate codeboxapi account
docker tag codebox:latest shroominic/codebox:$TAG

# docker push shroominic/codebox:$TAG
