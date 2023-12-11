import os
import subprocess
import toml

from abc import ABC, abstractmethod
from polyglot_piranha import execute_piranha, PiranhaArguments, Rule, RuleGraph, Filter

class FeatureCleanup(ABC):
    @abstractmethod
    def cleanupFlag(self, substitution, cleanup_comments):
        pass

# Create a subclass that can interact with the Polyglot Piranha
class PolyglotPiranha(FeatureCleanup):
    def __init__(self, language, pathToCodeBase, pathToToml):
        self.language = language
        self.pathToCodeBase = os.path.abspath(pathToCodeBase)
        self.pathToToml = os.path.abspath(pathToToml)
        config_parsed = self.parse_toml(self.pathToToml)
        rules = []
        for rule in config_parsed["rules"]:
            print("conf: {}".format(rule))

            r = Rule(
                name=rule["name"],
                query=rule["query"],
                replace_node=self._cleanup_replace_node(rule["replace_node"]),
                replace=rule["replace"],
                groups=set(rule["groups"]),
                holes=set(rule["holes"])
            )
            rules.append(r)
        self.rules = rules

    def _cleanup_replace_node(replace_node):
        if replace_node == "call_expression":
            return "call_exp"
        return replace_node

    def _parse_toml(toml_file_path):
        try:
            # Parse the TOML file
            with open(toml_file_path, "r") as toml_file:
                data = toml.load(toml_file)
                return data
        except FileNotFoundError:
            print(f"The file '{toml_file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def cleanupFlag(self, substitution, cleanup_comments):
        piranha_arguments = PiranhaArguments(
            self.language,
            paths_to_codebase=[],
            rule_graph=RuleGraph(rules=self.rules, edges=[]),
            substitutions=substitution,
            dry_run = False,
            cleanup_comments = cleanup_comments
        )
        return execute_piranha(piranha_arguments)

# Create a subclass that can interact with the JS Piranha
class JavascriptPiranha(FeatureCleanup):
    def __init__(self, language, pathToCodeBase, pathToProperties):
        self.language = language
        self.pathToCodeBase = os.path.abspath(pathToCodeBase)
        self.pathToProperties = os.path.abspath(pathToProperties)

    def cleanupFlag(self, substitution, cleanup_comments):
        flag_name = substitution["stale_flag_name"]
        command = f"node /piranha/legacy/javascript/src/piranha.js -s {self.pathToCodeBase} -p {self.pathToProperties} -f {flag_name}"

        # Run the command using subprocess
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            # Access the output
            diff = result.stdout
            print(diff)
            if result.stderr:
                print("Standard error:")
                print(result.stderr)
            return diff
        except subprocess.CalledProcessError as e:
            # Handles errors if the command fails
            print("Error executing command:", e)
