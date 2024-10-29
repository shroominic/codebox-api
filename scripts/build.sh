if [ -z "$1" ]; then
  echo "Error: No version supplied"
  echo "Usage: $0 <version>"
  exit 1
fi

VERSION=$1

docker build -t codebox .

# todo move container to seperate codeboxapi account
docker tag codebox shroominic/codebox:$VERSION
docker tag codebox shroominic/codebox:latest

docker push shroominic/codebox:$VERSION
docker push shroominic/codebox:latest
