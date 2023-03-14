# Understanding the rules.toml syntax
In the go demo folder we can see there are only 2 files.

1. example.go - this contains our code, in a real repository we could have hundreds of files in nested folders, only some (or none) of which  contain references to the feature flag we want to remove. This is fine, most files won't have any reference to the feature flag being removed and will safely be ignored. Similarly, if the flag doesn't exist at all no changes will be made and all files ignored.
2. config/rules.toml - This file defines how we find the feature flag references. Basically we need to inform the tool what we want to cleanup from our codebase and how to find it. This is required because our example uses a function called `isEnabled(flag)` while your codebase may use a different api,

Lets take a look at the go sdk demo line by line to see what each part means. We'll focus more on the "query" section after this, for now we're just concerned with what each keyword does:

```shell
# Find any instance where we call the function isEnabled() with a feature flag constant
# e.g. where @stale_flag_name is STALE_FLAG this would match a call looking like isEnabled("STALE_FLAG")
# note extra params dont matter - this rule will also match isEnabled("otherparam", "STALE_FLAG", morestuff)
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

**[[rules]]**: Defines a new rule that the flag cleanup tool will execute

**name:** Name for this particular rule. This can just be any descriptive name for your rule.

**query:** This query is a declarative tree-sitter query that locates your function call/enum declaration/constant declaration/whatever it is you want to search for. More info on how you can create and test these will come later. For now just knowing this is how we find which bits we want to cleanup is enough.

**replace:** What we want to replace the removed code with. This will be a boolean value in this case i.e. the call to isEnabled("STALE_FLAG") will be logically replaced with 'true' or 'false'. Note that this won't literally replace it with the value true. The tool goes through some parsing steps to logically apply this value. It will recognise that the block remaining is `if(true)` and will then proceed to delete the `else` block because it will never be hit, and then remove the `if(true)` section, leaving the code inside as the main code path as we can see after running the example.

**replace_node:** Which node to replace. In this case we've annotated the function call in the query to be called @call_exp, and whatever instance this query returns is what we want to replace.

**groups:** This is an important piece of config which tells the tool to run certain sets of pre-defined rules. e.g. in this case we want to run the rules in the group `replace_expression_with_boolean_literal`. These rules are defined within the cleanup tools [language specific implementations](https://github.com/uber/piranha/tree/master/src/cleanup_rules/go) itself if you're interested, however in general just copying the appropriate group names used from the examples is all you ever need.

**holes:** This parameter is important. This defines any variables we want to use as part of our query/cleanup rule. In our case these are the stale flag name we want to cleanup and the boolean value we want the flag to be globally treated as. These variables are fed in at runtime via the `PLUGIN_SUBSTITUTIONS` parameter, failing to provide fields that have been defined here will give you a runtime error.

### How do I work out which tree sitter query will find the code I want to remove?
For detailed info on using the tree sitter playground to diagnose and create queries see the [tree sitter playground guide](tree_sitter_playground_guide.md). 