# Running Locally

## Purpose
This guide will allow you to run the flag cleanup tool locally using either the go or java sdk.

## Time Required
<5 minutes 

## Guide
For this example we will use the golang sdk [here](https://github.com/harness/ff-golang-server-sdk), however you can also use the java sdk [here](https://github.com/harness/ff-java-server-sdk) if you'd prefer.

1. Clone the repo to your local machine. ```git clone git@github.com:harness/ff-golang-server-sdk.git```
2. Look at the current code in the go sdk example file [here](https://github.com/harness/ff-golang-server-sdk/blob/main/examples/code_cleanup/example.go#L15). Pay attention to the `if else` block that checks if the `harnessappdemodarkmode` flag is enabled.

![Before](./images/before.png "Before")

3. Run the code cleanup example from the root folder of the go sdk repo. This checks for the presence of the `harnessappdemodarkmode` flag and if present treats any `isEnabled("harnessappdemodarkmode")` checks as true.

```shell
docker run -v ${PWD}:/go-sdk -e PLUGIN_DEBUG=true -e PLUGIN_PATH_TO_CODEBASE="/go-sdk/examples/code_cleanup" -e PLUGIN_PATH_TO_CONFIGURATIONS="/go-sdk/examples/code_cleanup/config" -e PLUGIN_LANGUAGE="go" -e PLUGIN_SUBSTITUTIONS="stale_flag_name=harnessappdemodarkmode,treated=true" harness/flag_cleanup:latest
```

4. Observe the changes made to the example.go file - namely that the `if else` block has been removed and only the `true` code path remains. 

![After](./images/after.png "After")

## Explanation
Firstly, for detailed information of how this tool works see the piranha [documentation](https://github.com/uber/piranha/blob/master/POLYGLOT_README.md).

### What do the plugin parameters do?
For information on which parameters are available to pass to the flag cleanup plugin see the main [readme](../README.md#parameters). 

These include options you might expect like the location to the base directory of the code you want to cleanup, location of your config (more on that later) and substitutions which for most cases will be the name of the flag you want to remove (`stale_flag_name`) and whether you want the flag to be considered globally true or false (`treated`).

### Where can I find more examples?
A suite of examples are maintained in the uber/piranha repository. These can be found in the [test cases](https://github.com/uber/piranha/tree/master/test-resources) folder as well as in the [demo](https://github.com/uber/piranha/tree/master/demo) sample folder. 

### What configuration files are required?
A valid rules.toml file is a requirement. For more advanced use cases an edges.toml file may also be required. Examples of their usage can be found at the links above.


## Demo example explained
In the golang demo folder we can see there are only 2 files. 

1. example.go - this contains our code, in a real repository we could have hundreds of files in nested folders, only some (or none) of which  contain references to the feature flag we want to remove.
2. config/rules.toml - This file defines how we find the feature flag references. Basically we need to inform the tool what we want to cleanup and how to find it. 

Lets take a look at the go sdk demo line by line to see how it was constructed the way it is and what each part means:

```shell
# Find any instance where we call the function isEnabled() with a feature flag constant
# e.g. where @stale_flag_name is harnessappdemodarkmode this would match a call looking like isEnabled("harnessappdemodarkmode")
# note extra params dont matter - this rule will also match isEnabled("otherparam", "harnessappdemodarkmode", morestuff)
[[rules]]
name = "FlagCleanup"
query = """
(
    (call_expression
        function: (identifier) @func_id
        arguments: (argument_list
            (interpreted_string_literal) @arg_id
        )
    )
    (#eq? @func_id "isEnabled")
    (#eq? @arg_id "\\"@stale_flag_name\\"")
) @call_exp
"""
replace = "@treated"
replace_node = "call_exp"
groups = ["replace_expression_with_boolean_literal"]
holes = ["stale_flag_name", "treated"]
```

**[[rules]]**: Defines a new rule

**name:** Name for this particular rule. This can just be any descriptive name for your rule.

**query:** This query is a declarative tree-sitter query that locates your function call/enum declaration/constant declaration/whatever it is you want to search for. More info on how you can create and test these will come later. For now just knowing this is how we find which bits we want to cleanup is enough.

**replace:** What we want to replace the removed code with. This will be a boolean value in this case i.e. the call to isEnabled("harnessappdarkmodedemo") will be logically replaced with 'true' or 'false'. Note that this won't literally replace it with the value true. The tool go through some parsing steps to logically apply this value. It will recognise that the block remaining is `if(true)` and will then proceed to delete the `else` block because it will never be hit, and then remove the `if(true)` section, leaving the code inside as the main code path as we can see after running the example. 

**replace_node:** Which node to replace. In this case we've annotated the function call in the query to be called @call_exp, and whatever instance this query returns is what we want to replace.

**groups:** This is an important piece of config which tells the tool to run certain sets of pre-defined rules. e.g. in this case we want to run the rules in the group `replace_expression_with_boolean_literal`. These rules are defined within the cleanup tools [language specific implementations](https://github.com/uber/piranha/tree/master/src/cleanup_rules/go) itself if you're interested, however in general just copying the appropriate group names used from the examples is all you ever need.

**holes:** This parameter is important. This defines any variables we want to use as part of our query/cleanup rule. In our case these are the stale flag name we want to cleanup and the boolean value we want the flag to be globally treated as. These variables are fed in at runtime via the `PLUGIN_SUBSTITUTIONS` parameter, failing to provide fields that have been defined here will give you a runtime error.

### How do I work out which tree sitter query will find the code I want to remove?
For detailed info on using the tree sitter playground to diagnose and create queries see the [tree sitter playground guide](tree_sitter_playground_guide.md). 