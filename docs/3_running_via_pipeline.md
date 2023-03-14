# Running Via Pipeline

## Purpose
This guide will allow you to run the flag cleanup tool via a pipeline, cleaning up the flag and raising a pr on Github to remove it from the codebase. This will allow flags to be cleaned up by any team members with a few clicks. It will also provide the basis for running this pipeline to cleanup any stale flags in your system in an automated basis once every week/month etc. 

## Time Required
<15 minutes

## Requirements
1. Github access token
2. Harness account - this can be created for free with only an email

## Guide
For this example we will use the golang sdk example, however you can also use the java sdk example if you'd prefer.

As with any pipeline it makes sense to start small and incrementally add any new parts required as we go. For this pipeline we can build it up section by section: 
1. Run flag cleanup tool and print out the generated git diffs
2. Commit the git diffs and push to a branch on github
3. Raise a pr on github using that branch 

After this you can customise the pipeline to suit your own bespoke needs. You could open JIRA tickets to track the work or send messages into slack channels etc. You also might want to perform other tasks required for your codebase before pushing such as running linters to format the generated code etc.


## Run Flag Cleanup Tool and Print Diffs
A video demo of this is available in the [demo google drive folder](https://drive.google.com/drive/folders/1tbnnQ3dbed0bMpNFE58oOvOUM6cBLD62?usp=sharing)
1. Fork and clone repository
2. Login to your Harness account or create a free (only email required) account on https://app.harness.io/ 
3. Select the CI module and hit Get Started to create your pipeline
4. Go through the onboarding flow, inputting your github token and selecting the forked repo you want to run the tool against
5. Once the pipeline has been created click into the yaml editor view and copy the `pipeline.stages` and `pipeline.variables` sections from the [sample pipeline provided](pipelines/flag_cleanup_pipeline.yaml).
6. Save the pipeline
7. Go to the "triggers" tab and disable any webhook triggers - these will run the pipeline after each push which we don't want
8. Edit the stage variable GITHUB_USERNAME and assign it's value to your github username. This variable will be used to set the commit author as well as to configure a few urls e.g. in my example my fork is conormurray95/flag_cleanup so my `GITHUB_USERNAME` should be set to conormurray95.
9. Hit run and input the go sdk example flag we want to cleanup `harnessappdemodarkmode` for the `stale_flag` value and `true` for the `treated_as` value.
10. Observe in the pipeline that we run the flag cleanup tool, print out the git diffs, then commit and push them to git before finally opening a pr on github for those changes

