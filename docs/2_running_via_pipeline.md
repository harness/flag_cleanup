# Running Via Pipeline

## Purpose
This guide will allow you to run the flag cleanup tool via a pipeline, cleaning up the flag and raising a pr on Github to remove it from the codebase. This will allow flags to be cleaned up by any team members with a few clicks. It will also provide the basis for running this pipeline to cleanup any stale flags in your system in an automated basis once every week/month etc. 

## Time Required
<15 minutes

## Guide
For this example we will use the golang sdk [here](https://github.com/harness/ff-golang-server-sdk), however you can also use the java sdk [here](https://github.com/harness/ff-java-server-sdk) if you'd prefer.

## Instructions
### Fork repository 
Fork and clone this repository on github. 