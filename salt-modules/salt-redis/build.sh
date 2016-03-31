# build.sh

NAME="redis"

SRC_DIR=$RECIPE_DIR
cd $SRC_DIR

# Create directory structure

DIRECTORIES="srv/salt"
for path in $DIRECTORIES
do
    mkdir -p $PREFIX/$path
    touch $PREFIX/$path/.gitkeep
done

cp -r $NAME $PREFIX/srv/salt
