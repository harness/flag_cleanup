# Flag Cleanup

Piranha plugin wraps the [uber/piranha](https://github.com/uber/piranha/blob/master/POLYGLOT_README.md#polyglot-piranha) feature flag cleanup tool. For the usage information and a listing of the available options please take a look at the [docs](./DOCS.md).

## Build
Build the image with the following command:
```
make image
```

This will generate a local docker image named _harness/flag_cleanup:latest_ .

## Usage
Execute from the working directory of your codebase:
```shell
docker run -v ${CURDIR}:/my-codebase -e PLUGIN_DEBUG=true -e PLUGIN_PATH_TO_CODEBASE="/my-codebase" -e PLUGIN_PATH_TO_CONFIGURATIONS="/my-codebase/.flag_cleanup_config/" -e PLUGIN_LANGUAGE="go" -e PLUGIN_SUBSTITUTIONS="stale_flag_name=flag_to_remove,treated=true" harness/flag_cleanup:latest
```
