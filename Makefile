NS=thomasbuchinger
NAME=common
VERSION=0.0.1


.PHONY: lint
lint:
	ansible-lint site.yaml
.PHONY: build
build:
	ansible-galaxy collection build --force
	tar -zxf ${NS}-${NAME}-${VERSION}.tar.gz MANIFEST.json FILES.json
