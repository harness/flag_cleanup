image: ## Builds a docker image called harness/piranha:latest
	@echo "Building Piranha Image"
	@docker build -t harness/flag_cleanup:unscripted -f ./Dockerfile .